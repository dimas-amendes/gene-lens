#!/usr/bin/env python3
"""
Dashboard web local para analise genetica.
127.0.0.1 apenas. ECharts + Tabler locais. Zero CDN.
"""
import json
import sys
import time
import traceback
import os
import shutil
import threading
import uuid
from pathlib import Path
from collections import Counter
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

from config import DATA_DIR, INPUT_DIR, OUTPUT_DIR
from src.privacy import NetworkBlocker, ensure_directories
from src.parsers import load_genome
from src.databases import load_clinvar, load_pharmgkb
from src.analyzer import analyze_lifestyle, analyze_disease_risk
from src.reports import (
    _build_supplement_list, _build_diet_recs,
    _build_exercise_recs, _build_monitoring,
)
from src.translations import translate_traits, get_gene_context, GENE_CONTEXT
from src.translator import get_translator, translate_medical
from src.i18n import get_strings
from src.wellness_panels import analyze_all_panels, ALL_PANELS, SCORE_COLORS, SCORE_LABELS
from src.ancestry import analyze_ancestry, POP_LABELS, POP_COLORS, POP_COUNTRIES
from src.family_planning import analyze_family_planning
from src.phenotype import analyze_phenotype
from src.consent import require_consent_web, TERMS_TEXT
from src.hereditary_conditions import analyze_hereditary_conditions

import secrets
import threading

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 80 * 1024 * 1024

# Thread locks for shared state
_db_lock = threading.Lock()
_jobs_lock = threading.Lock()

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'"
    return response


@app.before_request
def _csrf_check():
    """Block cross-origin POST requests (CSRF protection without Flask-WTF).
    Allows all localhost variants and requests with no Origin/Referer."""
    if request.method == "POST":
        origin = request.headers.get("Origin") or ""
        referer = request.headers.get("Referer") or ""
        port = request.host.split(":")[-1] if ":" in request.host else "5000"
        allowed = (
            f"http://127.0.0.1:{port}",
            f"http://localhost:{port}",
            f"http://[::1]:{port}",
            "http://127.0.0.1",
            "http://localhost",
        )
        if origin and origin != "null" and not any(origin.startswith(a) for a in allowed):
            _log(f"CSRF blocked: Origin={origin}")
            return "Forbidden: cross-origin POST blocked", 403
        if not origin and referer and not any(referer.startswith(a) for a in allowed):
            _log(f"CSRF blocked: Referer={referer}")
            return "Forbidden: cross-origin POST blocked", 403

LOG_PATH = Path(__file__).parent / "dashboard.log"
HISTORY_DIR = Path(__file__).parent / "history"

def _log(msg):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as lf:
            lf.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
    except Exception:
        pass


# ── DB Cache ──────────────────────────────────────────────────────────────────

# `status` is updated as each DB loads so the UI can show sub-progress on the
# loading page. Started/finished are unix timestamps; current is a short slug
# the frontend maps to a translated label.
_db_cache = {
    "clinvar": None,
    "pharmgkb": None,
    "loaded": False,
    "status": {"current": "idle", "started_at": None, "finished_at": None, "error": None},
}

def _ensure_dbs():
    if _db_cache["loaded"]:
        return
    with _db_lock:
        if _db_cache["loaded"]:  # double-check after acquiring lock
            return
        _db_cache["status"]["started_at"] = time.time()
        _db_cache["status"]["error"] = None
        try:
            ensure_directories()
            _db_cache["status"]["current"] = "clinvar"
            _log("Carregando ClinVar (289 MB) — pode levar 30-90s na primeira vez...")
            _db_cache["clinvar"] = load_clinvar()
            _log(f"ClinVar OK: {len(_db_cache['clinvar']):,} posicoes")
            _db_cache["status"]["current"] = "pharmgkb"
            _log("Carregando PharmGKB...")
            _db_cache["pharmgkb"] = load_pharmgkb()
            _log(f"PharmGKB OK: {len(_db_cache['pharmgkb']):,} interacoes")
            _db_cache["loaded"] = True
            _db_cache["status"]["current"] = "ready"
            _db_cache["status"]["finished_at"] = time.time()
        except Exception as e:
            _log(f"ERRO DBs: {e}\n{traceback.format_exc()}")
            _db_cache["status"]["current"] = "error"
            _db_cache["status"]["error"] = str(e)
            # Don't mark as loaded so it retries next time
            if _db_cache["clinvar"] is None:
                _db_cache["clinvar"] = {}
            if _db_cache["pharmgkb"] is None:
                _db_cache["pharmgkb"] = {}


def _preload_dbs_async():
    """Kick off DB loading right after the server is up so the user never
    waits on the first analysis. Safe to call multiple times — _ensure_dbs
    is idempotent and protected by _db_lock."""
    threading.Thread(target=_ensure_dbs, daemon=True, name="db-preloader").start()


# ── Job system (async analysis with progress) ────────────────────────────────

_jobs = {}  # job_id -> {status, progress, result, error}

def _run_analysis(job_id: str, filepath: Path, subject_name: str, profile: dict = None, lang: str = "en"):
    """Run analysis in background thread."""
    job = _jobs[job_id]
    _tr = get_strings(lang)
    _analyzing_label = "Analyzing" if lang == "en" else "Analisando"
    _no_snps = "No SNPs loaded." if lang == "en" else "Nenhum SNP carregado."
    try:
        t0_total = time.time()
        job["progress"] = _tr["loading_step_db"] + "..."
        job["step"] = 0
        _log(f"[JOB {job_id[:8]}] Carregando DBs")
        _ensure_dbs()

        job["progress"] = _tr["loading_step_read"] + "..."
        job["step"] = 1
        _log(f"[JOB {job_id[:8]}] Lendo genoma")
        genome_by_rsid, genome_by_position, fmt = load_genome(filepath)
        _log(f"[JOB {job_id[:8]}] Formato: {fmt}, SNPs: {len(genome_by_rsid):,}")

        if len(genome_by_rsid) == 0:
            job["status"] = "error"
            job["error"] = f"{_no_snps} Format: {fmt}" if lang == "en" else f"{_no_snps} Formato: {fmt}"
            return

        # Infer biological sex if not provided in profile
        if not profile:
            profile = {}
        if not profile.get("sex"):
            from src.sex_inference import infer_sex
            inferred = infer_sex(genome_by_rsid)
            if inferred:
                profile["sex"] = inferred
                profile["sex_inferred"] = True
                _log(f"[JOB {job_id[:8]}] Sexo inferido: {inferred}")

        job["progress"] = f"{_analyzing_label} {len(genome_by_rsid):,} SNPs..."
        job["step"] = 2
        _log(f"[JOB {job_id[:8]}] Analisando")

        # === ALL ANALYSIS INSIDE NETWORK BLOCKER ===
        # Ensures zero data leakage during processing of genetic data
        with NetworkBlocker():
            health_results = analyze_lifestyle(genome_by_rsid, _db_cache["pharmgkb"])
            disease_findings, disease_stats = analyze_disease_risk(
                genome_by_position, _db_cache["clinvar"]
            )

            # Protocol (still part of variant analysis phase)
            findings_dict = {f["gene"]: f for f in health_results["findings"]}
            protocol_data = {
                "supplements": _build_supplement_list(findings_dict, lang),
                "diet": _build_diet_recs(findings_dict, lang),
                "exercise": _build_exercise_recs(findings_dict, lang),
                "monitoring": _build_monitoring(findings_dict, disease_findings, lang),
            }
            affected, carriers = [], []
            if disease_findings:
                for item in disease_findings.get("pathogenic", []) + disease_findings.get("likely_pathogenic", []):
                    if item.get("zygosity_status") == "AFFECTED":
                        affected.append(item)
                    elif item.get("zygosity_status") == "CARRIER":
                        carriers.append(item)
            protocol_data["affected"] = affected
            protocol_data["carriers"] = carriers

            charts_json = build_charts_json(health_results, disease_findings, lang=lang)
            conclusions = build_conclusions(health_results, disease_findings, protocol_data, lang=lang)

            # Wellness panels (needed before human conclusions)
            job["progress"] = _tr["loading_step_wellness"] + "..."
            job["step"] = 3
            _log(f"[JOB {job_id[:8]}] Paineis de bem-estar")
            wellness = analyze_all_panels(genome_by_rsid, lang=lang)

            # Family planning + phenotype
            family = analyze_family_planning(disease_findings, health_results, lang=lang)
            family["phenotype"] = analyze_phenotype(genome_by_rsid, lang=lang)

            # Hereditary conditions (sex-aware)
            hereditary = analyze_hereditary_conditions(disease_findings, profile, lang=lang)
            _log(f"[JOB {job_id[:8]}] Condicoes hereditarias: {len(hereditary['conditions'])} detectadas (sexo={hereditary['sex']})")

            # Coverage report (how many key markers does this chip actually carry?)
            from src.coverage import compute_coverage
            coverage = compute_coverage(genome_by_rsid)
            _log(
                f"[JOB {job_id[:8]}] Cobertura: "
                f"{coverage['summary']['markers_present']}/{coverage['summary']['markers_total']} marcadores "
                f"(alta={coverage['summary']['panels_high']}, parcial={coverage['summary']['panels_partial']}, baixa={coverage['summary']['panels_low']})"
            )

            # Composite Risk Index (transparent risk-allele tally per condition;
            # NOT a calibrated PRS — see src/prs.py for the rationale).
            from src.prs import compute_prs
            prs = compute_prs(genome_by_rsid)
            _log(
                f"[JOB {job_id[:8]}] CRI: "
                + ", ".join(f"{p['key']}={p['score']}/{p['max_score']}({p['band']})" for p in prs["panels"])
            )

            # Ancestry
            job["progress"] = ("Estimating ancestry..." if lang == "en" else "Estimando ancestralidade...")
            _log(f"[JOB {job_id[:8]}] Ancestralidade")
            ancestry = analyze_ancestry(genome_by_rsid, lang=lang)
            _log(f"[JOB {job_id[:8]}] Ancestralidade: {ancestry['percentages']} ({ancestry['markers_used']} marcadores)")

            # Translate INSIDE blocker — only meaningful for PT-BR, since
            # ClinVar/PharmGKB annotations are already in English. Running
            # the translator for an EN analysis is wasted work AND touches
            # argos's init path unnecessarily (which historically tried to
            # hit the network from inside the blocker).
            if lang == "pt":
                job["progress"] = _tr["loading_step_translate"] + "..."
                job["step"] = 4
                try:
                    translator = get_translator()
                    _log(f"[JOB {job_id[:8]}] Tradutor: neural={'sim' if translator.is_neural_available else 'nao'}")
                    for finding in health_results["pharmgkb_findings"]:
                        if finding.get("annotation"):
                            finding["annotation_original"] = finding["annotation"]
                            finding["annotation"] = translator.translate(finding["annotation"])
                    _log(f"[JOB {job_id[:8]}] Traducao OK: {len(health_results['pharmgkb_findings'])} anotacoes")
                except Exception as e:
                    _log(f"[JOB {job_id[:8]}] Traducao falhou (mantendo ingles): {e}")
            else:
                _log(f"[JOB {job_id[:8]}] Lang={lang}: pulando tradutor (anotacoes ja em ingles)")
                job["step"] = 4

        # === NETWORK BLOCKER RELEASED ===

        # Human-friendly conclusions for non-technical users
        job["progress"] = _tr["loading_step_conclude"] + "..."
        job["step"] = 5
        human = build_human_conclusions(
            health_results, disease_findings, protocol_data, wellness, family, ancestry,
            profile=profile, lang=lang,
        )

        filename = filepath.name
        result = {
            "health": health_results,
            "disease": disease_findings,
            "disease_stats": disease_stats,
            "genome_info": {
                "filename": filename,
                "format": fmt,
                "snp_count": len(genome_by_rsid),
                "subject_name": subject_name,
                "profile": profile or {},
            },
            "protocol_data": protocol_data,
            "charts_json": charts_json,
            "conclusions": conclusions,
            "human": human,
            "wellness": wellness,
            "ancestry": ancestry,
            "family": family,
            "hereditary": hereditary,
            "coverage": coverage,
            "prs": prs,
            "elapsed": round(time.time() - t0_total, 1),
        }

        # Save to history
        _save_history(result)

        # Clean up uploaded file (privacy: secure overwrite before deletion)
        try:
            from src.privacy import secure_delete
            if filepath.exists():
                secure_delete(filepath)
                _log(f"[JOB {job_id[:8]}] Upload limpo: {filepath.name}")
        except Exception:
            pass

        job["status"] = "done"
        job["result"] = result
        _log(f"[JOB {job_id[:8]}] Concluido")

    except Exception as e:
        _log(f"[JOB {job_id[:8]}] ERRO: {e}\n{traceback.format_exc()}")
        job["status"] = "error"
        job["error"] = str(e)


