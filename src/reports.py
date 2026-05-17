"""
Report generators — produce markdown files from analysis results.

Three reports:
1. Genetic Health Report (lifestyle SNPs + PharmGKB)
2. Disease Risk Report (ClinVar pathogenic/risk variants)
3. Actionable Health Protocol (synthesis of all findings)

No system-identifying metadata is written. No network access.
"""
from datetime import datetime
from collections import defaultdict
from pathlib import Path

from src.privacy import sanitize_report_metadata


def _meta_header(subject_name: str = None) -> str:
    meta = sanitize_report_metadata()
    lines = [f"**Generated:** {meta['generated_at']}"]
    if subject_name:
        lines.insert(0, f"**Subject:** {subject_name}")
    lines.append(f"**Tool:** {meta['tool']} v{meta['version']}")
    return "\n".join(lines)


LIMITATIONS_BANNER = """
> **IMPORTANTE: Esta e uma ferramenta de exploracao educacional, NAO um laudo clinico.**
>
> - Genotipagem de consumo (23andMe, AncestryDNA, etc.) usa chips de SNP, nao sequenciamento
>   de grau clinico. Os dados brutos sao rotulados pelas proprias empresas como adequados
>   apenas para pesquisa, educacao e informacao — nao para fins medicos.
> - Pesquisas publicadas encontraram uma **taxa de falso positivo de ~40%** para variantes
>   de significancia clinica em dados brutos de testes DTC (Tandy-Connor et al.,
>   *Genetics in Medicine*, 2018).
> - ClinVar e um arquivo publico de associacoes variante-doenca, nao um veredito automatico
>   sobre sua saude. PharmGKB/CPIC sao ferramentas de apoio a decisao clinica para medicos,
>   nao para auto-suplementacao ou ajuste de doses por conta propria.
> - Doencas comuns (cancer, Alzheimer, diabetes, cardiovasculares) sao **poligenicas e
>   dependentes de contexto** — um painel de SNPs nao consegue prever se voce as desenvolvera.
> - **Qualquer achado preocupante deve ser confirmado por teste de grau clinico e avaliado
>   por um conselheiro genetico ou medico antes de qualquer acao.**
> - Encontre um conselheiro genetico: [Diretorio NSGC](https://findageneticcounselor.nsgc.org)

"""


DISCLAIMER = """
---

## Avisos e Limitacoes

### Isto NAO e um diagnostico clinico

Este relatorio e apenas para **exploracao educacional e informativa**. Ele nao constitui
aconselhamento medico, diagnostico ou recomendacao de tratamento.

### Por que voce NAO deve agir com base apenas nisto

1. **Alta taxa de falso positivo.** Um estudo de 2018 na *Genetics in Medicine* encontrou
   que ~40% das variantes sinalizadas como clinicamente significativas em dados brutos de
   testes DTC eram falsos positivos quando confirmadas por sequenciamento clinico. As proprias
   empresas (23andMe, AncestryDNA) afirmam que seus dados brutos nao sao validados para uso clinico.

2. **Anotacoes de bancos de dados nao sao vereditos.** O ClinVar coleta submissoes sobre
   relacoes variante-doenca — classificacoes mudam, conflitam e dependem de ancestralidade,
   historico familiar e contexto. Um rotulo "Pathogenic" no ClinVar nao significa que voce
   tem ou tera uma condicao.

3. **Risco poligenico nao e capturado aqui.** A maioria das doencas comuns (cardiacas,
   diabetes, muitos canceres, Alzheimer) envolve centenas ou milhares de variantes mais
   fatores ambientais. Um punhado de SNPs nao consegue prever de forma significativa o
   seu risco individual.

4. **PharmGKB/CPIC sao ferramentas de suporte a decisao clinica para medicos.** Foram
   projetadas para ajudar clinicos a ajustar prescricoes quando resultados de testes
   geneticos validados estao disponiveis — nao para auto-suplementacao ou mudancas de dose.

5. **Penetrancia e incompleta.** Muitas pessoas que carregam variantes "patogenicas" nunca
   desenvolvem a condicao associada. E doencas podem ocorrer sem nenhuma variante conhecida.

### O que voce DEVE fazer

- **Trate todos os achados como sinais preliminares**, nao como fatos confirmados.
- **Foque apenas em achados de alta evidencia** (ClinVar 3-4 estrelas, PharmGKB Nivel 1A/1B).
- **Confirme qualquer resultado preocupante** com teste genetico de grau clinico solicitado
  por um profissional de saude.
- **Consulte um conselheiro genetico** antes de tomar qualquer decisao de saude com base
  nestes dados. Diretorio: https://findageneticcounselor.nsgc.org
- **Nao mude medicamentos, doses ou suplementos** com base apenas neste relatorio.

### Referencias

- MedlinePlus: "Dados brutos de testes DTC sao dificeis de interpretar e nao devem ser
  usados para diagnosticar doencas" (https://medlineplus.gov/genetics/)
- NHGRI/Genome.gov: "Achados de dados brutos requerem confirmacao clinica antes de
  decisoes de cuidado" (https://www.genome.gov/)
- Tandy-Connor et al. (2018). "False-positive results released by direct-to-consumer
  genetic tests." *Genetics in Medicine*, 20(12), 1515-1521.

*Gerado localmente — zero dados transmitidos para servidores externos.*
"""


