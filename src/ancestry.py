"""
Estimativa de ancestralidade continental baseada em AIMs
(Ancestry Informative Markers).

Usa marcadores com frequencias alelicas bem documentadas entre
populacoes continentais (1000 Genomes Project, ALFRED database).

AVISO: Estimativa grosseira baseada em dezenas de marcadores.
Empresas como Genera usam milhares de marcadores + paineis
de referencia proprietarios para obter sub-regioes.
"""
from src.i18n import Lang
import math

# ═══════════════════════════════════════════════════════════════════════════════
# AIM Panel — frequencias alélicas por populacao continental
# Fonte: 1000 Genomes Project, gnomAD, ALFRED
#
# Para cada SNP: {genotipo: {pop: frequencia_do_genotipo}}
# EUR = Europeu, AFR = Africano, AMR = Amerindio, EAS = Leste Asiatico
# ═══════════════════════════════════════════════════════════════════════════════

AIMS = {
    # ── Pigmentacao (altamente informativos) ──
    "rs12913832": {
        "gene": "HERC2/OCA2", "trait": "Cor dos olhos", "trait_en": "Eye color",
        "genotypes": {
            "GG": {"EUR": 0.79, "AFR": 0.01, "AMR": 0.12, "EAS": 0.00},
            "AG": {"EUR": 0.18, "AFR": 0.03, "AMR": 0.22, "EAS": 0.00},
            "GA": {"EUR": 0.18, "AFR": 0.03, "AMR": 0.22, "EAS": 0.00},
            "AA": {"EUR": 0.03, "AFR": 0.96, "AMR": 0.66, "EAS": 1.00},
        },
    },
    "rs1426654": {
        "gene": "SLC24A5", "trait": "Pigmentacao da pele", "trait_en": "Skin pigmentation",
        "genotypes": {
            "AA": {"EUR": 0.99, "AFR": 0.02, "AMR": 0.50, "EAS": 0.00},
            "AG": {"EUR": 0.01, "AFR": 0.08, "AMR": 0.35, "EAS": 0.02},
            "GA": {"EUR": 0.01, "AFR": 0.08, "AMR": 0.35, "EAS": 0.02},
            "GG": {"EUR": 0.00, "AFR": 0.90, "AMR": 0.15, "EAS": 0.98},
        },
    },
    "rs16891982": {
        "gene": "SLC45A2", "trait": "Pigmentacao da pele", "trait_en": "Skin pigmentation",
        "genotypes": {
            "GG": {"EUR": 0.87, "AFR": 0.01, "AMR": 0.35, "EAS": 0.00},
            "GC": {"EUR": 0.12, "AFR": 0.04, "AMR": 0.30, "EAS": 0.02},
            "CG": {"EUR": 0.12, "AFR": 0.04, "AMR": 0.30, "EAS": 0.02},
            "CC": {"EUR": 0.01, "AFR": 0.95, "AMR": 0.35, "EAS": 0.98},
        },
    },
    "rs1042602": {
        "gene": "TYR", "trait": "Pigmentacao", "trait_en": "Pigmentation",
        "genotypes": {
            "CC": {"EUR": 0.60, "AFR": 0.98, "AMR": 0.85, "EAS": 0.99},
            "CA": {"EUR": 0.35, "AFR": 0.02, "AMR": 0.13, "EAS": 0.01},
            "AC": {"EUR": 0.35, "AFR": 0.02, "AMR": 0.13, "EAS": 0.01},
            "AA": {"EUR": 0.05, "AFR": 0.00, "AMR": 0.02, "EAS": 0.00},
        },
    },

    # ── Marcadores Duffy / Sangue (muito informativos EUR vs AFR) ──
    "rs2814778": {
        "gene": "ACKR1/Duffy", "trait": "Grupo sanguineo Duffy", "trait_en": "Duffy blood group",
        "genotypes": {
            "TT": {"EUR": 0.99, "AFR": 0.01, "AMR": 0.70, "EAS": 0.99},
            "TC": {"EUR": 0.01, "AFR": 0.15, "AMR": 0.20, "EAS": 0.01},
            "CT": {"EUR": 0.01, "AFR": 0.15, "AMR": 0.20, "EAS": 0.01},
            "CC": {"EUR": 0.00, "AFR": 0.84, "AMR": 0.10, "EAS": 0.00},
        },
    },

    # ── Lactase / Metabolismo (informativo EUR) ──
    "rs4988235": {
        "gene": "MCM6/LCT", "trait": "Persistencia da lactase", "trait_en": "Lactase persistence",
        "genotypes": {
            "TT": {"EUR": 0.40, "AFR": 0.05, "AMR": 0.15, "EAS": 0.01},
            "TC": {"EUR": 0.42, "AFR": 0.10, "AMR": 0.30, "EAS": 0.02},
            "CT": {"EUR": 0.42, "AFR": 0.10, "AMR": 0.30, "EAS": 0.02},
            "CC": {"EUR": 0.18, "AFR": 0.85, "AMR": 0.55, "EAS": 0.97},
            "AA": {"EUR": 0.18, "AFR": 0.85, "AMR": 0.55, "EAS": 0.97},
        },
    },

    # ── EDAR (muito informativo para EAS) ──
    "rs3827760": {
        "gene": "EDAR", "trait": "Morfologia do cabelo", "trait_en": "Hair morphology",
        "genotypes": {
            "CC": {"EUR": 0.93, "AFR": 0.99, "AMR": 0.15, "EAS": 0.07},
            "CT": {"EUR": 0.07, "AFR": 0.01, "AMR": 0.25, "EAS": 0.20},
            "TC": {"EUR": 0.07, "AFR": 0.01, "AMR": 0.25, "EAS": 0.20},
            "TT": {"EUR": 0.00, "AFR": 0.00, "AMR": 0.60, "EAS": 0.73},
            "AA": {"EUR": 0.93, "AFR": 0.99, "AMR": 0.15, "EAS": 0.07},
        },
    },

    # ── Alcool (informativo para EAS) ──
    "rs671": {
        "gene": "ALDH2", "trait": "Metabolismo do acetaldeido", "trait_en": "Acetaldehyde metabolism",
        "genotypes": {
            "GG": {"EUR": 0.99, "AFR": 0.99, "AMR": 0.98, "EAS": 0.70},
            "GA": {"EUR": 0.01, "AFR": 0.01, "AMR": 0.02, "EAS": 0.25},
            "AG": {"EUR": 0.01, "AFR": 0.01, "AMR": 0.02, "EAS": 0.25},
            "AA": {"EUR": 0.00, "AFR": 0.00, "AMR": 0.00, "EAS": 0.05},
        },
    },
    "rs1229984": {
        "gene": "ADH1B", "trait": "Metabolismo do alcool", "trait_en": "Alcohol metabolism",
        "genotypes": {
            "CC": {"EUR": 0.90, "AFR": 0.75, "AMR": 0.60, "EAS": 0.25},
            "CT": {"EUR": 0.09, "AFR": 0.20, "AMR": 0.30, "EAS": 0.45},
            "TC": {"EUR": 0.09, "AFR": 0.20, "AMR": 0.30, "EAS": 0.45},
            "TT": {"EUR": 0.01, "AFR": 0.05, "AMR": 0.10, "EAS": 0.30},
        },
    },

    # ── Dopamina / Neurotransmissores ──
    "rs1079597": {
        "gene": "DRD2", "trait": "Receptor de dopamina", "trait_en": "Dopamine receptor",
        "genotypes": {
            "CC": {"EUR": 0.82, "AFR": 0.55, "AMR": 0.65, "EAS": 0.45},
            "CT": {"EUR": 0.16, "AFR": 0.35, "AMR": 0.30, "EAS": 0.40},
            "TC": {"EUR": 0.16, "AFR": 0.35, "AMR": 0.30, "EAS": 0.40},
            "TT": {"EUR": 0.02, "AFR": 0.10, "AMR": 0.05, "EAS": 0.15},
        },
    },

    # ── Marcadores adicionais ──
    "rs1800414": {
        "gene": "OCA2", "trait": "Pigmentacao (EAS specific)", "trait_en": "Pigmentation (EAS specific)",
        "genotypes": {
            "CC": {"EUR": 0.99, "AFR": 0.99, "AMR": 0.90, "EAS": 0.40},
            "CT": {"EUR": 0.01, "AFR": 0.01, "AMR": 0.08, "EAS": 0.40},
            "TC": {"EUR": 0.01, "AFR": 0.01, "AMR": 0.08, "EAS": 0.40},
            "TT": {"EUR": 0.00, "AFR": 0.00, "AMR": 0.02, "EAS": 0.20},
        },
    },
    "rs1393350": {
        "gene": "TYR", "trait": "Pigmentacao / melanina", "trait_en": "Pigmentation / melanin",
        "genotypes": {
            "GG": {"EUR": 0.65, "AFR": 0.98, "AMR": 0.80, "EAS": 0.98},
            "GA": {"EUR": 0.30, "AFR": 0.02, "AMR": 0.18, "EAS": 0.02},
            "AG": {"EUR": 0.30, "AFR": 0.02, "AMR": 0.18, "EAS": 0.02},
            "AA": {"EUR": 0.05, "AFR": 0.00, "AMR": 0.02, "EAS": 0.00},
        },
    },
    "rs4959270": {
        "gene": "AIM-CONT", "trait": "Marcador continental", "trait_en": "Continental marker",
        "genotypes": {
            "CC": {"EUR": 0.45, "AFR": 0.20, "AMR": 0.55, "EAS": 0.70},
            "CA": {"EUR": 0.40, "AFR": 0.45, "AMR": 0.35, "EAS": 0.25},
            "AC": {"EUR": 0.40, "AFR": 0.45, "AMR": 0.35, "EAS": 0.25},
            "AA": {"EUR": 0.15, "AFR": 0.35, "AMR": 0.10, "EAS": 0.05},
        },
    },
    "rs1805007": {
        "gene": "MC1R", "trait": "Cabelo ruivo / pele clara", "trait_en": "Red hair / fair skin",
        "genotypes": {
            "CC": {"EUR": 0.90, "AFR": 0.99, "AMR": 0.95, "EAS": 0.99},
            "CT": {"EUR": 0.09, "AFR": 0.01, "AMR": 0.04, "EAS": 0.01},
            "TC": {"EUR": 0.09, "AFR": 0.01, "AMR": 0.04, "EAS": 0.01},
            "TT": {"EUR": 0.01, "AFR": 0.00, "AMR": 0.01, "EAS": 0.00},
        },
    },
    "rs1805008": {
        "gene": "MC1R", "trait": "Pigmentacao (EUR marker)", "trait_en": "Pigmentation (EUR marker)",
        "genotypes": {
            "CC": {"EUR": 0.88, "AFR": 0.99, "AMR": 0.96, "EAS": 0.99},
            "CT": {"EUR": 0.11, "AFR": 0.01, "AMR": 0.04, "EAS": 0.01},
            "TC": {"EUR": 0.11, "AFR": 0.01, "AMR": 0.04, "EAS": 0.01},
            "TT": {"EUR": 0.01, "AFR": 0.00, "AMR": 0.00, "EAS": 0.00},
        },
    },
    "rs1408799": {
        "gene": "TYRP1", "trait": "Pigmentacao", "trait_en": "Pigmentation",
        "genotypes": {
            "CC": {"EUR": 0.30, "AFR": 0.70, "AMR": 0.55, "EAS": 0.80},
            "CT": {"EUR": 0.48, "AFR": 0.25, "AMR": 0.35, "EAS": 0.18},
            "TC": {"EUR": 0.48, "AFR": 0.25, "AMR": 0.35, "EAS": 0.18},
            "TT": {"EUR": 0.22, "AFR": 0.05, "AMR": 0.10, "EAS": 0.02},
        },
    },
    "rs12821256": {
        "gene": "KITLG", "trait": "Cor do cabelo (loiro)", "trait_en": "Hair color (blond)",
        "genotypes": {
            "TT": {"EUR": 0.85, "AFR": 0.99, "AMR": 0.92, "EAS": 0.99},
            "TC": {"EUR": 0.14, "AFR": 0.01, "AMR": 0.07, "EAS": 0.01},
            "CT": {"EUR": 0.14, "AFR": 0.01, "AMR": 0.07, "EAS": 0.01},
            "CC": {"EUR": 0.01, "AFR": 0.00, "AMR": 0.01, "EAS": 0.00},
        },
    },
    "rs260690": {
        "gene": "AIM-CONT", "trait": "Marcador continental", "trait_en": "Continental marker",
        "genotypes": {
            "CC": {"EUR": 0.60, "AFR": 0.30, "AMR": 0.50, "EAS": 0.45},
            "CT": {"EUR": 0.32, "AFR": 0.48, "AMR": 0.38, "EAS": 0.40},
            "TC": {"EUR": 0.32, "AFR": 0.48, "AMR": 0.38, "EAS": 0.40},
            "TT": {"EUR": 0.08, "AFR": 0.22, "AMR": 0.12, "EAS": 0.15},
        },
    },
    "rs1344870": {
        "gene": "AIM-CONT", "trait": "Marcador continental", "trait_en": "Continental marker",
        "genotypes": {
            "TT": {"EUR": 0.50, "AFR": 0.25, "AMR": 0.60, "EAS": 0.75},
            "TC": {"EUR": 0.40, "AFR": 0.45, "AMR": 0.30, "EAS": 0.22},
            "CT": {"EUR": 0.40, "AFR": 0.45, "AMR": 0.30, "EAS": 0.22},
            "CC": {"EUR": 0.10, "AFR": 0.30, "AMR": 0.10, "EAS": 0.03},
        },
    },
    "rs10497191": {
        "gene": "AIM-CONT", "trait": "Marcador continental", "trait_en": "Continental marker",
        "genotypes": {
            "TT": {"EUR": 0.15, "AFR": 0.55, "AMR": 0.30, "EAS": 0.10},
            "TC": {"EUR": 0.45, "AFR": 0.38, "AMR": 0.45, "EAS": 0.35},
            "CT": {"EUR": 0.45, "AFR": 0.38, "AMR": 0.45, "EAS": 0.35},
            "CC": {"EUR": 0.40, "AFR": 0.07, "AMR": 0.25, "EAS": 0.55},
        },
    },
    "rs4471745": {
        "gene": "AIM-CONT", "trait": "Marcador continental", "trait_en": "Continental marker",
        "genotypes": {
            "AA": {"EUR": 0.35, "AFR": 0.70, "AMR": 0.45, "EAS": 0.20},
            "AG": {"EUR": 0.45, "AFR": 0.25, "AMR": 0.40, "EAS": 0.45},
            "GA": {"EUR": 0.45, "AFR": 0.25, "AMR": 0.40, "EAS": 0.45},
            "GG": {"EUR": 0.20, "AFR": 0.05, "AMR": 0.15, "EAS": 0.35},
        },
    },
    "rs772262": {
        "gene": "AIM-CONT", "trait": "Marcador continental", "trait_en": "Continental marker",
        "genotypes": {
            "AA": {"EUR": 0.55, "AFR": 0.20, "AMR": 0.40, "EAS": 0.65},
            "AG": {"EUR": 0.37, "AFR": 0.45, "AMR": 0.42, "EAS": 0.30},
            "GA": {"EUR": 0.37, "AFR": 0.45, "AMR": 0.42, "EAS": 0.30},
            "GG": {"EUR": 0.08, "AFR": 0.35, "AMR": 0.18, "EAS": 0.05},
        },
    },
}