# ── History persistence ───────────────────────────────────────────────────────

def _save_history(result):
    """Save full analysis result to history for instant reload."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = result["genome_info"].get("subject_name") or "anonimo"
    safe_name = "".join(c for c in name if c.isalnum() or c in "-_")
    hid = f"{ts}_{safe_name}"

    # Save full result (for reload) + summary meta (for listing)
    full = {
        "id": hid,
        "timestamp": datetime.now().isoformat(),
        **result,
    }

    with open(HISTORY_DIR / f"{hid}.json", "w", encoding="utf-8") as f:
        json.dump(full, f, ensure_ascii=False, default=str)

    _log(f"Historico salvo: {hid} ({(HISTORY_DIR / f'{hid}.json').stat().st_size // 1024}KB)")


def _load_history_index():
    """Load history listing (just metadata, not full results)."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    entries = []
    for p in sorted(HISTORY_DIR.glob("*.json"), reverse=True):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            entries.append({
                "id": data.get("id", p.stem),
                "timestamp": data.get("timestamp", ""),
                "genome_info": data.get("genome_info", {}),
                "elapsed": data.get("elapsed", 0),
                "summary": data.get("health", {}).get("summary", data.get("summary", {})),
                "pharmgkb_count": len(data.get("health", {}).get("pharmgkb_findings", [])),
            })
        except Exception:
            pass
    return entries


def _sanitize_hid(hid: str) -> str:
    """Sanitize history ID to prevent path traversal."""
    # Only allow alphanumeric, underscore, hyphen
    return "".join(c for c in hid if c.isalnum() or c in "-_")


def _load_history_full(hid: str) -> dict | None:
    """Load full analysis result from history."""
    hid = _sanitize_hid(hid)
    if not hid:
        return None
    p = HISTORY_DIR / f"{hid}.json"
    # Ensure resolved path is inside HISTORY_DIR (defense in depth)
    if not str(p.resolve()).startswith(str(HISTORY_DIR.resolve())):
        return None
    if not p.exists():
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _delete_history(hid: str):
    """Delete a history entry."""
    hid = _sanitize_hid(hid)
    if not hid:
        return
    p = HISTORY_DIR / f"{hid}.json"
    if not str(p.resolve()).startswith(str(HISTORY_DIR.resolve())):
        return
    if p.exists():
        from src.privacy import secure_delete
        secure_delete(p)


# ── Chart builder ─────────────────────────────────────────────────────────────

def build_charts_json(health, disease, lang="en"):
    charts = {}
    cat_counts = {cat: len(f) for cat, f in health["by_category"].items()}
    if cat_counts:
        cats = sorted(cat_counts.items(), key=lambda x: -x[1])
        charts["categories"] = {"labels": [c[0] for c in cats], "values": [c[1] for c in cats]}

    if lang == "pt":
        mag = {"Baixo (0-1)": 0, "Moderado (2)": 0, "Alto (3+)": 0}
    else:
        mag = {"Low (0-1)": 0, "Moderate (2)": 0, "High (3+)": 0}
    for f in health["findings"]:
        m = f["magnitude"]
        keys = list(mag.keys())
        if m >= 3: mag[keys[2]] += 1
        elif m >= 2: mag[keys[1]] += 1
        else: mag[keys[0]] += 1
    charts["magnitude"] = [{"name": k, "value": v} for k, v in mag.items() if v > 0]

    levels = Counter(f["level"] for f in health["pharmgkb_findings"])
    if levels:
        charts["drug_levels"] = {"labels": list(levels.keys()), "values": list(levels.values())}

    if disease:
        if lang == "pt":
            charts["disease"] = [d for d in [
                {"name": "Patogenica", "value": len(disease.get("pathogenic", []))},
                {"name": "Prov. Patogenica", "value": len(disease.get("likely_pathogenic", []))},
                {"name": "Fator de Risco", "value": len(disease.get("risk_factor", []))},
                {"name": "Resp. Medicamento", "value": len(disease.get("drug_response", []))},
                {"name": "Protetora", "value": len(disease.get("protective", []))},
            ] if d["value"] > 0]
        else:
            charts["disease"] = [d for d in [
                {"name": "Pathogenic", "value": len(disease.get("pathogenic", []))},
                {"name": "Likely Pathogenic", "value": len(disease.get("likely_pathogenic", []))},
                {"name": "Risk Factor", "value": len(disease.get("risk_factor", []))},
                {"name": "Drug Response", "value": len(disease.get("drug_response", []))},
                {"name": "Protective", "value": len(disease.get("protective", []))},
            ] if d["value"] > 0]

    return json.dumps(charts, ensure_ascii=False)


# ── Conclusions ───────────────────────────────────────────────────────────────