# ═══════════════════════════════════════════════════════════════════════════════
# REPORT 1: GENETIC HEALTH REPORT
# ═══════════════════════════════════════════════════════════════════════════════

def generate_genetic_report(results: dict, path: Path, subject_name: str = None):
    """Generate comprehensive lifestyle/health genetic report."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Relatorio de Exploracao Genetica\n\n{_meta_header(subject_name)}\n\n")
        f.write(LIMITATIONS_BANNER)
        f.write("---\n\n")

        # Executive Summary
        s = results["summary"]
        f.write("## Resumo Geral\n\n")
        f.write(f"- **Total de SNPs no genoma:** {s['total_snps']:,}\n")
        f.write(f"- **SNPs cruzados com banco curado:** {s['analyzed_snps']}\n")
        f.write(f"- **Achados de alta magnitude (>= 3):** {s['high_impact']}\n")
        f.write(f"- **Achados de magnitude moderada (2):** {s['moderate_impact']}\n")
        f.write(f"- **Achados notaveis (1):** {s['low_impact']}\n")
        f.write(f"- **Interacoes droga-gene PharmGKB (Nivel 1-2):** {len(results['pharmgkb_findings'])}\n\n")

        # High-impact findings
        f.write("---\n\n## Achados Notaveis (Requerem Confirmacao Clinica)\n\n")
        f.write("*Estes sao sinais preliminares baseados em genotipagem de consumo. ")
        f.write("Qualquer achado aqui deve ser confirmado por teste clinico antes de qualquer acao.*\n\n")
        high = [x for x in results["findings"] if x["magnitude"] >= 3]
        if high:
            for finding in high:
                f.write(f"### {finding['gene']} ({finding['rsid']})\n\n")
                f.write(f"- **Categoria:** {finding['category']}\n")
                f.write(f"- **Seu Genotipo:** `{finding['genotype']}`\n")
                f.write(f"- **Status:** {finding['status'].replace('_', ' ').title()}\n")
                f.write(f"- **Magnitude:** {finding['magnitude']}/6\n")
                f.write(f"- **Detalhes:** {finding['description']}\n")
                f.write(f"- **Confianca:** Preliminar — dados de chip de consumo, nao validados clinicamente\n\n")
        else:
            f.write("Nenhum achado de alta magnitude (>= 3) detectado.\n\n")

        # Category-by-category breakdown
        category_order = [
            ("Drug Metabolism", "Como voce processa medicamentos"),
            ("Methylation", "Processamento de vitaminas B e ciclo de metilacao"),
            ("Neurotransmitters", "Dopamina, serotonina, quimica cerebral"),
            ("Caffeine Response", "Metabolismo e sensibilidade a cafeina"),
            ("Cardiovascular", "Saude cardiaca e pressao arterial"),
            ("Nutrition", "Metabolismo de nutrientes e necessidades alimentares"),
            ("Fitness", "Resposta ao exercicio e perfil atletico"),
            ("Sleep/Circadian", "Padroes de sono e ritmo circadiano"),
            ("Inflammation", "Resposta inflamatoria"),
            ("Autoimmune", "Suscetibilidade autoimune"),
            ("Detoxification", "Enzimas de detoxificacao fase I/II"),
            ("Skin", "Envelhecimento cutaneo e resposta UV"),
            ("Iron Metabolism", "Absorcao e armazenamento de ferro"),
            ("Longevity", "Variantes associadas a envelhecimento e longevidade"),
            ("Alcohol", "Metabolismo do alcool"),
        ]

        for cat_name, cat_desc in category_order:
            cat_findings = results["by_category"].get(cat_name, [])
            if not cat_findings:
                continue
            f.write(f"---\n\n## {cat_name}\n\n*{cat_desc}*\n\n")
            f.write("| Gene | rsID | Genotipo | Status | Magnitude | Detalhes |\n")
            f.write("|------|------|----------|--------|-----------|----------|\n")
            for finding in sorted(cat_findings, key=lambda x: -x["magnitude"]):
                status = finding["status"].replace("_", " ").title()
                desc = finding["description"][:80]
                f.write(f"| {finding['gene']} | {finding['rsid']} | `{finding['genotype']}` | {status} | {finding['magnitude']}/6 | {desc} |\n")
            f.write("\n")

        # PharmGKB drug interactions
        f.write("---\n\n## Interacoes Droga-Gene (PharmGKB)\n\n")
        f.write("**Apenas para referencia do medico.** As diretrizes PharmGKB/CPIC foram ")
        f.write("projetadas para ajudar clinicos a ajustar prescricoes quando resultados de ")
        f.write("testes geneticos *validados* estao disponiveis. NAO mude medicamentos ou doses ")
        f.write("com base apenas em genotipagem de consumo. Compartilhe esta secao com seu ")
        f.write("medico prescritor para avaliacao.\n\n")

        level_1 = [x for x in results["pharmgkb_findings"] if x["level"] in ("1A", "1B")]
        level_2 = [x for x in results["pharmgkb_findings"] if x["level"] in ("2A", "2B")]

        if level_1:
            f.write("### Nivel 1 — Diretrizes Clinicas Existentes\n\n")
            f.write("| Gene | Nivel | Medicamentos | Seu Genotipo |\n")
            f.write("|------|-------|--------------|---------------|\n")
            for item in level_1:
                drugs = item["drugs"][:60] + "..." if len(item["drugs"]) > 60 else item["drugs"]
                f.write(f"| {item['gene']} | {item['level']} | {drugs} | `{item['genotype']}` |\n")
            f.write("\n")

        if level_2:
            f.write("### Nivel 2 — Evidencia Moderada\n\n")
            f.write("| Gene | Nivel | Medicamentos | Seu Genotipo |\n")
            f.write("|------|-------|--------------|---------------|\n")
            for item in level_2[:20]:
                drugs = item["drugs"][:60] + "..." if len(item["drugs"]) > 60 else item["drugs"]
                f.write(f"| {item['gene']} | {item['level']} | {drugs} | `{item['genotype']}` |\n")
            if len(level_2) > 20:
                f.write(f"\n*...e mais {len(level_2) - 20} interacoes de Nivel 2*\n")
            f.write("\n")

        if not level_1 and not level_2:
            f.write("Nenhuma interacao droga-gene de Nivel 1-2 detectada.\n\n")

        f.write(DISCLAIMER)


# ═══════════════════════════════════════════════════════════════════════════════
# REPORT 2: DISEASE RISK REPORT
# ═══════════════════════════════════════════════════════════════════════════════

def generate_disease_report(
    findings: dict,
    stats: dict,
    genome_count: int,
    path: Path,
    subject_name: str = None,
):
    """Generate disease risk report from ClinVar analysis."""
    if not findings:
        return

    # Classify by zygosity
    affected = [f for f in findings["pathogenic"] + findings["likely_pathogenic"]
                if f.get("zygosity_status") == "AFFECTED"]
    carriers = [f for f in findings["pathogenic"] + findings["likely_pathogenic"]
                if f.get("zygosity_status") == "CARRIER"]
    het_unknown = [f for f in findings["pathogenic"] + findings["likely_pathogenic"]
                   if f.get("zygosity_status") not in ("AFFECTED", "CARRIER")]

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Relatorio de Exploracao de Variantes\n\n{_meta_header(subject_name)}\n\n")
        f.write(LIMITATIONS_BANNER)
        f.write("---\n\n")

        # Summary table
        f.write("## Resumo de Correspondencias ClinVar\n\n")
        f.write("*Estas sao correspondencias em banco de dados, nao diagnosticos. Um rotulo ")
        f.write("\"Pathogenic\" no ClinVar significa que a variante foi reportada como associada ")
        f.write("a doenca — NAO significa que voce tem ou tera a condicao. A penetrancia e ")
        f.write("frequentemente incompleta, e dados de chip de consumo tem uma taxa de falso ")
        f.write("positivo de ~40% para tais variantes.*\n\n")
        f.write(f"- **Total de SNPs analisados:** {genome_count:,}\n")
        f.write(f"- **Posicoes ClinVar verificadas:** {stats['total_clinvar_positions']:,}\n")
        f.write(f"- **Posicoes encontradas no seu genoma:** {stats['matched']:,}\n\n")

        f.write("| Categoria | Quantidade |\n")
        f.write("|-----------|------------|\n")
        f.write(f"| Patogenica (Afetado) | {len(affected)} |\n")
        f.write(f"| Patogenica (Portador) | {len(carriers)} |\n")
        f.write(f"| Patogenica (Het, heranca indefinida) | {len(het_unknown)} |\n")
        f.write(f"| Fatores de Risco | {len(findings['risk_factor'])} |\n")
        f.write(f"| Resposta a Medicamentos | {len(findings['drug_response'])} |\n")
        f.write(f"| Protetoras | {len(findings['protective'])} |\n\n")

        # Confidence guide
        f.write("### Confianca (Estrelas)\n\n")
        f.write("- 4 estrelas: Diretriz de pratica / Painel de especialistas\n")
        f.write("- 3 estrelas: Multiplos submissores, sem conflitos\n")
        f.write("- 2 estrelas: Multiplos submissores ou unico com criterios\n")
        f.write("- 1 estrela: Submissor unico\n")
        f.write("- 0 estrelas: Sem criterios de afirmacao\n\n")

        # Affected
        if affected:
            f.write("---\n\n## Variantes Patogenicas — Status Afetado\n\n")
            f.write("**Consulte um conselheiro genetico ou medico.**\n\n")
            for item in affected:
                _write_variant_detail(f, item)

        # Carriers
        if carriers:
            f.write("---\n\n## Status de Portador — Condicoes Recessivas\n\n")
            f.write("Portadores tipicamente nao apresentam sintomas. Implicacoes reprodutivas se o parceiro tambem for portador.\n\n")
            for item in carriers:
                _write_variant_detail(f, item)

        # Het unknown
        if het_unknown:
            f.write("---\n\n## Patogenica — Heranca Indefinida\n\n")
            for item in het_unknown:
                _write_variant_detail(f, item)

        # Risk factors
        if findings["risk_factor"]:
            f.write("---\n\n## Variantes de Fator de Risco\n\n")
            f.write("| Gene | rsID | Genotipo | Confianca | Condicao |\n")
            f.write("|------|------|----------|-----------|----------|\n")
            for item in findings["risk_factor"][:40]:
                stars = item.get("gold_stars", 0)
                condition = (item.get("traits") or "Desconhecida").split(";")[0][:60]
                f.write(f"| {item.get('gene', '---')} | {item['rsid']} | `{item['user_genotype']}` | {stars}/4 | {condition} |\n")
            f.write("\n")

        # Drug response
        if findings["drug_response"]:
            f.write("---\n\n## Variantes de Resposta a Medicamentos\n\n")
            f.write("| Gene | rsID | Genotipo | Medicamento/Resposta |\n")
            f.write("|------|------|----------|----------------------|\n")
            for item in findings["drug_response"][:30]:
                response = (item.get("traits") or "Desconhecida")[:60]
                f.write(f"| {item.get('gene', '---')} | {item['rsid']} | `{item['user_genotype']}` | {response} |\n")
            f.write("\n")

        # Protective
        if findings["protective"]:
            f.write("---\n\n## Variantes Protetoras\n\n")
            for item in findings["protective"]:
                condition = (item.get("traits") or "Efeito protetor").split(";")[0]
                f.write(f"- **{item.get('gene', '---')}** ({item['rsid']}): {condition}\n")
            f.write("\n")

        f.write(DISCLAIMER)


def _write_variant_detail(f, item: dict):
    """Write detailed variant info block."""
    stars = "*" * item.get("gold_stars", 0) + "." * (4 - item.get("gold_stars", 0))
    condition = (item.get("traits") or "Not specified").split(";")[0]
    zyg = "Homozigoto" if item.get("is_homozygous") else "Heterozigoto"

    f.write(f"### {item.get('gene', '---')} — {condition}\n\n")
    f.write(f"| Campo | Valor |\n")
    f.write(f"|-------|-------|\n")
    f.write(f"| Gene | {item.get('gene', '---')} |\n")
    f.write(f"| Posicao | chr{item.get('chrom', '?')}:{item.get('pos', '?')} |\n")
    f.write(f"| rsID | {item.get('rsid', '---')} |\n")
    f.write(f"| Genotipo | `{item.get('user_genotype', '?')}` ({zyg}) |\n")
    f.write(f"| Variante | {item.get('ref', '?')} > {item.get('alt', '?')} |\n")
    f.write(f"| Significancia | {item.get('clinical_significance', '---')} |\n")
    f.write(f"| Confianca | {stars} ({item.get('gold_stars', 0)}/4) |\n")
    f.write(f"| Heranca | {item.get('inheritance') or 'Nao especificada'} |\n\n")

    if item.get("hgvs_p") or item.get("hgvs_c"):
        f.write(f"**Detalhe molecular:** {item.get('hgvs_p') or item.get('hgvs_c', '')}\n\n")
    if item.get("traits"):
        f.write(f"**Condicoes:** {item['traits']}\n\n")
    f.write("---\n\n")


# ═══════════════════════════════════════════════════════════════════════════════
# REPORT 3: ACTIONABLE HEALTH PROTOCOL
# ═══════════════════════════════════════════════════════════════════════════════

def generate_protocol(
    health_results: dict,
    disease_findings: dict,
    path: Path,
    subject_name: str = None,
):
    """Generate actionable health protocol combining all analysis sources."""
    findings_dict = {f["gene"]: f for f in health_results["findings"]}

    # Classify disease findings
    affected, carriers = [], []
    if disease_findings:
        for item in disease_findings.get("pathogenic", []) + disease_findings.get("likely_pathogenic", []):
            if item.get("zygosity_status") == "AFFECTED":
                affected.append(item)
            elif item.get("zygosity_status") == "CARRIER":
                carriers.append(item)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Notas para Discussao com Medico\n\n{_meta_header(subject_name)}\n\n")
        f.write(LIMITATIONS_BANNER)

        f.write("**O que e este documento:** Uma sintese de sinais geneticos preliminares em ")
        f.write("topicos para *discutir com seu medico*. NAO e uma prescricao, ")
        f.write("protocolo ou plano de tratamento.\n\n")
        f.write("**O que fazer com ele:** Leve a uma consulta medica como ponto de partida ")
        f.write("para conversa. Nao se auto-prescreva suplementos, mude medicamentos ")
        f.write("ou altere doses com base apenas neste documento.\n\n")

        # Summary counts
        f.write(f"Fontes de dados: {len(health_results['findings'])} SNPs de estilo de vida, ")
        f.write(f"{len(health_results['pharmgkb_findings'])} correspondencias droga-gene")
        if disease_findings:
            f.write(f", {len(affected)} correspondencias patogenicas ClinVar, {len(carriers)} portadores")
            f.write(f", {len(disease_findings.get('risk_factor', []))} fatores de risco")
        f.write("\n\n---\n\n")

        # Notable findings
        f.write("## Achados Notaveis (Nao Confirmados)\n\n")
        f.write("*Todos os achados abaixo sao baseados em genotipagem de consumo e consultas ")
        f.write("a bancos de dados. Requerem confirmacao clinica antes de qualquer acao.*\n\n")
        high_impact = [x for x in health_results["findings"] if x["magnitude"] >= 3]
        if high_impact:
            for item in high_impact:
                f.write(f"- **{item['gene']}** ({item['category']}): {item['description']}\n")
        else:
            f.write("Nenhum achado de alta magnitude detectado.\n")

        if affected:
            f.write("\n### Correspondencias Patogenicas ClinVar (Requerem Confirmacao Clinica)\n\n")
            f.write("*Um rotulo \"Pathogenic\" no ClinVar significa que a variante foi associada a ")
            f.write("uma condicao em relatorios submetidos. NAO confirma que voce tem ou tera ")
            f.write("a condicao. Taxa de falso positivo de ~40% para dados de chip de consumo.*\n\n")
            for item in affected:
                condition = (item.get("traits") or "Desconhecida").split(";")[0]
                f.write(f"- **{item.get('gene', '---')}**: {condition} ({item.get('gold_stars', 0)}/4 confianca)\n")

        if carriers:
            f.write("\n### Status de Portador\n\n")
            for item in carriers:
                condition = (item.get("traits") or "Desconhecida").split(";")[0]
                f.write(f"- **{item.get('gene', '---')}**: {condition}\n")

        # Supplements
        f.write("\n\n---\n\n## Topicos para Discussao com Medico: Suplementos\n\n")
        f.write("*Estes NAO sao prescricoes. Sao topicos para levantar com um profissional ")
        f.write("de saude que pode avaliar seu quadro clinico completo, exames de sangue e ")
        f.write("interacoes medicamentosas.*\n\n")
        supplements = _build_supplement_list(findings_dict)
        if supplements:
            f.write("| Suplemento | Dose | Motivo |\n")
            f.write("|------------|------|--------|\n")
            for s in supplements:
                f.write(f"| {s['name']} | {s['dose']} | {s['reason']} |\n")
        else:
            f.write("Nenhum suplemento especifico indicado pelos sinais geneticos.\n")

        # Diet
        f.write("\n---\n\n## Topicos para Discussao com Medico: Alimentacao\n\n")
        f.write("*Padroes gerais sugeridos por sinais geneticos. Necessidades individuais variam ")
        f.write("conforme exames de sangue, medicamentos e contexto clinico.*\n\n")
        diet_recs = _build_diet_recs(findings_dict)
        for rec in diet_recs:
            f.write(f"- {rec}\n\n")
        if not diet_recs:
            f.write("Nenhum sinal alimentar especifico da genotipagem.\n")

        # Exercise
        f.write("\n---\n\n## Topicos para Discussao com Medico: Exercicio\n\n")
        exercise_recs = _build_exercise_recs(findings_dict)
        for rec in exercise_recs:
            f.write(f"- {rec}\n\n")
        if not exercise_recs:
            f.write("Nenhum sinal de exercicio especifico da genotipagem.\n")

        # Monitoring
        f.write("\n---\n\n## Exames para Discutir com Medico\n\n")
        f.write("*Estes sao exames que podem valer a pena solicitar na proxima consulta, ")
        f.write("com base em sinais geneticos. Seu medico decidira o que e apropriado.*\n\n")
        monitoring = _build_monitoring(findings_dict, disease_findings)
        if monitoring:
            f.write("| Exame | Frequencia Sugerida | Base Genetica |\n")
            f.write("|-------|---------------------|---------------|\n")
            for m in monitoring:
                f.write(f"| {m['test']} | {m['freq']} | {m['reason']} |\n")
        else:
            f.write("Rastreamento de saude padrao apropriado para a idade.\n")

        # Drug interactions summary
        f.write("\n---\n\n## Interacoes Droga-Gene (Para Revisao do Medico)\n\n")
        f.write("**NAO mude medicamentos com base nisto.** Estas correspondencias PharmGKB/CPIC ")
        f.write("sao projetadas para uso clinico com resultados de testes geneticos *validados*. ")
        f.write("Genotipagem de chip de consumo nao e suficiente para decisoes de prescricao. ")
        f.write("Compartilhe esta lista com seu medico para avaliacao.\n\n")
        level_1 = [x for x in health_results["pharmgkb_findings"] if x["level"] in ("1A", "1B")]
        if level_1:
            f.write("| Gene | Medicamentos | Seu Genotipo | Evidencia |\n")
            f.write("|------|--------------|--------------|----------|\n")
            for item in level_1:
                drugs = item["drugs"][:50] + "..." if len(item["drugs"]) > 50 else item["drugs"]
                f.write(f"| {item['gene']} | {drugs} | `{item['genotype']}` | {item['level']} |\n")
        else:
            f.write("Nenhuma interacao droga-gene de Nivel 1 (diretriz CPIC) detectada.\n")

        f.write(DISCLAIMER)


def _build_supplement_list(fd: dict, lang: str = "en") -> list:
    supps = []
    _t = _PROTOCOL_PT if lang == "pt" else _PROTOCOL_EN
    if "MTHFR" in fd and fd["MTHFR"]["magnitude"] >= 2:
        supps.append({"name": "Methylfolate (L-5-MTHF)", "dose": "400–800mcg", "reason": _t["mthfr_folate"]})
        supps.append({"name": "Methylcobalamin (B12)", "dose": "1000mcg sublingual", "reason": _t["b12_methylation"]})
    if "MTRR" in fd and fd["MTRR"]["magnitude"] >= 2 and not any("B12" in s["name"] for s in supps):
        supps.append({"name": "Methylcobalamin (B12)", "dose": "1000–5000mcg", "reason": _t["mtrr_b12"]})
    if "GC" in fd and fd["GC"].get("status") in ("low", "very_low"):
        supps.append({"name": _t["vit_d3"], "dose": "2000–5000 IU", "reason": _t["gc_vitd"]})
        supps.append({"name": _t["vit_k2"], "dose": "100–200mcg", "reason": _t["k2_synergy"]})
    if "FADS1" in fd and fd["FADS1"].get("status") == "low_conversion":
        supps.append({"name": _t["fish_oil"], "dose": "1–2g EPA+DHA", "reason": _t["fads1_conversion"]})
    if "COMT" in fd and fd["COMT"].get("status") == "slow":
        supps.append({"name": _t["magnesium"], "dose": "300–400mg", "reason": _t["comt_calm"]})
    if "PEMT" in fd:
        supps.append({"name": _t["choline"], "dose": "250–500mg", "reason": _t["pemt_choline"]})
    if "IL6" in fd and fd["IL6"].get("status") == "high":
        supps.append({"name": "Omega-3 (EPA/DHA)", "dose": "2–3g", "reason": _t["il6_omega"]})
    if "BCMO1" in fd and "reduced" in fd["BCMO1"].get("status", ""):
        supps.append({"name": _t["vit_a"], "dose": "2500–5000 IU", "reason": _t["bcmo1_conversion"]})
    return supps


def _build_diet_recs(fd: dict, lang: str = "en") -> list:
    recs = []
    _t = _PROTOCOL_PT if lang == "pt" else _PROTOCOL_EN
    if "APOA2" in fd and fd["APOA2"].get("status") == "sensitive":
        recs.append(_t["diet_sat_fat"])
    if "MTHFR" in fd and fd["MTHFR"]["magnitude"] >= 2:
        recs.append(_t["diet_folate"])
    if "IL6" in fd:
        recs.append(_t["diet_antiinflam"])
    if "MCM6/LCT" in fd and "intolerant" in fd["MCM6/LCT"].get("status", ""):
        recs.append(_t["diet_lactose"])
    if "HLA-DQA1" in fd:
        recs.append(_t["diet_celiac"])
    # Caffeine
    caffeine_flags = []
    if "CYP1A2" in fd and fd["CYP1A2"].get("status") in ("slow", "intermediate"):
        caffeine_flags.append(_t["caffeine_slow"])
    if "ADORA2A" in fd and fd["ADORA2A"].get("status") == "anxiety_prone":
        caffeine_flags.append(_t["caffeine_anxiety"])
    if "COMT" in fd and fd["COMT"].get("status") == "slow":
        caffeine_flags.append("COMT " + _t["caffeine_slow_comt"])
    if caffeine_flags:
        recs.append(f"**{_t['caffeine_title']}** ({', '.join(caffeine_flags)}): {_t['caffeine_advice']}")
    if "HFE" in fd:
        recs.append(_t["diet_iron"])
    if "ALDH2" in fd and "deficient" in fd["ALDH2"].get("status", ""):
        recs.append(_t["diet_alcohol"])
    return recs


def _build_exercise_recs(fd: dict, lang: str = "en") -> list:
    recs = []
    _t = _PROTOCOL_PT if lang == "pt" else _PROTOCOL_EN
    if "ACTN3" in fd:
        status = fd["ACTN3"].get("status", "")
        if status == "endurance":
            recs.append(_t["actn3_endurance"])
        elif status == "power":
            recs.append(_t["actn3_power"])
        else:
            recs.append(_t["actn3_mixed"])
    if "BDNF" in fd and fd["BDNF"]["magnitude"] >= 2:
        recs.append(_t["bdnf_exercise"])
    if "PPARGC1A" in fd and fd["PPARGC1A"]["magnitude"] >= 1:
        recs.append(_t["pgc1a_mito"])
    return recs


def _build_monitoring(fd: dict, disease_findings: dict, lang: str = "en") -> list:
    tests = []
    _t = _PROTOCOL_PT if lang == "pt" else _PROTOCOL_EN
    if "MTHFR" in fd and fd["MTHFR"]["magnitude"] >= 2:
        tests.append({"test": _t["test_homocysteine"], "freq": _t["freq_annual"], "reason": _t["reason_mthfr"]})
    if "MTRR" in fd and fd["MTRR"]["magnitude"] >= 2:
        tests.append({"test": "B12 + MMA", "freq": _t["freq_annual"], "reason": _t["reason_mtrr"]})
    if "GC" in fd:
        tests.append({"test": "25-OH Vitamin D", "freq": _t["freq_3m_annual"], "reason": _t["reason_gc"]})
    bp_genes = ["AGTR1", "ACE", "AGT", "GNB3"]
    if any(g in fd for g in bp_genes):
        tests.append({"test": _t["test_bp"], "freq": _t["freq_home"], "reason": _t["reason_bp"]})
    if "HFE" in fd:
        tests.append({"test": _t["test_ferritin"], "freq": _t["freq_1_2y"], "reason": _t["reason_hfe"]})
    if "TCF7L2" in fd and fd["TCF7L2"]["magnitude"] >= 2:
        tests.append({"test": _t["test_glucose"], "freq": _t["freq_annual"], "reason": _t["reason_tcf7l2"]})
    if "F5" in fd and fd["F5"]["magnitude"] >= 3:
        tests.append({"test": _t["test_clotting"], "freq": _t["freq_surgery"], "reason": "Factor V Leiden"})
    if "APOE" in fd and fd["APOE"]["magnitude"] >= 3:
        tests.append({"test": _t["test_lipid_cog"], "freq": _t["freq_annual"], "reason": "APOE e4"})

    if disease_findings:
        risk_traits = " ".join(f.get("traits", "").lower() for f in disease_findings.get("risk_factor", []))
        if "macular degeneration" in risk_traits:
            tests.append({"test": _t["test_ophth"], "freq": _t["freq_40"], "reason": _t["reason_amd"]})
    return tests


# ── Protocol translation dictionaries ────────────────────────────────────────

_PROTOCOL_EN = {
    # Supplements
    "mthfr_folate": "MTHFR variant reduces folic acid conversion",
    "b12_methylation": "Supports methylation cycle",
    "mtrr_b12": "MTRR impairs B12 recycling",
    "vit_d3": "Vitamin D3",
    "gc_vitd": "Genetically lower vitamin D binding protein",
    "vit_k2": "Vitamin K2 (MK-7)",
    "k2_synergy": "Synergistic with D3",
    "fish_oil": "Fish Oil (EPA/DHA)",
    "fads1_conversion": "Poor ALA conversion",
    "magnesium": "Magnesium Glycinate",
    "comt_calm": "Supports COMT, calming",
    "choline": "Choline / CDP-Choline",
    "pemt_choline": "PEMT variant increases choline need",
    "il6_omega": "Higher baseline IL-6",
    "vit_a": "Preformed Vitamin A",
    "bcmo1_conversion": "Poor beta-carotene conversion",

    # Diet
    "diet_sat_fat": "**Limit saturated fat (<7% calories)**: APOA2 variant links sat fat to weight gain. Prefer olive oil, nuts, avocado.",
    "diet_folate": "**Emphasize folate-rich foods**: Leafy greens, legumes, liver. Avoid excess folic acid from fortified foods.",
    "diet_antiinflam": "**Anti-inflammatory diet**: Omega-3 fish, colorful vegetables, minimize processed foods.",
    "diet_lactose": "**Lactose intolerance**: Fermented dairy (yogurt, aged cheese) usually tolerated. Lactase supplements available.",
    "diet_celiac": "**Celiac awareness (HLA-DQ2.5)**: No preventive gluten-free diet needed. If GI symptoms, test tTG-IgA while eating gluten.",
    "caffeine_slow": "slow metabolizer",
    "caffeine_anxiety": "anxiety-prone",
    "caffeine_slow_comt": "slow",
    "caffeine_title": "Caffeine caution",
    "caffeine_advice": "Morning only, consider green tea or L-theanine pairing.",
    "diet_iron": "**Iron awareness (HFE)**: Don't supplement iron unless confirmed deficient. Blood donation helps if ferritin is high.",
    "diet_alcohol": "**Alcohol caution (ALDH2)**: Increased cancer risk with alcohol consumption. Minimize or avoid.",

    # Exercise
    "actn3_endurance": "**ACTN3 endurance profile**: Genetics favor aerobic/endurance training. Can still build strength.",
    "actn3_power": "**ACTN3 power profile**: Genetics favor explosive/strength training.",
    "actn3_mixed": "**ACTN3 mixed profile**: Versatile — respond well to both power and endurance.",
    "bdnf_exercise": "**Exercise is essential for BDNF**: Your variant reduces activity-dependent neuroplasticity. Regular exercise is one of the strongest natural BDNF boosters.",
    "pgc1a_mito": "**Mitochondrial health (PGC-1a)**: Reduced variant — aerobic exercise particularly important for mitochondrial biogenesis.",

    # Monitoring
    "test_homocysteine": "Homocysteine",
    "test_bp": "Blood pressure",
    "test_ferritin": "Ferritin / iron panel",
    "test_glucose": "Fasting glucose / HbA1c",
    "test_clotting": "Clotting panel",
    "test_lipid_cog": "Lipid panel + cognitive baseline",
    "test_ophth": "Ophthalmology exam",
    "freq_annual": "Annually",
    "freq_3m_annual": "After 3 months, then annually",
    "freq_home": "Regular home monitoring",
    "freq_1_2y": "Every 1–2 years",
    "freq_surgery": "Before surgery/travel",
    "freq_40": "Annually after 40",
    "reason_mthfr": "MTHFR variant",
    "reason_mtrr": "MTRR variant",
    "reason_gc": "GC variant",
    "reason_bp": "Multiple BP variants",
    "reason_hfe": "HFE carrier",
    "reason_tcf7l2": "TCF7L2 diabetes risk",
    "reason_amd": "AMD risk variants",
}

_PROTOCOL_PT = {
    # Suplementos
    "mthfr_folate": "Variante MTHFR reduz conversao de acido folico",
    "b12_methylation": "Suporte ao ciclo de metilacao",
    "mtrr_b12": "MTRR prejudica reciclagem de B12",
    "vit_d3": "Vitamina D3",
    "gc_vitd": "Proteina de ligacao de vitamina D geneticamente mais baixa",
    "vit_k2": "Vitamina K2 (MK-7)",
    "k2_synergy": "Sinergico com D3",
    "fish_oil": "Oleo de Peixe (EPA/DHA)",
    "fads1_conversion": "Conversao deficiente de ALA",
    "magnesium": "Magnesio Glicinato",
    "comt_calm": "Suporte ao COMT, calmante",
    "choline": "Colina / CDP-Colina",
    "pemt_choline": "Variante PEMT aumenta necessidade de colina",
    "il6_omega": "IL-6 basal elevada",
    "vit_a": "Vitamina A Pre-formada",
    "bcmo1_conversion": "Conversao deficiente de beta-caroteno",

    # Alimentacao
    "diet_sat_fat": "**Limitar gordura saturada (<7% calorias)**: Variante APOA2 liga gordura saturada a ganho de peso. Prefira azeite, castanhas, abacate.",
    "diet_folate": "**Priorizar alimentos ricos em folato**: Folhas verdes escuras, leguminosas, figado. Evitar excesso de acido folico de alimentos fortificados.",
    "diet_antiinflam": "**Dieta anti-inflamatoria**: Peixes ricos em Omega-3, vegetais coloridos, minimizar ultraprocessados.",
    "diet_lactose": "**Intolerancia a lactose**: Laticinios fermentados (iogurte, queijos curados) geralmente sao tolerados. Enzima lactase disponivel em farmacias.",
    "diet_celiac": "**Atencao celiaca (HLA-DQ2.5)**: Nao e necessario dieta sem gluten preventiva. Se sintomas gastrointestinais, peca sorologia anti-transglutaminase (tTG-IgA) ENQUANTO come gluten.",
    "caffeine_slow": "metabolizador lento",
    "caffeine_anxiety": "propenso a ansiedade",
    "caffeine_slow_comt": "lento",
    "caffeine_title": "Cuidado com cafeina",
    "caffeine_advice": "Apenas pela manha, considere cha verde ou L-teanina junto.",
    "diet_iron": "**Cuidado com ferro (HFE)**: Nao suplemente ferro sem confirmacao de deficiencia. Doacao de sangue ajuda se ferritina alta.",
    "diet_alcohol": "**Cuidado com alcool (ALDH2)**: Risco aumentado de cancer com consumo de alcool. Minimize ou evite.",

    # Exercicio
    "actn3_endurance": "**ACTN3 perfil de resistencia**: Genetica favorece treino aerobico/resistencia. Ainda pode ganhar forca.",
    "actn3_power": "**ACTN3 perfil de potencia**: Genetica favorece treino explosivo/forca.",
    "actn3_mixed": "**ACTN3 perfil misto**: Versatil — responde bem tanto a potencia quanto resistencia.",
    "bdnf_exercise": "**Exercicio e essencial para BDNF**: Sua variante reduz neuroplasticidade. Exercicio regular e um dos estimuladores naturais mais potentes de BDNF.",
    "pgc1a_mito": "**Saude mitocondrial (PGC-1a)**: Variante reduzida — exercicio aerobico particularmente importante para biogenese mitocondrial.",

    # Monitoramento
    "test_homocysteine": "Homocisteina",
    "test_bp": "Pressao arterial",
    "test_ferritin": "Ferritina / painel de ferro",
    "test_glucose": "Glicemia de jejum / HbA1c",
    "test_clotting": "Painel de coagulacao",
    "test_lipid_cog": "Perfil lipidico + baseline cognitivo",
    "test_ophth": "Exame oftalmologico",
    "freq_annual": "Anualmente",
    "freq_3m_annual": "Apos 3 meses, depois anualmente",
    "freq_home": "Monitoramento domiciliar regular",
    "freq_1_2y": "A cada 1–2 anos",
    "freq_surgery": "Antes de cirurgia/viagem",
    "freq_40": "Anualmente apos 40 anos",
    "reason_mthfr": "Variante MTHFR",
    "reason_mtrr": "Variante MTRR",
    "reason_gc": "Variante GC",
    "reason_bp": "Multiplas variantes de PA",
    "reason_hfe": "Portador HFE",
    "reason_tcf7l2": "Risco de diabetes TCF7L2",
    "reason_amd": "Variantes de risco DMRI",
}