POP_LABELS = {
    "EUR": "Europeu",
    "AFR": "Africano",
    "AMR": "Amerindio",
    "EAS": "Leste Asiatico",
}

POP_LABELS_EN = {
    "EUR": "European",
    "AFR": "African",
    "AMR": "Amerindian",
    "EAS": "East Asian",
}

POP_COLORS = {
    "EUR": "#D12E26",
    "AFR": "#77bc31",
    "AMR": "#EB6D3B",
    "EAS": "#4A90D9",
}

# Countries per continental group (for map coloring)
POP_COUNTRIES = {
    "EUR": [
        "Portugal", "Spain", "France", "Germany", "United Kingdom", "Ireland",
        "Italy", "Netherlands", "Belgium", "Switzerland", "Austria", "Poland",
        "Czech Republic", "Slovakia", "Hungary", "Romania", "Bulgaria", "Greece",
        "Croatia", "Serbia", "Sweden", "Norway", "Finland", "Denmark", "Iceland",
        "Russia", "Ukraine", "Belarus", "Lithuania", "Latvia", "Estonia",
    ],
    "AFR": [
        "Nigeria", "Ghana", "Cameroon", "Congo", "Angola", "Mozambique",
        "Kenya", "Tanzania", "Ethiopia", "South Africa", "Senegal", "Mali",
        "Guinea", "Sierra Leone", "Liberia", "Ivory Coast", "Burkina Faso",
        "Niger", "Chad", "Sudan", "Uganda", "Rwanda", "Burundi",
        "Dem. Rep. Congo", "Zambia", "Zimbabwe", "Malawi", "Madagascar",
        "Togo", "Benin", "Gabon", "Eq. Guinea",
    ],
    "AMR": [
        "Mexico", "Guatemala", "Honduras", "El Salvador", "Nicaragua",
        "Costa Rica", "Panama", "Colombia", "Venezuela", "Ecuador",
        "Peru", "Bolivia", "Chile", "Argentina", "Paraguay", "Uruguay",
        "Brazil",
    ],
    "EAS": [
        "China", "Japan", "South Korea", "North Korea", "Mongolia",
        "Vietnam", "Thailand", "Myanmar", "Laos", "Cambodia",
        "Philippines", "Malaysia", "Indonesia", "Taiwan",
    ],
}