def _get_drug_gene_note(gene: str, genotype: str) -> str:
    """Return clinical interpretation for pharmacogenes."""
    notes = {
        "CYP2D6": {
            "_default": "CYP2D6 metaboliza ~25% de todos os medicamentos, incluindo codeina, tramadol, tamoxifeno e muitos antidepressivos.",
            "poor": "Metabolizador lento — codeina sera ineficaz (nao converte em morfina), tramadol reduzido. Risco de efeitos adversos com doses padrao de antidepressivos.",
            "intermediate": "Metabolizador intermediario — pode precisar de ajuste de dose para opioides e antidepressivos.",
        },
        "CYP2C19": {
            "_default": "CYP2C19 metaboliza clopidogrel (anticoagulante), inibidores de bomba de protons (omeprazol) e alguns antidepressivos.",
            "poor": "Metabolizador lento — clopidogrel sera INEFICAZ (nao converte na forma ativa). Considerar anticoagulante alternativo (prasugrel, ticagrelor).",
            "intermediate": "Metabolizador intermediario — clopidogrel pode ter eficacia reduzida. Discutir alternativas com cardiologista.",
            "rapid": "Metabolizador rapido — pode precisar de doses maiores de omeprazol/PPIs. Antidepressivos metabolizados mais rapido.",
            "ultrarapid": "Metabolizador ultrarapido — doses padrao de PPIs e antidepressivos podem ser insuficientes.",
        },
        "CYP2C9": {
            "_default": "CYP2C9 metaboliza warfarina (anticoagulante) e AINEs (ibuprofeno, naproxeno).",
            "poor": "Metabolizador lento — warfarina requer reducao significativa de dose (risco de sangramento). AINEs podem acumular.",
            "intermediate": "Metabolizador intermediario — warfarina requer reducao moderada de dose.",
        },
        "VKORC1": {
            "_default": "VKORC1 e o alvo da warfarina. Variantes afetam diretamente a sensibilidade.",
            "sensitive": "Sensibilidade aumentada — doses de warfarina significativamente menores necessarias.",
            "highly_sensitive": "Altamente sensivel — doses de warfarina muito reduzidas. Risco elevado de sangramento com dose padrao.",
        },
        "DPYD": {
            "_default": "DPYD metaboliza fluoropirimidinas (5-FU, capecitabina) usadas em quimioterapia.",
            "intermediate": "DPYD reduzido — dose de 5-FU/capecitabina deve ser reduzida em 50%. Toxicidade grave se dose padrao.",
            "deficient": "DPYD deficiente — 5-FU e capecitabina sao CONTRAINDICADOS. Pode ser fatal com dose padrao.",
        },
        "TPMT": {
            "_default": "TPMT metaboliza tiopurinas (azatioprina, 6-mercaptopurina) usadas em autoimunes e leucemia.",
            "intermediate": "TPMT intermediario — reducao de dose de tiopurinas necessaria para evitar mielossupressao.",
            "poor": "TPMT deficiente — tiopurinas podem causar mielossupressao grave. Dose drasticamente reduzida ou alternativa.",
        },
        "SLCO1B1": {
            "_default": "SLCO1B1 transporta estatinas para o figado. Variantes afetam risco de miopatia.",
            "intermediate": "Transportador intermediario — 4x maior risco de miopatia com sinvastatina. Considerar rosuvastatina ou pravastatina.",
            "poor": "Transportador deficiente — 17x maior risco de miopatia com sinvastatina. EVITAR sinvastatina. Usar alternativas.",
        },
        "CYP3A5": {
            "_default": "CYP3A5 afeta metabolismo de tacrolimus (imunossupressor pos-transplante).",
        },
        "HLA-B": {
            "_default": "HLA-B*5701 — abacavir (antirretroviral para HIV) e contraindicado em portadores por risco de hipersensibilidade grave.",
        },
        "CYP1A2": {
            "_default": "CYP1A2 metaboliza cafeina, teofilina e alguns antipsicoticos (clozapina).",
        },
    }

    gene_info = notes.get(gene)
    if not gene_info:
        return ""

    # Try to match status from snp_database
    from src.snp_database import CURATED_SNPS
    status = None
    for rsid, info in CURATED_SNPS.items():
        if info["gene"] == gene:
            variant = info["variants"].get(genotype)
            if not variant and len(genotype) == 2:
                variant = info["variants"].get(genotype[::-1])
            if variant:
                status = variant.get("status")
                break

    if status and status in gene_info:
        return gene_info[status]
    return gene_info.get("_default", "")


_TC = {
    "pt": {
        "overview_high": "Foram identificados {n} achado(s) de alta magnitude que merecem atencao: {genes}. Estes sinais sao preliminares e requerem confirmacao clinica.",
        "overview_none": "Nenhum achado de alta magnitude foi detectado. Isso e um sinal positivo, mas nao exclui riscos nao cobertos por este painel.",
        "overview_drugs": "Ha {n} interacao(oes) droga-gene com diretrizes clinicas (CPIC Nivel 1). Medicamentos envolvidos incluem: {drugs}. Compartilhe com seu medico prescritor.",
        "lifestyle_mthfr": "Variante MTHFR detectada — a capacidade de converter acido folico em metilfolato esta reduzida. Discuta com seu medico a possibilidade de suplementacao com metilfolato.",
        "lifestyle_comt": "COMT lento (Met/Met) — dopamina e norepinefrina permanecem ativas por mais tempo. Voce pode ter melhor foco em condicoes calmas, mas mais sensibilidade ao estresse.",
        "lifestyle_cyp1a2": "Metabolismo de cafeina reduzido — a cafeina permanece no organismo por mais tempo. Considere limitar o consumo ao periodo da manha.",
        "lifestyle_bp": "Multiplas variantes cardiovasculares detectadas ({genes}) — monitoramento regular de pressao arterial e recomendado.",
        "lifestyle_gc": "Predisposicao genetica a niveis mais baixos de vitamina D — discuta dosagem de D3 e monitore 25-OH vitamina D.",
        "disease_patho": "{n} variante(s) patogenica(s) com evidencia (1+ estrelas). Dados de consumo tem ~40% de falso positivo — confirme com sequenciamento clinico.",
        "disease_carrier": "{n} status de portador ({genes}). Portadores nao apresentam sintomas, mas ha implicacoes reprodutivas.",
        "disease_risk": "{n} fator(es) de risco com evidencia (2+ estrelas). Indicam suscetibilidade aumentada, nao certeza de doenca.",
        "disease_low_conf": "Nota tecnica: {n} variante(s) com 0/4 estrelas (sem criterios de afirmacao) foram detectadas mas nao geram conclusoes por falta de evidencia. Genes: {genes}. Consulte as tabelas de dados para detalhes completos.",
        "disease_low_risk": "{n} fator(es) de risco de baixa confianca omitidos das conclusoes.",
        "drugs_l1_intro": "{n} interacao(oes) com diretrizes CPIC Nivel 1A/1B — estas tem guias de dosagem publicados baseados em multiplos estudos clinicos. Leve esta lista ao medico OBRIGATORIAMENTE. Se algum dia precisar desses medicamentos, o medico precisa saber do seu genotipo.",
        "drugs_l2": "{n} interacao(oes) com evidencia moderada (Nivel 2A/2B) — associacao gene-droga documentada na literatura, mas sem diretriz formal de dosagem. Vale mencionar na consulta.",
        "drugs_important": "IMPORTANTE: Os niveis refletem a qualidade da evidencia cientifica da interacao gene-droga, NAO a gravidade do efeito. Um nivel 2B pode ter consequencia grave — so tem menos estudos confirmando. NAO ajuste medicamentos por conta propria.",
        "protocol_supps": "{n} topico(s) de suplementacao identificado(s). Discuta com seu medico antes de iniciar.",
        "protocol_tests": "Exames sugeridos: {tests}. Seu medico decidira quais sao apropriados.",
        "protocol_urgent": "Ha variantes patogenicas que requerem confirmacao clinica URGENTE.",
    },
    "en": {
        "overview_high": "{n} high-magnitude finding(s) identified that deserve attention: {genes}. These are preliminary signals and require clinical confirmation.",
        "overview_none": "No high-magnitude findings detected. This is a positive sign, but does not exclude risks not covered by this panel.",
        "overview_drugs": "There are {n} drug-gene interaction(s) with clinical guidelines (CPIC Level 1). Medications involved include: {drugs}. Share with your prescribing physician.",
        "lifestyle_mthfr": "MTHFR variant detected — the ability to convert folic acid to methylfolate is reduced. Discuss with your doctor the possibility of methylfolate supplementation.",
        "lifestyle_comt": "Slow COMT (Met/Met) — dopamine and norepinephrine remain active longer. You may have better focus in calm conditions, but more sensitivity to stress.",
        "lifestyle_cyp1a2": "Reduced caffeine metabolism — caffeine stays in your system longer. Consider limiting intake to the morning.",
        "lifestyle_bp": "Multiple cardiovascular variants detected ({genes}) — regular blood pressure monitoring is recommended.",
        "lifestyle_gc": "Genetic predisposition to lower vitamin D levels — discuss D3 dosing and monitor 25-OH vitamin D.",
        "disease_patho": "{n} pathogenic variant(s) with evidence (1+ stars). Consumer data has ~40% false positive rate — confirm with clinical sequencing.",
        "disease_carrier": "{n} carrier status ({genes}). Carriers do not show symptoms, but there are reproductive implications.",
        "disease_risk": "{n} risk factor(s) with evidence (2+ stars). Indicate increased susceptibility, not certainty of disease.",
        "disease_low_conf": "Technical note: {n} variant(s) with 0/4 stars (no assertion criteria) were detected but do not generate conclusions due to lack of evidence. Genes: {genes}. See data tables for full details.",
        "disease_low_risk": "{n} low-confidence risk factor(s) omitted from conclusions.",
        "drugs_l1_intro": "{n} interaction(s) with CPIC Level 1A/1B guidelines — these have published dosing guides based on multiple clinical studies. Bring this list to your physician. If you ever need these medications, your doctor needs to know your genotype.",
        "drugs_l2": "{n} interaction(s) with moderate evidence (Level 2A/2B) — documented gene-drug association in the literature, but no formal dosing guideline. Worth mentioning at your appointment.",
        "drugs_important": "IMPORTANT: Levels reflect the quality of scientific evidence for the gene-drug interaction, NOT the severity of the effect. A level 2B can have serious consequences — it just has fewer confirming studies. Do NOT adjust medications on your own.",
        "protocol_supps": "{n} supplementation topic(s) identified. Discuss with your physician before starting.",
        "protocol_tests": "Suggested tests: {tests}. Your physician will decide which are appropriate.",
        "protocol_urgent": "There are pathogenic variants that require URGENT clinical confirmation.",
    },
}


