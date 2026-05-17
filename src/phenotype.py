"""
Predicao de tracos fisicos baseada em SNPs — cor dos olhos, cabelo, pele.

Baseado no sistema IrisPlex/HIrisPlex (Walsh et al. 2011, 2013)
e literatura de genetica de pigmentacao.

AVISO: Predicoes probabilisticas, nao deterministicas.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# EYE COLOR PREDICTION
# ═══════════════════════════════════════════════════════════════════════════════

EYE_SNPS = {
    "rs12913832": {
        "gene": "HERC2/OCA2",
        "trait": "Determinante principal da cor dos olhos",
        "impact": "alto",
        "variants": {
            "GG": {"blue": 0.85, "green": 0.10, "brown": 0.05, "desc": "Forte predisposicao para olhos azuis"},
            "AG": {"blue": 0.20, "green": 0.25, "brown": 0.55, "desc": "Olhos castanhos ou verdes mais provaveis"},
            "GA": {"blue": 0.20, "green": 0.25, "brown": 0.55, "desc": "Olhos castanhos ou verdes mais provaveis"},
            "AA": {"blue": 0.01, "green": 0.10, "brown": 0.89, "desc": "Olhos castanhos muito provaveis"},
        },
    },
    "rs1800407": {
        "gene": "OCA2",
        "trait": "Modificador da cor dos olhos",
        "impact": "moderado",
        "variants": {
            "CC": {"blue": 0.0, "green": 0.0, "brown": 0.05, "desc": "Sem efeito modificador (referencia)"},
            "CT": {"blue": 0.10, "green": 0.15, "brown": -0.10, "desc": "Tendencia a clarear olhos castanhos para verdes"},
            "TC": {"blue": 0.10, "green": 0.15, "brown": -0.10, "desc": "Tendencia a clarear olhos"},
            "TT": {"blue": 0.20, "green": 0.10, "brown": -0.20, "desc": "Forte clareamento — pode tornar olhos verdes ou azuis"},
        },
    },
    "rs12896399": {
        "gene": "SLC24A4",
        "trait": "Olhos claros",
        "impact": "moderado",
        "variants": {
            "GG": {"blue": 0.0, "green": 0.0, "brown": 0.0, "desc": "Referencia"},
            "GT": {"blue": 0.05, "green": 0.05, "brown": -0.05, "desc": "Leve tendencia a olhos mais claros"},
            "TG": {"blue": 0.05, "green": 0.05, "brown": -0.05, "desc": "Leve tendencia a olhos mais claros"},
            "TT": {"blue": 0.10, "green": 0.05, "brown": -0.10, "desc": "Moderada tendencia a olhos claros"},
        },
    },
    "rs1393350": {
        "gene": "TYR",
        "trait": "Modificador de pigmentacao ocular",
        "impact": "baixo",
        "variants": {
            "GG": {"blue": 0.0, "green": 0.0, "brown": 0.0, "desc": "Referencia"},
            "GA": {"blue": 0.05, "green": 0.05, "brown": -0.05, "desc": "Leve clareamento"},
            "AG": {"blue": 0.05, "green": 0.05, "brown": -0.05, "desc": "Leve clareamento"},
            "AA": {"blue": 0.10, "green": 0.05, "brown": -0.10, "desc": "Clareamento moderado"},
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# HAIR COLOR PREDICTION
# ═══════════════════════════════════════════════════════════════════════════════

HAIR_SNPS = {
    "rs12821256": {
        "gene": "KITLG",
        "trait": "Cabelo loiro",
        "variants": {
            "TT": {"blond": 0.0, "red": 0.0, "brown": 0.0, "black": 0.0, "desc": "Referencia (sem efeito loiro)"},
            "TC": {"blond": 0.15, "red": 0.0, "brown": -0.05, "black": -0.05, "desc": "Tendencia a cabelo mais claro"},
            "CT": {"blond": 0.15, "red": 0.0, "brown": -0.05, "black": -0.05, "desc": "Tendencia a cabelo mais claro"},
            "CC": {"blond": 0.30, "red": 0.0, "brown": -0.10, "black": -0.15, "desc": "Forte tendencia a cabelo loiro"},
        },
    },
    "rs1805007": {
        "gene": "MC1R",
        "trait": "Cabelo ruivo (R151C)",
        "variants": {
            "CC": {"blond": 0.0, "red": 0.0, "brown": 0.0, "black": 0.0, "desc": "Referencia (sem efeito ruivo)"},
            "CT": {"blond": 0.0, "red": 0.30, "brown": -0.10, "black": -0.10, "desc": "Portador de ruivo — reflexos avermelhados possiveis"},
            "TC": {"blond": 0.0, "red": 0.30, "brown": -0.10, "black": -0.10, "desc": "Portador de ruivo"},
            "TT": {"blond": 0.0, "red": 0.70, "brown": -0.20, "black": -0.20, "desc": "Forte predisposicao a cabelo ruivo"},
        },
    },
    "rs1805008": {
        "gene": "MC1R",
        "trait": "Cabelo ruivo (R160W)",
        "variants": {
            "CC": {"blond": 0.0, "red": 0.0, "brown": 0.0, "black": 0.0, "desc": "Referencia"},
            "CT": {"blond": 0.0, "red": 0.20, "brown": -0.05, "black": -0.05, "desc": "Portador de ruivo — leve tendencia"},
            "TC": {"blond": 0.0, "red": 0.20, "brown": -0.05, "black": -0.05, "desc": "Portador de ruivo"},
            "TT": {"blond": 0.0, "red": 0.60, "brown": -0.15, "black": -0.20, "desc": "Forte predisposicao ruiva"},
        },
    },
    "rs2228479": {
        "gene": "MC1R",
        "trait": "Pigmentacao geral",
        "variants": {
            "GG": {"blond": 0.0, "red": 0.0, "brown": 0.0, "black": 0.0, "desc": "Pigmentacao normal"},
            "GA": {"blond": 0.0, "red": 0.05, "brown": -0.05, "black": -0.05, "desc": "Leve reducao de pigmento — cabelo levemente mais claro"},
            "AG": {"blond": 0.0, "red": 0.05, "brown": -0.05, "black": -0.05, "desc": "Leve reducao"},
            "AA": {"blond": 0.05, "red": 0.10, "brown": -0.10, "black": -0.10, "desc": "Pigmentacao reduzida — cabelo mais claro"},
        },
    },
    "rs12203592": {
        "gene": "IRF4",
        "trait": "Cabelo claro / sardas",
        "variants": {
            "CC": {"blond": 0.0, "red": 0.0, "brown": 0.0, "black": 0.0, "desc": "Referencia"},
            "CT": {"blond": 0.10, "red": 0.05, "brown": -0.05, "black": -0.05, "desc": "Tendencia a cabelo mais claro e sardas"},
            "TC": {"blond": 0.10, "red": 0.05, "brown": -0.05, "black": -0.05, "desc": "Tendencia a cabelo mais claro"},
            "TT": {"blond": 0.20, "red": 0.10, "brown": -0.10, "black": -0.10, "desc": "Cabelo claro e sardas provaveis"},
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# HAIR TEXTURE
# ═══════════════════════════════════════════════════════════════════════════════

TEXTURE_SNPS = {
    "rs3827760": {
        "gene": "EDAR",
        "trait": "Espessura do cabelo",
        "variants": {
            "CC": {"desc": "Cabelo de espessura padrao europeu/africano"},
            "CT": {"desc": "Cabelo intermediario — levemente mais grosso"},
            "TC": {"desc": "Cabelo intermediario — levemente mais grosso"},
            "TT": {"desc": "Cabelo mais grosso e liso (variante comum no leste asiatico)"},
            "AA": {"desc": "Cabelo de espessura padrao"},
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# FRECKLING
# ═══════════════════════════════════════════════════════════════════════════════

FRECKLE_SNPS = {
    "rs4911414": {
        "gene": "IRF4",
        "trait": "Sardas",
        "variants": {
            "TT": {"freckles": 0.0, "desc": "Baixa tendencia a sardas"},
            "TG": {"freckles": 0.15, "desc": "Moderada tendencia a sardas"},
            "GT": {"freckles": 0.15, "desc": "Moderada tendencia a sardas"},
            "GG": {"freckles": 0.30, "desc": "Tendencia aumentada a sardas"},
        },
    },
    "rs1805009": {
        "gene": "MC1R",
        "trait": "Sardas / pele sensivel ao sol",
        "variants": {
            "GG": {"freckles": 0.0, "desc": "Referencia"},
            "GC": {"freckles": 0.20, "desc": "Tendencia a sardas e pele clara"},
            "CG": {"freckles": 0.20, "desc": "Tendencia a sardas"},
            "CC": {"freckles": 0.40, "desc": "Forte tendencia a sardas e sensibilidade solar"},
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# BALDNESS (Androgenetic Alopecia)
# ═══════════════════════════════════════════════════════════════════════════════

BALDNESS_SNPS = {
    "rs2180439": {
        "gene": "20p11",
        "trait": "Locus principal de calvicie masculina",
        "impact": "alto",
        "variants": {
            "CC": {"risk": 0.40, "desc": "Alelo de risco homozigoto — risco significativamente aumentado de calvicie androgenica."},
            "CT": {"risk": 0.20, "desc": "Portador de uma copia do alelo de risco — risco moderadamente aumentado."},
            "TC": {"risk": 0.20, "desc": "Portador de uma copia — risco moderado."},
            "TT": {"risk": 0.0, "desc": "Sem alelo de risco neste locus — protetor."},
        },
    },
    "rs6152": {
        "gene": "AR (Receptor de Androgeno, cromossomo X)",
        "trait": "Sensibilidade a DHT — herdado da mae",
        "impact": "alto",
        "variants": {
            "GG": {"risk": 0.0, "desc": "Receptor de androgeno padrao — sem aumento de risco por esta via."},
            "GA": {"risk": 0.25, "desc": "Sensibilidade aumentada a DHT (dihidrotestosterona). Risco aumentado de calvicie. Este gene e herdado da MAE."},
            "AG": {"risk": 0.25, "desc": "Sensibilidade aumentada a DHT, herdada da mae."},
            "AA": {"risk": 0.35, "desc": "Alta sensibilidade a DHT — risco substancial de calvicie. Herdado da mae. Finasterida pode ser eficaz se indicada por dermatologista."},
        },
    },
    "rs929626": {
        "gene": "EBF1 (20p11)",
        "trait": "Locus adicional de calvicie (GWAS)",
        "impact": "moderado",
        "variants": {
            "AA": {"risk": 0.15, "desc": "Alelo de risco homozigoto — contribuicao adicional ao risco de calvicie."},
            "AG": {"risk": 0.08, "desc": "Portador — contribuicao leve ao risco."},
            "GA": {"risk": 0.08, "desc": "Portador — contribuicao leve."},
            "GG": {"risk": 0.0, "desc": "Sem alelo de risco neste locus."},
        },
    },
    "rs1385699": {
        "gene": "HDAC9 (7p21)",
        "trait": "Locus de calvicie precoce",
        "impact": "moderado",
        "variants": {
            "TT": {"risk": 0.15, "desc": "Risco aumentado de inicio precoce da calvicie."},
            "TC": {"risk": 0.08, "desc": "Risco leve de inicio mais cedo."},
            "CT": {"risk": 0.08, "desc": "Risco leve de inicio mais cedo."},
            "CC": {"risk": 0.0, "desc": "Sem aumento de risco de calvicie precoce por este locus."},
        },
    },
}


# Color labels and hex codes for display
EYE_COLORS = {
    "blue": {"pt": "Azul", "en": "Blue", "hex": "#4A90D9", "emoji": "\U0001f535"},
    "green": {"pt": "Verde", "en": "Green", "hex": "#6BAF5B", "emoji": "\U0001f7e2"},
    "brown": {"pt": "Castanho", "en": "Brown", "hex": "#8B4513", "emoji": "\U0001f7e4"},
}

HAIR_COLORS = {
    "black": {"pt": "Preto", "en": "Black", "hex": "#1a1a1a", "emoji": "\u26ab"},
    "brown": {"pt": "Castanho", "en": "Brown", "hex": "#6B3A2A", "emoji": "\U0001f7e4"},
    "blond": {"pt": "Loiro", "en": "Blond", "hex": "#DAA520", "emoji": "\U0001f7e1"},
    "red": {"pt": "Ruivo", "en": "Red", "hex": "#CC4422", "emoji": "\U0001f534"},
}


def analyze_phenotype(genome_by_rsid: dict) -> dict:
    """Predict physical traits from SNPs.

    Returns {
        "eye_color": {"predictions": {blue: %, green: %, brown: %}, "details": [...]},
        "hair_color": {"predictions": {black: %, brown: %, blond: %, red: %}, "details": [...]},
        "hair_texture": {"description": str, "details": [...]},
        "freckling": {"tendency": str, "details": [...]},
        "markers_found": int,
        "markers_total": int,
    }
    """
    # Eye color
    eye_probs = {"blue": 0.10, "green": 0.15, "brown": 0.75}  # population priors
    eye_details = []
    for rsid, info in EYE_SNPS.items():
        if rsid not in genome_by_rsid:
            continue
        genotype = genome_by_rsid[rsid]["genotype"]
        variant = info["variants"].get(genotype)
        if not variant and len(genotype) == 2:
            variant = info["variants"].get(genotype[::-1])
        if not variant:
            continue
        for color in ("blue", "green", "brown"):
            eye_probs[color] += variant.get(color, 0)
        eye_details.append({
            "rsid": rsid, "gene": info["gene"], "genotype": genotype,
            "trait": info["trait"], "impact": info["impact"], "desc": variant["desc"],
        })

    # Normalize eye probs
    eye_probs = {k: max(0, v) for k, v in eye_probs.items()}
    total = sum(eye_probs.values()) or 1
    eye_probs = {k: round(100 * v / total, 1) for k, v in eye_probs.items()}

    # Hair color
    hair_probs = {"black": 0.30, "brown": 0.40, "blond": 0.15, "red": 0.05}  # priors
    hair_details = []
    for rsid, info in HAIR_SNPS.items():
        if rsid not in genome_by_rsid:
            continue
        genotype = genome_by_rsid[rsid]["genotype"]
        variant = info["variants"].get(genotype)
        if not variant and len(genotype) == 2:
            variant = info["variants"].get(genotype[::-1])
        if not variant:
            continue
        for color in ("black", "brown", "blond", "red"):
            hair_probs[color] += variant.get(color, 0)
        hair_details.append({
            "rsid": rsid, "gene": info["gene"], "genotype": genotype,
            "trait": info["trait"], "desc": variant["desc"],
        })

    hair_probs = {k: max(0, v) for k, v in hair_probs.items()}
    total = sum(hair_probs.values()) or 1
    hair_probs = {k: round(100 * v / total, 1) for k, v in hair_probs.items()}

    # Hair texture
    texture_desc = "Informacao nao disponivel"
    texture_details = []
    for rsid, info in TEXTURE_SNPS.items():
        if rsid not in genome_by_rsid:
            continue
        genotype = genome_by_rsid[rsid]["genotype"]
        variant = info["variants"].get(genotype)
        if not variant and len(genotype) == 2:
            variant = info["variants"].get(genotype[::-1])
        if variant:
            texture_desc = variant["desc"]
            texture_details.append({
                "rsid": rsid, "gene": info["gene"], "genotype": genotype, "desc": variant["desc"],
            })

    # Freckling
    freckle_score = 0
    freckle_details = []
    for rsid, info in FRECKLE_SNPS.items():
        if rsid not in genome_by_rsid:
            continue
        genotype = genome_by_rsid[rsid]["genotype"]
        variant = info["variants"].get(genotype)
        if not variant and len(genotype) == 2:
            variant = info["variants"].get(genotype[::-1])
        if variant:
            freckle_score += variant.get("freckles", 0)
            freckle_details.append({
                "rsid": rsid, "gene": info["gene"], "genotype": genotype, "desc": variant["desc"],
            })

    if freckle_score >= 0.3:
        freckle_tendency = "Alta tendencia a sardas"
    elif freckle_score >= 0.15:
        freckle_tendency = "Moderada tendencia a sardas"
    else:
        freckle_tendency = "Baixa tendencia a sardas"

    # Baldness risk
    baldness_score = 0
    baldness_details = []
    for rsid, info in BALDNESS_SNPS.items():
        if rsid not in genome_by_rsid:
            continue
        genotype = genome_by_rsid[rsid]["genotype"]
        variant = info["variants"].get(genotype)
        if not variant and len(genotype) == 2:
            variant = info["variants"].get(genotype[::-1])
        if variant:
            baldness_score += variant.get("risk", 0)
            baldness_details.append({
                "rsid": rsid, "gene": info["gene"], "genotype": genotype,
                "trait": info["trait"], "impact": info["impact"], "desc": variant["desc"],
            })

    if baldness_score >= 0.60:
        baldness_risk = "Alto risco de calvicie androgenica"
        baldness_pct = min(95, round(30 + baldness_score * 80))
    elif baldness_score >= 0.30:
        baldness_risk = "Risco moderado de calvicie androgenica"
        baldness_pct = round(20 + baldness_score * 60)
    elif baldness_score > 0:
        baldness_risk = "Risco leve de calvicie androgenica"
        baldness_pct = round(10 + baldness_score * 40)
    else:
        baldness_risk = "Risco baixo de calvicie androgenica (nos loci analisados)"
        baldness_pct = 15  # baseline population risk

    # Note about X-linked AR gene
    ar_note = ""
    ar_found = any(d["rsid"] == "rs6152" for d in baldness_details)
    if ar_found:
        ar_note = "O gene AR (receptor de androgeno) esta no cromossomo X — voce herdou essa variante da sua MAE. Por isso, olhar para o avo materno e mais informativo que o pai."

    markers_found = len(eye_details) + len(hair_details) + len(texture_details) + len(freckle_details) + len(baldness_details)
    markers_total = len(EYE_SNPS) + len(HAIR_SNPS) + len(TEXTURE_SNPS) + len(FRECKLE_SNPS) + len(BALDNESS_SNPS)

    return {
        "eye_color": {"predictions": eye_probs, "details": eye_details},
        "hair_color": {"predictions": hair_probs, "details": hair_details},
        "hair_texture": {"description": texture_desc, "details": texture_details},
        "freckling": {"tendency": freckle_tendency, "score": round(freckle_score, 2), "details": freckle_details},
        "baldness": {
            "risk": baldness_risk,
            "risk_pct": baldness_pct,
            "score": round(baldness_score, 2),
            "ar_note": ar_note,
            "details": baldness_details,
        },
        "markers_found": markers_found,
        "markers_total": markers_total,
        "eye_colors_meta": EYE_COLORS,
        "hair_colors_meta": HAIR_COLORS,
    }