def analyze_ancestry(genome_by_rsid: dict, lang: Lang = "en") -> dict:
    """Estimate continental ancestry from AIMs.

    Returns {
        "percentages": {"EUR": 70.0, "AFR": 22.0, ...},
        "markers_used": 15,
        "markers_total": 20,
        "marker_details": [{rsid, gene, trait, genotype, freqs}, ...],
        "confidence": "low" | "moderate" | "good",
    }
    """
    pops = ["EUR", "AFR", "AMR", "EAS"]
    log_likelihoods = {p: 0.0 for p in pops}
    markers_used = 0
    marker_details = []
    is_en = lang == "en"
    trait_key = "trait_en" if is_en else "trait"
    labels = POP_LABELS_EN if is_en else POP_LABELS

    for rsid, info in AIMS.items():
        if rsid not in genome_by_rsid:
            continue

        genotype = genome_by_rsid[rsid]["genotype"]
        freqs = info["genotypes"].get(genotype)
        if not freqs and len(genotype) == 2:
            freqs = info["genotypes"].get(genotype[::-1])
        if not freqs:
            continue

        markers_used += 1

        # Accumulate log-likelihood
        for pop in pops:
            freq = max(freqs.get(pop, 0.001), 0.001)
            log_likelihoods[pop] += math.log(freq)

        marker_details.append({
            "rsid": rsid,
            "gene": info["gene"],
            "trait": info.get(trait_key, info["trait"]),
            "genotype": genotype,
            "freqs": {p: round(freqs.get(p, 0), 3) for p in pops},
        })

    # Convert log-likelihoods to percentages
    if markers_used == 0:
        return {
            "percentages": {p: 25.0 for p in pops},
            "markers_used": 0,
            "markers_total": len(AIMS),
            "marker_details": [],
            "confidence": "none",
            "labels": labels,
            "colors": POP_COLORS,
            "conclusions": [],
        }

    # Normalize via softmax
    max_ll = max(log_likelihoods.values())
    probs = {p: math.exp(ll - max_ll) for p, ll in log_likelihoods.items()}
    total = sum(probs.values())
    percentages = {p: round(100 * v / total, 1) for p, v in probs.items()}

    # Confidence based on number of markers
    if markers_used >= 15:
        confidence = "good"
    elif markers_used >= 8:
        confidence = "moderate"
    else:
        confidence = "low"

    # Build human-readable conclusions
    conclusions = _build_ancestry_conclusions(percentages, markers_used, confidence, lang=lang)

    return {
        "percentages": percentages,
        "markers_used": markers_used,
        "markers_total": len(AIMS),
        "marker_details": sorted(marker_details, key=lambda x: x["rsid"]),
        "confidence": confidence,
        "conclusions": conclusions,
        "labels": labels,
        "colors": POP_COLORS,
    }