def build_conclusions(health, disease, protocol, lang="en"):
    c = {}
    t = _TC.get(lang, _TC["en"])

    # Overview
    overview = []
    high = [f for f in health["findings"] if f["magnitude"] >= 3]
    if high:
        genes = ", ".join(f["gene"] for f in high)
        overview.append(t["overview_high"].format(n=len(high), genes=genes))
    else:
        overview.append(t["overview_none"])
    if health["pharmgkb_findings"]:
        l1 = [f for f in health["pharmgkb_findings"] if f["level"] in ("1A", "1B")]
        if l1:
            drugs = set()
            for f in l1:
                drugs.update(d.strip() for d in f["drugs"].split(";")[:3])
            overview.append(t["overview_drugs"].format(n=len(l1), drugs=", ".join(list(drugs)[:5])))
    c["overview"] = overview

    # Lifestyle
    lifestyle = []
    fd = {f["gene"]: f for f in health["findings"]}
    if "MTHFR" in fd and fd["MTHFR"]["magnitude"] >= 2:
        lifestyle.append(t["lifestyle_mthfr"])
    if "COMT" in fd and fd["COMT"].get("status") == "slow":
        lifestyle.append(t["lifestyle_comt"])
    if "CYP1A2" in fd and fd["CYP1A2"].get("status") in ("slow", "intermediate"):
        lifestyle.append(t["lifestyle_cyp1a2"])
    apoe = health.get("apoe")
    if apoe:
        lifestyle.append(f"**APOE {apoe['isoform']}** (rs429358={apoe['rs429358']}, rs7412={apoe['rs7412']}): {apoe['description']}")
    bp_genes = [g for g in ("AGTR1", "ACE", "AGT", "GNB3") if g in fd]
    if len(bp_genes) >= 2:
        lifestyle.append(t["lifestyle_bp"].format(genes=", ".join(bp_genes)))
    if "GC" in fd and fd["GC"].get("status") in ("low", "very_low"):
        lifestyle.append(t["lifestyle_gc"])
    c["lifestyle"] = lifestyle

    # Disease
    disease_conc = []
    disease_technical = []
    stars_label = "estrelas" if lang == "pt" else "stars"
    action_label = "**Acao recomendada:**" if lang == "pt" else "**Recommended action:**"
    if disease:
        patho = disease.get("pathogenic", []) + disease.get("likely_pathogenic", [])
        high_conf = [f for f in patho if f.get("gold_stars", 0) >= 1]
        low_conf = [f for f in patho if f.get("gold_stars", 0) == 0]

        if high_conf:
            affected_hc = [f for f in high_conf if f.get("zygosity_status") == "AFFECTED"]
            carriers_hc = [f for f in high_conf if f.get("zygosity_status") == "CARRIER"]
            het_hc = [f for f in high_conf if f.get("zygosity_status") not in ("AFFECTED", "CARRIER")]

            total_hc = len(affected_hc) + len(het_hc)
            if total_hc:
                disease_conc.append(t["disease_patho"].format(n=total_hc))

            genes_seen = set()
            for f in sorted(high_conf, key=lambda x: -x.get("gold_stars", 0)):
                gene = f.get("gene", "")
                if not gene or gene in genes_seen:
                    continue
                genes_seen.add(gene)
                stars = f.get("gold_stars", 0)
                ctx = get_gene_context(gene)
                if ctx:
                    traits_pt = translate_traits(f.get("traits", ""))
                    note = ctx.get("note", "")
                    action = ctx.get("action", "")
                    confidence = f"({stars}/4 {stars_label})"
                    line = f"**{gene}** {confidence} — {traits_pt}: {note}"
                    if action:
                        line += f" {action_label} {action}"
                    disease_conc.append(line)

            if carriers_hc:
                carrier_genes = ", ".join(set(f.get("gene", "?") for f in carriers_hc))
                disease_conc.append(t["disease_carrier"].format(n=len(carriers_hc), genes=carrier_genes))

        apoe_findings = [f for f in patho if f.get("gene") == "APOE"]
        if apoe_findings and "APOE" not in {f.get("gene") for f in high_conf}:
            ctx = get_gene_context("APOE")
            if ctx:
                disease_conc.append(f"**APOE**: {ctx['note']}")

        if low_conf:
            low_genes = [f.get("gene", "?") for f in low_conf if f.get("gene")]
            unique_low = list(set(g for g in low_genes if g))[:10]
            genes_str = ", ".join(unique_low) if unique_low else "N/A"
            disease_technical.append(t["disease_low_conf"].format(n=len(low_conf), genes=genes_str))

        risk = disease.get("risk_factor", [])
        if risk:
            high_risk = [f for f in risk if f.get("gold_stars", 0) >= 2]
            if high_risk:
                disease_conc.append(t["disease_risk"].format(n=len(high_risk)))
            if len(risk) > len(high_risk):
                disease_technical.append(t["disease_low_risk"].format(n=len(risk) - len(high_risk)))

    c["disease"] = disease_conc
    c["disease_technical"] = disease_technical

    # Drugs — with per-gene clinical context
    drugs_conc = []
    if health["pharmgkb_findings"]:
        l1 = [f for f in health["pharmgkb_findings"] if f["level"] in ("1A", "1B")]
        l2 = [f for f in health["pharmgkb_findings"] if f["level"] in ("2A", "2B")]

        if l1:
            l1_by_gene = {}
            for f in l1:
                gene = f.get("gene", "?")
                if gene not in l1_by_gene:
                    l1_by_gene[gene] = []
                l1_by_gene[gene].append(f)

            drugs_conc.append(t["drugs_l1_intro"].format(n=len(l1)))

            genotype_label = "genotipo" if lang == "pt" else "genotype"
            level_label = "nivel" if lang == "pt" else "level"
            meds_label = "medicamentos" if lang == "pt" else "medications"
            for gene, findings in l1_by_gene.items():
                drugs_list = set()
                for f in findings:
                    drugs_list.update(d.strip() for d in f["drugs"].split(";") if d.strip())
                drugs_str = ", ".join(sorted(drugs_list)[:5])
                genotype = findings[0].get("genotype", "?")
                level = findings[0].get("level", "?")
                gene_note = _get_drug_gene_note(gene, genotype)
                if gene_note:
                    drugs_conc.append(f"**{gene}** ({genotype_label} `{genotype}`, {level_label} {level}) — {meds_label}: {drugs_str}. {gene_note}")
                else:
                    drugs_conc.append(f"**{gene}** ({genotype_label} `{genotype}`, {level_label} {level}) — {meds_label}: {drugs_str}.")

        if l2:
            drugs_conc.append(t["drugs_l2"].format(n=len(l2)))

        drugs_conc.append(t["drugs_important"])
    c["drugs"] = drugs_conc

    # Protocol
    protocol_conc = []
    if protocol:
        if protocol.get("supplements"):
            protocol_conc.append(t["protocol_supps"].format(n=len(protocol["supplements"])))
        if protocol.get("monitoring"):
            tests = [m["test"] for m in protocol["monitoring"]]
            protocol_conc.append(t["protocol_tests"].format(tests=", ".join(tests)))
        if protocol.get("affected"):
            protocol_conc.append(t["protocol_urgent"])
    c["protocol"] = protocol_conc

    return c


# ── Bilingual text for human conclusions and profile notes ─────────────────────

_HC = {
    "pt": {
        # Profile notes
        "female_autoimmune": "**Perfil feminino:** Doencas autoimunes (tireoide, celiaca) sao significativamente mais comuns em mulheres. Atencao especial aos paineis de tireoide e sensibilidades alimentares.",
        "female_fertile": "**Idade fertil:** Os riscos gestacionais na aba Heranca sao particularmente relevantes para voce. Consulte seu obstetra sobre seu perfil genetico antes de planejar gravidez.",
        "female_hfe": "**Ferro (HFE):** Mulheres pre-menopausa sao parcialmente protegidas do acumulo de ferro pela menstruacao. Monitorar ferritina e mais critico apos a menopausa.",
        "female_menopause": "**Pos-menopausa:** O painel de saude ossea e especialmente relevante. A perda de estrogeno acelera a perda ossea em mulheres com variantes de risco.",
        "male_profile": "**Perfil masculino:** O painel de calvicie androgenica e particularmente relevante. Condicoes X-linked (G6PD, daltonismo) afetam homens com maior frequencia e severidade.",
        "male_hfe": "**Ferro (HFE):** Homens acumulam ferro mais cedo que mulheres (sem perda menstrual). Monitorar ferritina e mais urgente.",
        "age_eye": "**Idade {age}:** Exames oftalmologicos anuais sao recomendados, especialmente se ha variantes de risco para DMRI ou glaucoma.",
        "age_screening": "**Rastreamento:** A partir dos 50 anos, colonoscopia e densitometria ossea devem ser discutidas com seu medico, especialmente com variantes de risco.",
        "bmi_obese": "**IMC {bmi} (obesidade):** Variantes de risco para diabetes (TCF7L2) e cardiovascular (AGT, AGTR1) tem impacto amplificado. Controle de peso e a intervencao mais eficaz.",
        "bmi_overweight": "**IMC {bmi} (sobrepeso):** Variantes metabolicas (APOA2, GNB3, TCF7L2) merecem atencao extra. Atividade fisica regular e alimentacao equilibrada sao especialmente importantes.",
        # Human conclusions
        "overview_clean": "Analisamos {analyzed:,} marcadores do seu DNA e nao encontramos nenhum achado de alta importancia. Isso e um bom sinal, mas nao significa ausencia total de riscos — este teste cobre apenas uma fracao do genoma.",
        "overview_findings": "Analisamos {analyzed:,} marcadores do seu DNA e encontramos {high} achado(s) que merecem atencao. Isso NAO e um diagnostico — significa que vale a pena conversar com seu medico sobre esses pontos.",
        "overview_drugs": "Seu corpo pode processar {count} medicamento(s) de forma diferente da maioria das pessoas. Se voce algum dia precisar tomar esses remedios, seu medico precisa saber disso para ajustar a dose.",
        "health_points_intro": "Seu DNA indica que voce pode ter particularidades em como seu corpo lida com: ",
        "health_no_findings": "Nao encontramos particularidades significativas no seu metabolismo. Isso e um bom sinal, mas mantenha habitos saudaveis e exames de rotina.",
        "health_disease_found": "Encontramos {count} variante(s) genetica(s) que podem estar associadas a condicoes de saude. IMPORTANTE: testes de consumo como este tem alta taxa de erro (~40%). Nao se preocupe excessivamente — mas leve esses resultados ao seu medico para ele decidir se vale fazer um teste de confirmacao.",
        "health_no_disease": "Nao foram encontradas variantes geneticas preocupantes nas bases de dados medicas. Isso e positivo, mas lembre-se que este teste cobre apenas uma fracao das condicoes conhecidas.",
        "health_carrier": "Voce e portador(a) de {count} condicao(oes) — isso significa que voce NAO tem a doenca, mas pode passar o gene para seus filhos. Isso so e relevante se voce planeja ter filhos e e detalhado na aba Heranca.",
        "drugs_found": "Seu DNA mostra que voce processa {count} medicamento(s) de forma diferente. Isso nao significa que voce nao pode toma-los — significa que seu medico pode precisar ajustar a dose ou escolher um alternativo.",
        "drugs_list": "Medicamentos que podem ser afetados: {drugs}. Imprima esta pagina e leve na proxima consulta medica.",
        "drugs_warning": "NUNCA altere ou pare um medicamento por conta propria baseado neste resultado. Apenas seu medico pode fazer esse julgamento.",
        "drugs_some": "Foram encontradas algumas interacoes gene-medicamento, mas nenhuma com evidencia maxima. Mesmo assim, e bom mencionar ao seu medico na proxima consulta.",
        "drugs_none": "Nenhuma interacao gene-medicamento significativa foi detectada. Seu corpo parece processar os medicamentos mais comuns de forma padrao.",
        "wellness_summary": "De {total} marcadores de bem-estar analisados, {pct}% estao dentro do esperado. Isso significa que, geneticamente, voce tem uma boa base para a maioria dos aspectos do dia a dia.",
        "wellness_panel_alert": "**{label}:** Pontos que merecem atencao: {tips}. Veja os detalhes no accordion abaixo.",
        "wellness_ok": "Seus marcadores de bem-estar estao em boa forma. Mantenha uma dieta equilibrada, exercicio regular e sono adequado — seu DNA nao indica necessidades especiais.",
        "family_none": "Nenhuma variante com implicacao reprodutiva significativa foi encontrada. Isso e tranquilizador, mas se voce planeja ter filhos, um teste de portador expandido (disponivel em laboratorios especializados) cobre muitas mais condicoes.",
        "family_carrier": "Voce carrega {count} gene(s) que pode(m) causar doenca nos filhos SE seu parceiro(a) tambem carregar o mesmo gene. Isso e relativamente comum — cerca de 1 em cada 25 pessoas e portadora de alguma condicao recessiva. O mais importante e que seu parceiro(a) faca um teste genetico antes de engravidar.",
        "family_dominant": "Voce tem {count} variante(s) que pode(m) ser transmitida(s) diretamente aos seus filhos (50% de chance cada). Converse com um geneticista para entender o que isso significa na pratica.",
        "family_counselor": "Recomendamos consultar um conselheiro genetico antes de planejar gravidez. Eles podem explicar tudo em detalhes e orientar os proximos passos.",
        # Lifestyle point templates
        "lp_mthfr": "absorver acido folico (vitamina B9) — pode precisar de uma forma especial dessa vitamina",
        "lp_caffeine": "processar cafeina — o cafe demora mais para sair do seu corpo, evite tomar depois do almoco",
        "lp_comt": "lidar com estresse — voce pode ser mais sensivel a situacoes estressantes, mas tem melhor foco em ambientes calmos",
        "lp_apoe": "risco de Alzheimer — a variante APOE E4 esta associada a maior risco, exercicio fisico regular e dieta mediterranea podem ajudar",
        "lp_bp": "pressao arterial — voce tem predisposicao genetica, medir a pressao regularmente e importante",
        "lp_vitd": "niveis de vitamina D — seu corpo pode ter dificuldade em manter niveis adequados, converse com seu medico sobre suplementacao",
    },
    "en": {
        # Profile notes
        "female_autoimmune": "**Female profile:** Autoimmune diseases (thyroid, celiac) are significantly more common in women. Pay special attention to the thyroid and food sensitivities panels.",
        "female_fertile": "**Childbearing age:** The gestational risks in the Heritage tab are particularly relevant for you. Consult your OB/GYN about your genetic profile before planning pregnancy.",
        "female_hfe": "**Iron (HFE):** Premenopausal women are partially protected from iron accumulation by menstruation. Monitoring ferritin is more critical after menopause.",
        "female_menopause": "**Post-menopause:** The bone health panel is especially relevant. Estrogen loss accelerates bone loss in women with risk variants.",
        "male_profile": "**Male profile:** The androgenetic alopecia panel is particularly relevant. X-linked conditions (G6PD, color blindness) affect men with greater frequency and severity.",
        "male_hfe": "**Iron (HFE):** Men accumulate iron earlier than women (no menstrual loss). Monitoring ferritin is more urgent.",
        "age_eye": "**Age {age}:** Annual eye exams are recommended, especially if you have risk variants for AMD or glaucoma.",
        "age_screening": "**Screening:** From age 50, colonoscopy and bone density scans should be discussed with your physician, especially with risk variants.",
        "bmi_obese": "**BMI {bmi} (obese):** Risk variants for diabetes (TCF7L2) and cardiovascular (AGT, AGTR1) have amplified impact. Weight management is the most effective intervention.",
        "bmi_overweight": "**BMI {bmi} (overweight):** Metabolic variants (APOA2, GNB3, TCF7L2) deserve extra attention. Regular physical activity and balanced nutrition are especially important.",
        # Human conclusions
        "overview_clean": "We analyzed {analyzed:,} markers from your DNA and found no high-importance findings. This is a good sign, but does not mean the absence of all risks — this test covers only a fraction of the genome.",
        "overview_findings": "We analyzed {analyzed:,} markers from your DNA and found {high} finding(s) that deserve attention. This is NOT a diagnosis — it means it is worth discussing these points with your physician.",
        "overview_drugs": "Your body may process {count} medication(s) differently from most people. If you ever need to take these medications, your doctor needs to know this to adjust the dosage.",
        "health_points_intro": "Your DNA indicates you may have particularities in how your body handles: ",
        "health_no_findings": "We found no significant particularities in your metabolism. This is a good sign, but maintain healthy habits and routine check-ups.",
        "health_disease_found": "We found {count} genetic variant(s) that may be associated with health conditions. IMPORTANT: consumer tests like this have a high error rate (~40%). Do not worry excessively — but bring these results to your doctor to decide whether a confirmatory test is warranted.",
        "health_no_disease": "No concerning genetic variants were found in the medical databases. This is positive, but remember this test covers only a fraction of known conditions.",
        "health_carrier": "You are a carrier of {count} condition(s) — this means you do NOT have the disease, but may pass the gene to your children. This is only relevant if you plan to have children and is detailed in the Heritage tab.",
        "drugs_found": "Your DNA shows you process {count} medication(s) differently. This does not mean you cannot take them — it means your doctor may need to adjust the dose or choose an alternative.",
        "drugs_list": "Medications that may be affected: {drugs}. Print this page and bring it to your next medical appointment.",
        "drugs_warning": "NEVER change or stop a medication on your own based on this result. Only your physician can make that judgment.",
        "drugs_some": "Some gene-drug interactions were found, but none with the highest evidence level. Still, it is worth mentioning to your doctor at your next visit.",
        "drugs_none": "No significant gene-drug interactions were detected. Your body appears to process the most common medications in a standard way.",
        "wellness_summary": "Of {total} wellness markers analyzed, {pct}% are within the expected range. This means, genetically, you have a good baseline for most aspects of daily life.",
        "wellness_panel_alert": "**{label}:** Points that deserve attention: {tips}. See details in the accordion below.",
        "wellness_ok": "Your wellness markers are in good shape. Maintain a balanced diet, regular exercise, and adequate sleep — your DNA does not indicate special needs.",
        "family_none": "No variants with significant reproductive implications were found. This is reassuring, but if you plan to have children, an expanded carrier screening (available at specialized labs) covers many more conditions.",
        "family_carrier": "You carry {count} gene(s) that may cause disease in your children IF your partner also carries the same gene. This is relatively common — about 1 in 25 people carries some recessive condition. The most important step is for your partner to have a genetic test before conceiving.",
        "family_dominant": "You have {count} variant(s) that may be transmitted directly to your children (50% chance each). Talk to a geneticist to understand what this means in practice.",
        "family_counselor": "We recommend consulting a genetic counselor before planning pregnancy. They can explain everything in detail and guide the next steps.",
        # Lifestyle point templates
        "lp_mthfr": "absorbing folic acid (vitamin B9) — may need a special form of this vitamin",
        "lp_caffeine": "processing caffeine — coffee takes longer to leave your body, avoid drinking it after lunch",
        "lp_comt": "handling stress — you may be more sensitive to stressful situations, but have better focus in calm environments",
        "lp_apoe": "Alzheimer's risk — the APOE E4 variant is associated with higher risk, regular exercise and Mediterranean diet may help",
        "lp_bp": "blood pressure — you have a genetic predisposition, measuring blood pressure regularly is important",
        "lp_vitd": "vitamin D levels — your body may have difficulty maintaining adequate levels, discuss supplementation with your doctor",
    },
}