def _build_ancestry_conclusions(pcts: dict, markers: int, confidence: str, lang: Lang = "en") -> list:
    """Build human-friendly ancestry conclusions."""
    conclusions = []
    is_en = lang == "en"

    # Sort by percentage descending
    sorted_pops = sorted(pcts.items(), key=lambda x: -x[1])
    primary = sorted_pops[0]
    secondary = sorted_pops[1] if len(sorted_pops) > 1 else None

    if is_en:
        pop_names = {
            "EUR": "European", "AFR": "African",
            "AMR": "Amerindian (Indigenous American)",
            "EAS": "East Asian",
        }
        pop_regions = {
            "EUR": "Europe (Portugal, Spain, Italy, France, Germany and other European countries)",
            "AFR": "Africa (West, Central and East Africa)",
            "AMR": "the Americas (pre-Columbian Indigenous populations of South, Central and North America)",
            "EAS": "East Asia (China, Japan, Korea and Southeast Asia)",
        }
    else:
        pop_names = {
            "EUR": "europeia", "AFR": "africana",
            "AMR": "amerindia (indigena das Americas)",
            "EAS": "do leste asiatico",
        }
        pop_regions = {
            "EUR": "Europa (Portugal, Espanha, Italia, Franca, Alemanha e outros paises europeus)",
            "AFR": "Africa (Africa Ocidental, Central e Oriental)",
            "AMR": "Americas (populacoes indigenas pre-colombianas da America do Sul, Central e Norte)",
            "EAS": "Leste Asiatico (China, Japao, Coreia e sudeste asiatico)",
        }

    p_name = pop_names.get(primary[0], primary[0])
    p_pct = primary[1]

    if is_en:
        if p_pct >= 70:
            conclusions.append(
                f"Your genetic composition shows predominantly {p_name} ancestry "
                f"({p_pct}%). This means most of your ancestors likely came from "
                f"{pop_regions.get(primary[0], 'associated regions')}."
            )
        elif p_pct >= 40:
            conclusions.append(
                f"Your genetic composition shows significant admixture, with the "
                f"largest contribution being {p_name} ({p_pct}%). "
                f"This reflects ancestors from {pop_regions.get(primary[0], '')}."
            )
        else:
            conclusions.append(
                f"Your genetic composition is highly admixed, with no strongly "
                f"predominant ancestry. The largest contribution is {p_name} ({p_pct}%)."
            )

        if secondary and secondary[1] >= 10:
            s_name = pop_names.get(secondary[0], secondary[0])
            s_pct = secondary[1]
            conclusions.append(
                f"The second largest contribution is {s_name} ({s_pct}%), "
                f"indicating ancestors from {pop_regions.get(secondary[0], '')}."
            )

        significant = [(p, v) for p, v in pcts.items() if v >= 5]
        if len(significant) >= 3:
            names = [f"{pop_names.get(p, p)} ({v}%)" for p, v in sorted(significant, key=lambda x: -x[1])]
            conclusions.append(
                f"You show contributions from {len(significant)} continental groups: "
                f"{', '.join(names)}. "
                f"This admixture profile is typical of Latin American populations, "
                f"especially Brazilian, which historically received European, African "
                f"and Amerindian contributions."
            )

        conf_text = {
            "good": f"This estimate is based on {markers} genetic markers, which provides a good indication of your continental composition.",
            "moderate": f"This estimate uses {markers} markers — enough for a general indication, but less precise than commercial tests.",
            "low": f"This estimate uses only {markers} markers — treat it as preliminary. Commercial tests use thousands.",
        }
        conclusions.append(conf_text.get(confidence, ""))

        conclusions.append(
            "IMPORTANT: These percentages represent CONTINENTAL ancestry "
            "(broad population groups), not specific countries or ethnicities. "
            "For sub-regions (e.g., Western vs Iberian Europe), commercial tests "
            "like Genera, 23andMe or AncestryDNA use proprietary reference panels "
            "with thousands of markers."
        )
    else:
        if p_pct >= 70:
            conclusions.append(
                f"Sua composicao genetica indica uma predominancia {p_name} "
                f"({p_pct}%). Isso significa que a maior parte dos seus ancestrais "
                f"provavelmente vieram de {pop_regions.get(primary[0], 'regioes associadas')}."
            )
        elif p_pct >= 40:
            conclusions.append(
                f"Sua composicao genetica mostra uma mistura significativa, com "
                f"a maior contribuicao sendo {p_name} ({p_pct}%). "
                f"Isso reflete ancestrais de {pop_regions.get(primary[0], '')}."
            )
        else:
            conclusions.append(
                f"Sua composicao genetica e altamente miscigenada, sem uma "
                f"ancestralidade fortemente predominante. A maior contribuicao "
                f"e {p_name} ({p_pct}%)."
            )

        if secondary and secondary[1] >= 10:
            s_name = pop_names.get(secondary[0], secondary[0])
            s_pct = secondary[1]
            conclusions.append(
                f"A segunda maior contribuicao e {s_name} ({s_pct}%), "
                f"indicando ancestrais de {pop_regions.get(secondary[0], '')}."
            )

        significant = [(p, v) for p, v in pcts.items() if v >= 5]
        if len(significant) >= 3:
            names = [f"{pop_names.get(p, p)} ({v}%)" for p, v in sorted(significant, key=lambda x: -x[1])]
            conclusions.append(
                f"Voce apresenta contribuicoes de {len(significant)} grupos continentais: "
                f"{', '.join(names)}. "
                f"Esse perfil de miscigenacao e tipico de populacoes latino-americanas, "
                f"especialmente brasileiras, que historicamente receberam contribuicoes "
                f"europeias, africanas e amerindias."
            )

        conf_text = {
            "good": f"Esta estimativa e baseada em {markers} marcadores geneticos, o que oferece uma boa indicacao da sua composicao continental.",
            "moderate": f"Esta estimativa usa {markers} marcadores — suficiente para uma indicacao geral, mas menos precisa que testes comerciais.",
            "low": f"Esta estimativa usa apenas {markers} marcadores — considere-a uma indicacao preliminar. Testes comerciais usam milhares.",
        }
        conclusions.append(conf_text.get(confidence, ""))

        conclusions.append(
            "IMPORTANTE: Estes percentuais representam ancestralidade CONTINENTAL "
            "(grandes grupos populacionais), nao paises ou etnias especificas. "
            "Para sub-regioes (ex: Europa Ocidental vs Iberica), testes comerciais "
            "como Genera, 23andMe ou AncestryDNA usam paineis de referencia "
            "proprietarios com milhares de marcadores."
        )

    return conclusions