def _build_profile_notes(profile: dict, health: dict, disease: dict, lang: str = "en") -> list:
    """Generate contextual notes based on user profile (sex, age, weight)."""
    notes = []
    if not profile:
        return notes
    t = _HC.get(lang, _HC["en"])

    sex = profile.get("sex")
    age = profile.get("age")
    bmi = profile.get("bmi")

    fd = {f["gene"]: f for f in health.get("findings", [])}

    # Sex-specific notes
    if sex == "F":
        notes.append(t["female_autoimmune"])
        if age and 18 <= age <= 45:
            notes.append(t["female_fertile"])
        if "HFE" in fd:
            notes.append(t["female_hfe"])
        if age and age >= 45:
            notes.append(t["female_menopause"])
    elif sex == "M":
        notes.append(t["male_profile"])
        if "HFE" in fd:
            notes.append(t["male_hfe"])

    # Age-specific notes
    if age:
        if age >= 40:
            notes.append(t["age_eye"].format(age=age))
        if age >= 50:
            notes.append(t["age_screening"])

    # BMI notes
    if bmi:
        if bmi >= 30:
            notes.append(t["bmi_obese"].format(bmi=bmi))
        elif bmi >= 25:
            notes.append(t["bmi_overweight"].format(bmi=bmi))

    return notes


def build_human_conclusions(health, disease, protocol, wellness, family, ancestry, profile=None, lang="en"):
    """Build plain-language conclusions for non-technical users."""
    h = {}
    t = _HC.get(lang, _HC["en"])

    # ── Profile-based contextual notes ──
    h["profile_notes"] = _build_profile_notes(profile or {}, health, disease, lang=lang)

    # ── Overview ──
    overview = []
    analyzed = health["summary"]["analyzed_snps"]
    high = [f for f in health["findings"] if f["magnitude"] >= 3]

    if not high:
        overview.append(t["overview_clean"].format(analyzed=analyzed))
    else:
        overview.append(t["overview_findings"].format(analyzed=analyzed, high=len(high)))
    if health["pharmgkb_findings"]:
        l1 = [f for f in health["pharmgkb_findings"] if f["level"] in ("1A", "1B")]
        if l1:
            overview.append(t["overview_drugs"].format(count=len(l1)))
    h["overview"] = overview

    # ── Health & Risks ──
    health_h = []
    fd = {f["gene"]: f for f in health["findings"]}
    lifestyle_points = []
    if "MTHFR" in fd and fd["MTHFR"]["magnitude"] >= 2:
        lifestyle_points.append(t["lp_mthfr"])
    if "CYP1A2" in fd and fd["CYP1A2"].get("status") in ("slow", "intermediate"):
        lifestyle_points.append(t["lp_caffeine"])
    if "COMT" in fd and fd["COMT"].get("status") == "slow":
        lifestyle_points.append(t["lp_comt"])
    apoe = health.get("apoe")
    if apoe and "E4" in apoe["isoform"]:
        lifestyle_points.append(t["lp_apoe"])
    bp_genes = [g for g in ("AGTR1", "ACE", "AGT", "GNB3") if g in fd]
    if len(bp_genes) >= 2:
        lifestyle_points.append(t["lp_bp"])
    if "GC" in fd and fd["GC"].get("status") in ("low", "very_low"):
        lifestyle_points.append(t["lp_vitd"])

    if lifestyle_points:
        health_h.append(t["health_points_intro"] + "; ".join(lifestyle_points) + ".")
    else:
        health_h.append(t["health_no_findings"])

    if disease:
        patho = disease.get("pathogenic", []) + disease.get("likely_pathogenic", [])
        high_conf = [f for f in patho if f.get("gold_stars", 0) >= 1]
        carriers = [f for f in high_conf if f.get("zygosity_status") == "CARRIER"]
        affected = [f for f in high_conf if f.get("zygosity_status") != "CARRIER"]

        if affected:
            health_h.append(t["health_disease_found"].format(count=len(affected)))
        elif not patho:
            health_h.append(t["health_no_disease"])
        if carriers:
            health_h.append(t["health_carrier"].format(count=len(carriers)))
    h["health"] = health_h

    # ── Drugs ──
    drugs_h = []
    if health["pharmgkb_findings"]:
        l1 = [f for f in health["pharmgkb_findings"] if f["level"] in ("1A", "1B")]
        if l1:
            drug_names = set()
            for f in l1:
                drug_names.update(d.strip() for d in f["drugs"].split(";") if d.strip())
            drugs_h.append(t["drugs_found"].format(count=len(l1)))
            drugs_h.append(t["drugs_list"].format(drugs=", ".join(sorted(drug_names)[:8])))
            drugs_h.append(t["drugs_warning"])
        else:
            drugs_h.append(t["drugs_some"])
    else:
        drugs_h.append(t["drugs_none"])
    h["drugs"] = drugs_h

    # ── Wellness ──
    wellness_h = []
    if wellness:
        total_alerta = sum(p.get("summary", {}).get("alerta", 0) for p in wellness.values() if isinstance(p, dict))
        total_atencao = sum(p.get("summary", {}).get("atencao", 0) for p in wellness.values() if isinstance(p, dict))
        total_normal = sum(p.get("summary", {}).get("normal", 0) for p in wellness.values() if isinstance(p, dict))
        grand_total = total_alerta + total_atencao + total_normal

        if grand_total > 0:
            pct_ok = round(100 * total_normal / grand_total)
            wellness_h.append(t["wellness_summary"].format(total=grand_total, pct=pct_ok))

        panel_labels = {"nutri": "Nutrition", "fit": "Exercise", "skin": "Skin", "aging": "Aging"} if lang == "en" else {"nutri": "Nutricao", "fit": "Exercicio", "skin": "Pele", "aging": "Envelhecimento"}
        for pk, label in panel_labels.items():
            panel = wellness.get(pk, {})
            if not panel or not isinstance(panel, dict):
                continue
            findings = panel.get("findings", [])
            alertas = [f for f in findings if f.get("score") in ("alerta", "critico")]
            if alertas:
                tips = ", ".join(f["trait"] for f in alertas[:2])
                wellness_h.append(t["wellness_panel_alert"].format(label=label, tips=tips))

        if not wellness_h:
            wellness_h.append(t["wellness_ok"])
    h["wellness"] = wellness_h

    # ── Family ──
    family_h = []
    if family:
        carriers = family.get("carrier_findings", [])
        dominant = family.get("dominant_findings", [])
        total_rel = family.get("summary", {}).get("total_relevant", 0)

        if total_rel == 0:
            family_h.append(t["family_none"])
        else:
            if carriers:
                family_h.append(t["family_carrier"].format(count=len(carriers)))
            if dominant:
                family_h.append(t["family_dominant"].format(count=len(dominant)))
            family_h.append(t["family_counselor"])
    h["family"] = family_h

    return h


# ── Translation maps ─────────────────────────────────────────────────────────

CAT_PT = {
    "Drug Metabolism": "\U0001f48a Metabolismo de Medicamentos",
    "Methylation": "\U0001f9ec Metilacao",
    "Neurotransmitters": "\U0001f9e0 Neurotransmissores",
    "Caffeine Response": "\u2615 Resposta a Cafeina",
    "Cardiovascular": "\u2764\ufe0f Cardiovascular",
    "Nutrition": "\U0001f957 Nutricao",
    "Fitness": "\U0001f4aa Aptidao Fisica",
    "Sleep/Circadian": "\U0001f634 Sono / Ritmo Circadiano",
    "Inflammation": "\U0001f525 Inflamacao",
    "Autoimmune": "\U0001f6e1\ufe0f Autoimune",
    "Detoxification": "\U0001f9f9 Detoxificacao",
    "Skin": "\u2728 Pele",
    "Iron Metabolism": "\U0001fa78 Metabolismo do Ferro",
    "Longevity": "\u23f3 Longevidade",
    "Alcohol": "\U0001f377 Alcool",
}
ZYGOSITY_PT = {
    "AFFECTED": "AFETADO",
    "CARRIER": "PORTADOR",
    "CARRIER/AT_RISK": "PORTADOR/RISCO",
    "HETEROZYGOUS": "HETEROZIGOTO",
    "UNKNOWN": "INDEFINIDO",
}
import re as _re
from markupsafe import escape as _escape
def _md_bold(text):
    """Convert **text** markdown to <strong>text</strong> HTML. Escapes first for XSS safety."""
    if not text:
        return text
    escaped = str(_escape(text))
    return _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)

app.jinja_env.filters["bold"] = _md_bold
app.jinja_env.globals["CAT_PT"] = CAT_PT
app.jinja_env.globals["ZYG_PT"] = ZYGOSITY_PT
app.jinja_env.globals["translate_traits"] = translate_traits
app.jinja_env.globals["get_gene_context"] = get_gene_context
app.jinja_env.globals["translate_medical"] = translate_medical
app.jinja_env.globals["POP_COUNTRIES"] = POP_COUNTRIES

# Language state
_current_lang = "en"  # fallback default

def _get_lang():
    """Get language from cookie (per-request) or fallback to global default."""
    return request.cookies.get("lang", _current_lang) if request else _current_lang


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    global _current_lang
    # Restore language from cookie if not set via URL
    saved_lang = request.cookies.get("lang")
    if saved_lang in ("pt", "en"):
        _current_lang = saved_lang
    active = _jobs.get("active_result")
    history = _load_history_index()
    t = get_strings(_current_lang)

    # Always regenerate human conclusions in the current language
    human = {}
    if active and active.get("health"):
        _log(f"Regenerating human conclusions in lang={_current_lang}")
        try:
            human = build_human_conclusions(
                active.get("health", {}),
                active.get("disease"),
                active.get("protocol_data", {}),
                active.get("wellness", {}),
                active.get("family", {}),
                active.get("ancestry", {}),
                profile=active.get("genome_info", {}).get("profile", {}),
                lang=_current_lang,
            )
        except Exception:
            human = {}

        # Regenerate wellness panels in current language (for i18n)
        # Only if health data exists (needed for genome_by_rsid to re-analyze)
        # Note: wellness is cached from analysis. For language switch, we keep
        # the cached data since wellness texts are translated at display time
        # via the panel conclusions only.

        # Regenerate conclusions in current language
        try:
            conclusions = build_conclusions(
                active.get("health", {}),
                active.get("disease"),
                active.get("protocol_data", {}),
                lang=_current_lang,
            )
            active["conclusions"] = conclusions
        except Exception:
            pass

        # Regenerate family planning for old entries missing gestational/x-linked
        family = active.get("family") or {}
        if family and "gestational_risks" not in family and active.get("health"):
            try:
                family = analyze_family_planning(
                    active.get("disease"),
                    active.get("health", {}),
                    lang=_current_lang,
                )
                # Preserve phenotype from old data
                if active.get("family", {}).get("phenotype"):
                    family["phenotype"] = active["family"]["phenotype"]
                active["family"] = family
            except Exception:
                pass

    # AI chat is opt-in: requires Ollama installed AND the user toggling it on
    # in /settings. We detect both signals on each page load so the FAB reflects
    # the latest state without needing a restart.
    try:
        from src.local_ai import is_ollama_available, list_models
        from src.preferences import is_ai_chat_enabled
        ollama_installed = is_ollama_available()
        ai_chat_enabled = is_ai_chat_enabled()
        ollama_ready = ollama_installed and ai_chat_enabled
        ollama_models = list_models() if ollama_ready else []
    except Exception:
        ollama_installed = False
        ai_chat_enabled = False
        ollama_ready = False
        ollama_models = []

    return render_template(
        "dashboard.html",
        results=active.get("health") if active else None,
        disease=active.get("disease") if active else None,
        disease_stats=active.get("disease_stats") if active else None,
        genome_info=active.get("genome_info") if active else None,
        protocol=active.get("protocol_data") if active else None,
        charts_json=build_charts_json(active["health"], active.get("disease"), lang=_current_lang) if active and active.get("health") else "{}",
        conclusions=active.get("conclusions") or {} if active else {},
        human=human,
        wellness=active.get("wellness") or {} if active else {},
        ancestry=active.get("ancestry") or {} if active else {},
        family=active.get("family") or {} if active else {},
        hereditary=active.get("hereditary") or {} if active else {},
        coverage=active.get("coverage") or {} if active else {},
        prs=active.get("prs") or {} if active else {},
        elapsed=active.get("elapsed", 0) if active else 0,
        history=history,
        t=t,
        lang=_current_lang,
        ollama_ready=ollama_ready,
        ollama_models=ollama_models,
        ollama_installed=ollama_installed,
        ai_chat_enabled=ai_chat_enabled,
        needs_translator=_block_pt_without_translator(),
        needs_clinvar=_clinvar_missing(),
        needs_pharmgkb=_pharmgkb_missing(),
    )


@app.route("/lang/<code>")
def set_lang(code):
    global _current_lang
    if code in ("pt", "en"):
        _current_lang = code
    resp = redirect(url_for("index"))
    resp.set_cookie("lang", _current_lang, max_age=365*24*3600, httponly=True, samesite="Strict")
    return resp


@app.route("/consent", methods=["GET", "POST"])
def consent():
    """Show terms and accept consent via web."""
    t = get_strings(_current_lang)
    if request.method == "POST":
        from src.consent import CONSENT_FILE
        CONSENT_FILE.write_text(
            "consent_accepted=true\n"
            "This file records that the user accepted the terms of use.\n"
            "Delete this file to be prompted again.\n"
        )
        flash(get_strings(_get_lang())["flash_terms_accepted"])
        return redirect(url_for("index"))
    return render_template("consent.html", terms=TERMS_TEXT, t=t, lang=_current_lang)


def _block_pt_without_translator() -> bool:
    """In PT mode the analysis depends on the neural translator. If the
    model isn't installed, redirect the user to /settings instead of
    producing a half-translated report. EN mode bypasses this entirely."""
    if _get_lang() != "pt":
        return False
    from src.system_status import is_argos_model_installed
    return not is_argos_model_installed()


def _clinvar_missing() -> bool:
    """ClinVar is the core reference DB. Analysing without it yields an
    empty report — better to redirect than fake success."""
    from config import CLINVAR_TSV
    return not CLINVAR_TSV.exists()


def _pharmgkb_missing() -> bool:
    from config import PHARMGKB_ANNOTATIONS, PHARMGKB_ALLELES
    return not (PHARMGKB_ANNOTATIONS.exists() and PHARMGKB_ALLELES.exists())


@app.route("/analyze", methods=["POST"])
def analyze():
    _log("ROUTE HIT /analyze")
    if not require_consent_web():
        return redirect(url_for("consent"))
    if _block_pt_without_translator():
        flash(get_strings(_get_lang())["flash_translator_required"])
        return redirect(url_for("settings"))
    if _clinvar_missing():
        flash(get_strings(_get_lang())["flash_clinvar_required"])
        return redirect(url_for("settings"))
    try:
        _t = get_strings(_get_lang())
        if "genome_file" not in request.files:
            flash(_t["flash_no_file"])
            return redirect(url_for("index"))

        uploaded = request.files["genome_file"]
        if uploaded.filename == "":
            flash(_t["flash_no_file"])
            return redirect(url_for("index"))

        subject_name = request.form.get("subject_name", "").strip() or None
        # Profile (optional)
        profile = {}
        sex = request.form.get("sex", "").strip()
        if sex in ("M", "F"):
            profile["sex"] = sex
        try:
            age = int(request.form.get("age", "") or 0)
            if 1 <= age <= 120:
                profile["age"] = age
        except (ValueError, TypeError):
            pass
        try:
            weight = float(request.form.get("weight", "") or 0)
            if 20 <= weight <= 300:
                profile["weight"] = weight
        except (ValueError, TypeError):
            pass
        try:
            height = int(request.form.get("height", "") or 0)
            if 100 <= height <= 250:
                profile["height"] = height
                if profile.get("weight"):
                    profile["bmi"] = round(profile["weight"] / (height / 100) ** 2, 1)
        except (ValueError, TypeError):
            pass

        ensure_directories()
        filename = secure_filename(uploaded.filename)
        allowed_ext = {'.txt', '.csv', '.tsv', '.gz'}
        if not any(filename.lower().endswith(ext) for ext in allowed_ext):
            flash(_t["flash_invalid_file"])
            return redirect(url_for("index"))
        filepath = INPUT_DIR / filename
        uploaded.save(str(filepath))
        _log(f"Arquivo salvo: {filename} ({filepath.stat().st_size:,} bytes)")
    except Exception as ex:
        _log(f"ERRO upload: {ex}\n{traceback.format_exc()}")
        flash(get_strings(_get_lang())["flash_upload_error"])
        return redirect(url_for("index"))

    # Start background job
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "running", "progress": "Iniciando...", "step": 0, "result": None, "error": None}
    _jobs["current_job"] = job_id

    _lang_for_thread = _get_lang()
    t = threading.Thread(target=_run_analysis, args=(job_id, filepath, subject_name, profile, _lang_for_thread), daemon=True)
    t.start()

    return redirect(url_for("loading", job_id=job_id))


@app.route("/analyze-sample", methods=["POST"])
def analyze_sample():
    """Run the analysis on the bundled synthetic sample genome.

    The source file at sample/sample_genome.csv is COPIED into INPUT_DIR
    under a timestamped name. The background job then secure_deletes the
    copy after analysis (same as a real upload), but the original sample
    stays intact — so the user can hit "try sample" repeatedly even after
    deleting the resulting analyses from history.
    """
    if not require_consent_web():
        return redirect(url_for("consent"))
    if _block_pt_without_translator():
        flash(get_strings(_get_lang())["flash_translator_required"])
        return redirect(url_for("settings"))
    _t = get_strings(_get_lang())
    sample_src = Path(__file__).parent / "sample" / "sample_genome.csv"
    if not sample_src.exists():
        flash(_t.get("flash_sample_missing", "Sample genome file not found."))
        return redirect(url_for("index"))

    ensure_directories()
    # Timestamped name keeps concurrent runs from clobbering each other and
    # makes it obvious in INPUT_DIR which copies came from the sample button.
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = INPUT_DIR / f"sample_{ts}.csv"
    shutil.copyfile(sample_src, filepath)
    _log(f"Sample copiado para analise: {filepath.name}")

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "running", "progress": "Iniciando...", "step": 0, "result": None, "error": None}
    _jobs["current_job"] = job_id
    _lang_for_thread = _get_lang()
    th = threading.Thread(
        target=_run_analysis,
        args=(job_id, filepath, "Sample", {}, _lang_for_thread),
        daemon=True,
    )
    th.start()
    return redirect(url_for("loading", job_id=job_id))


@app.route("/loading/<job_id>")
def loading(job_id):
    t = get_strings(_current_lang)
    return render_template("loading.html", job_id=job_id, t=t, lang=_current_lang)


@app.route("/api/db-status")
def db_status():
    """Sub-progress for the DB preloader so the loading page can show
    'Loading ClinVar (12s elapsed)' instead of a generic spinner."""
    s = _db_cache["status"]
    elapsed = None
    if s["started_at"]:
        end = s["finished_at"] or time.time()
        elapsed = round(end - s["started_at"], 1)
    return jsonify({
        "loaded": _db_cache["loaded"],
        "current": s["current"],
        "elapsed_seconds": elapsed,
        "error": s["error"],
    })


@app.route("/status/<job_id>")
def job_status(job_id):
    job = _jobs.get(job_id, {"status": "not_found"})
    return jsonify({
        "status": job.get("status", "not_found"),
        "progress": job.get("progress", ""),
        "step": job.get("step", 0),
        "error": job.get("error"),
    })


@app.route("/done/<job_id>")
def job_done(job_id):
    job = _jobs.get(job_id)
    if not job or job["status"] != "done":
        flash(get_strings(_get_lang())["flash_analysis_not_found"])
        return redirect(url_for("index"))
    _jobs["active_result"] = job["result"]
    return redirect(url_for("index"))


@app.route("/history/load/<hid>")
def load_history(hid):
    data = _load_history_full(hid)
    if not data:
        flash(get_strings(_get_lang())["flash_history_not_found"])
        return redirect(url_for("index"))
    _jobs["active_result"] = data
    return redirect(url_for("index"))


@app.route("/history/delete/<hid>", methods=["POST"])
def delete_history(hid):
    _delete_history(hid)
    flash(get_strings(_get_lang())["flash_history_deleted"])
    return redirect(url_for("index"))


@app.route("/clear", methods=["POST"])
def clear():
    _jobs.pop("active_result", None)
    flash(get_strings(_get_lang())["flash_results_cleared"])
    return redirect(url_for("index"))


def _build_chat_context(active: dict, lang: str) -> str:
    """Serialize the active analysis into a compact text the LLM can read."""
    if not active:
        return "No analysis is loaded."

    lines = []
    info = active.get("genome_info") or {}
    if info:
        lines.append(f"Total SNPs: {info.get('total_snps', '?')}, format: {info.get('format', '?')}")
        profile = info.get("profile") or {}
        if profile:
            bits = []
            for key in ("sex", "age", "weight", "height"):
                if profile.get(key):
                    bits.append(f"{key}={profile[key]}")
            if bits:
                lines.append("Profile: " + ", ".join(bits))

    health_findings = (active.get("health") or {}).get("findings") or []
    if health_findings:
        lines.append("")
        lines.append(f"Lifestyle / pharmacogenomics findings ({len(health_findings)} total — showing top 20):")
        for f in health_findings[:20]:
            lines.append(
                f"- {f.get('rsid')} ({f.get('gene','?')}, {f.get('category','?')}): "
                f"{f.get('genotype','?')} — {f.get('description','')[:160]}"
            )

    disease = active.get("disease") or {}
    disease_findings = disease.get("findings") if isinstance(disease, dict) else []
    if disease_findings:
        lines.append("")
        lines.append(f"Disease-associated variants ({len(disease_findings)} total — showing top 15):")
        for f in disease_findings[:15]:
            lines.append(
                f"- {f.get('rsid')} ({f.get('gene','?')}): {f.get('clinical_significance','?')} "
                f"— {(f.get('phenotype') or f.get('description') or '')[:160]}"
            )

    wellness = active.get("wellness") or {}
    active_panels = [(k, v) for k, v in wellness.items() if v.get("findings")]
    if active_panels:
        lines.append("")
        lines.append(f"Active wellness panels ({len(active_panels)}):")
        for name, panel in active_panels[:10]:
            findings_count = len(panel.get("findings", []))
            lines.append(f"- {name}: {findings_count} findings")

    ancestry = active.get("ancestry") or {}
    if ancestry.get("region_scores"):
        top = sorted(ancestry["region_scores"].items(), key=lambda kv: kv[1], reverse=True)[:5]
        lines.append("")
        lines.append("Top ancestry regions: " + ", ".join(f"{r} ({s:.0%})" for r, s in top))

    family = active.get("family") or {}
    if family.get("phenotype"):
        lines.append("")
        lines.append("Phenotype: " + ", ".join(f"{k}={v}" for k, v in family["phenotype"].items() if v))

    return "\n".join(lines) if lines else "Analysis loaded but no notable findings."


@app.route("/api/chat/ask", methods=["POST"])
def chat_ask():
    """Send a question + chat history to Ollama and return the assistant reply.
    CSRF is already enforced by the global before_request hook."""
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    if not question:
        return {"ok": False, "error": "empty question"}, 400

    from src.preferences import is_ai_chat_enabled
    if not is_ai_chat_enabled():
        return {"ok": False, "error": "ai_chat_disabled"}, 403

    history = payload.get("history") or []
    model = payload.get("model") or "llama3.1:8b"
    lang = _get_lang()

    active = _jobs.get("active_result")
    context = _build_chat_context(active, lang)

    from src.local_ai import chat_about_analysis, estimate_tokens, estimate_prompt_tokens
    import time as _time
    started = _time.monotonic()
    ok, reply = chat_about_analysis(
        context=context,
        history=history,
        question=question,
        model=model,
        language=lang,
    )
    elapsed_ms = int((_time.monotonic() - started) * 1000)
    if not ok:
        return {"ok": False, "error": reply}, 503
    prompt_tokens = estimate_prompt_tokens(context, history, question, language=lang)
    completion_tokens = estimate_tokens(reply)
    return {
        "ok": True,
        "reply": reply,
        "elapsed_ms": elapsed_ms,
        "tokens": {
            "prompt": prompt_tokens["total"],
            "completion": completion_tokens,
            "total": prompt_tokens["total"] + completion_tokens,
        },
    }


@app.route("/settings")
def settings():
    """Show installation status of databases and optional integrations."""
    from src.system_status import check_all
    from src.preferences import is_ai_chat_enabled
    t = get_strings(_get_lang())
    components = check_all()
    ollama_installed = any(c.key == "ollama" and c.installed for c in components)
    argos = next((c for c in components if c.key == "argos"), None)
    # argos.installed is True only when both package AND model are present.
    argos_pkg_present = bool(argos and "not installed in this Python" not in argos.detail)
    return render_template(
        "settings.html",
        t=t,
        lang=_get_lang(),
        components=components,
        ai_chat_enabled=is_ai_chat_enabled(),
        ollama_installed=ollama_installed,
        translator_ready=bool(argos and argos.installed),
        translator_pkg_present=argos_pkg_present,
        translator_install=dict(_translator_install),
    )


# Neural translator install state: shared so the settings page can poll
# progress while the download runs in the background. The install pulls
# ~100MB from the network, so it MUST run on a thread spawned from the
# Flask request — never from inside the NetworkBlocker.
_translator_install = {"running": False, "ok": None, "message": "", "started_at": None}
_translator_install_lock = threading.Lock()


def _install_translator_worker():
    from src.translator import install_en_pt_model
    ok, msg = install_en_pt_model()
    _translator_install["running"] = False
    _translator_install["ok"] = ok
    _translator_install["message"] = msg
    _log(f"Translator install: ok={ok} msg={msg}")


@app.route("/settings/install-translator", methods=["POST"])
def settings_install_translator():
    """Kick off a background download of the Argos en->pt model."""
    with _translator_install_lock:
        if _translator_install["running"]:
            return redirect(url_for("settings"))
        _translator_install.update({
            "running": True, "ok": None, "message": "", "started_at": time.time(),
        })
    threading.Thread(target=_install_translator_worker, daemon=True, name="argos-install").start()
    return redirect(url_for("settings"))


@app.route("/api/translator-status")
def translator_status():
    from src.system_status import is_argos_model_installed
    elapsed = None
    if _translator_install["started_at"]:
        elapsed = round(time.time() - _translator_install["started_at"], 1)
    return jsonify({
        "running": _translator_install["running"],
        "ok": _translator_install["ok"],
        "message": _translator_install["message"],
        "elapsed_seconds": elapsed,
        "model_installed": is_argos_model_installed(),
    })


@app.route("/settings/ai-toggle", methods=["POST"])
def settings_ai_toggle():
    """Flip the AI chat opt-in. Requires Ollama to be installed before enabling."""
    from src.local_ai import is_ollama_available
    from src.preferences import set_ai_chat_enabled, is_ai_chat_enabled
    desired = not is_ai_chat_enabled()
    if desired and not is_ollama_available():
        flash(get_strings(_get_lang())["flash_install_ollama"])
        return redirect(url_for("settings"))
    set_ai_chat_enabled(desired)
    return redirect(url_for("settings"))


def run_dashboard(port: int = 5000, debug: bool = False):
    ensure_directories()
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    print()
    print("=" * 60)
    print("  DASHBOARD GENETICO LOCAL")
    print(f"  http://127.0.0.1:{port}")
    print()
    print("  Privacidade: servidor apenas em localhost")
    print("  ECharts + Tabler servidos localmente (sem CDN)")
    print("=" * 60)
    print()
    # Kick off DB loading in the background so the first analysis doesn't
    # eat the 30-90s ClinVar parse. The /api/db-status endpoint surfaces
    # progress to the loading page if a user uploads before it finishes.
    # Skip during the Werkzeug reloader's parent process to avoid loading
    # twice (debug=True spawns a child that reruns this).
    if not (debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true"):
        _preload_dbs_async()
        print("  Pre-carregando bancos de dados em background...")
        print()
    app.config["TEMPLATES_AUTO_RELOAD"] = debug
    app.run(host="127.0.0.1", port=port, debug=debug)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    run_dashboard(args.port)
