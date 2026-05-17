"""
English translations for all Portuguese texts in the phenotype and ancestry modules.
"""

# =============================================================================
# Phenotype SNP translations: rsid -> {trait_en, variants: {genotype: desc_en}}
# =============================================================================

PHENOTYPE_EN = {
    # ── EYE COLOR SNPs ──
    "rs12913832": {
        "trait_en": "Main determinant of eye color",
        "variants": {
            "GG": "Strong predisposition for blue eyes",
            "AG": "Brown or green eyes more likely",
            "GA": "Brown or green eyes more likely",
            "AA": "Brown eyes very likely",
        },
    },
    "rs1800407": {
        "trait_en": "Eye color modifier",
        "variants": {
            "CC": "No modifier effect (reference)",
            "CT": "Tendency to lighten brown eyes toward green",
            "TC": "Tendency to lighten eyes",
            "TT": "Strong lightening — may result in green or blue eyes",
        },
    },
    "rs12896399": {
        "trait_en": "Light eyes",
        "variants": {
            "GG": "Reference",
            "GT": "Slight tendency toward lighter eyes",
            "TG": "Slight tendency toward lighter eyes",
            "TT": "Moderate tendency toward light eyes",
        },
    },
    "rs1393350": {
        "trait_en": "Ocular pigmentation modifier",
        "variants": {
            "GG": "Reference",
            "GA": "Slight lightening",
            "AG": "Slight lightening",
            "AA": "Moderate lightening",
        },
    },

    # ── HAIR COLOR SNPs ──
    "rs12821256": {
        "trait_en": "Blond hair",
        "variants": {
            "TT": "Reference (no blond effect)",
            "TC": "Tendency toward lighter hair",
            "CT": "Tendency toward lighter hair",
            "CC": "Strong tendency toward blond hair",
        },
    },
    "rs1805007": {
        "trait_en": "Red hair (R151C)",
        "variants": {
            "CC": "Reference (no red hair effect)",
            "CT": "Red hair carrier — reddish highlights possible",
            "TC": "Red hair carrier",
            "TT": "Strong predisposition for red hair",
        },
    },
    "rs1805008": {
        "trait_en": "Red hair (R160W)",
        "variants": {
            "CC": "Reference",
            "CT": "Red hair carrier — slight tendency",
            "TC": "Red hair carrier",
            "TT": "Strong red hair predisposition",
        },
    },
    "rs2228479": {
        "trait_en": "General pigmentation",
        "variants": {
            "GG": "Normal pigmentation",
            "GA": "Slight pigment reduction — slightly lighter hair",
            "AG": "Slight reduction",
            "AA": "Reduced pigmentation — lighter hair",
        },
    },
    "rs12203592": {
        "trait_en": "Light hair / freckles",
        "variants": {
            "CC": "Reference",
            "CT": "Tendency toward lighter hair and freckles",
            "TC": "Tendency toward lighter hair",
            "TT": "Light hair and freckles likely",
        },
    },

    # ── HAIR TEXTURE SNPs ──
    "rs3827760": {
        "trait_en": "Hair Thickness",
        "variants": {
            "CC": "Standard European/African hair thickness",
            "CT": "Intermediate — slightly thicker hair",
            "TC": "Intermediate — slightly thicker hair",
            "TT": "Thicker, straighter hair (common East Asian variant)",
            "AA": "Standard hair thickness",
        },
    },

    # ── FRECKLE SNPs ──
    "rs4911414": {
        "trait_en": "Freckles",
        "variants": {
            "TT": "Low tendency for freckles",
            "TG": "Moderate tendency for freckles",
            "GT": "Moderate tendency for freckles",
            "GG": "Increased tendency for freckles",
        },
    },
    "rs1805009": {
        "trait_en": "Freckles / sun-sensitive skin",
        "variants": {
            "GG": "Reference",
            "GC": "Tendency for freckles and fair skin",
            "CG": "Tendency for freckles",
            "CC": "Strong tendency for freckles and sun sensitivity",
        },
    },

    # ── BALDNESS SNPs ──
    "rs2180439": {
        "trait_en": "Main male-pattern baldness locus",
        "variants": {
            "CC": "Homozygous risk allele — significantly increased risk of androgenetic alopecia.",
            "CT": "Carrier of one risk allele copy — moderately increased risk.",
            "TC": "Carrier of one copy — moderate risk.",
            "TT": "No risk allele at this locus — protective.",
        },
    },
    "rs6152": {
        "trait_en": "DHT sensitivity — inherited from mother",
        "variants": {
            "GG": "Standard androgen receptor — no increased risk via this pathway.",
            "GA": "Increased DHT (dihydrotestosterone) sensitivity. Increased baldness risk. This gene is inherited from the MOTHER.",
            "AG": "Increased DHT sensitivity, inherited from mother.",
            "AA": "High DHT sensitivity — substantial baldness risk. Inherited from mother. Finasteride may be effective if prescribed by a dermatologist.",
        },
    },
    "rs929626": {
        "trait_en": "Additional baldness locus (GWAS)",
        "variants": {
            "AA": "Homozygous risk allele — additional contribution to baldness risk.",
            "AG": "Carrier — slight contribution to risk.",
            "GA": "Carrier — slight contribution.",
            "GG": "No risk allele at this locus.",
        },
    },
    "rs1385699": {
        "trait_en": "Early-onset baldness locus",
        "variants": {
            "TT": "Increased risk of early-onset baldness.",
            "TC": "Slight risk of earlier onset.",
            "CT": "Slight risk of earlier onset.",
            "CC": "No increased risk of early baldness at this locus.",
        },
    },
}


# =============================================================================
# Baldness result translations (summary strings from analyze_phenotype)
# =============================================================================

BALDNESS_EN = {
    "high": "High risk of androgenetic alopecia",
    "moderate": "Moderate risk of androgenetic alopecia",
    "mild": "Mild risk of androgenetic alopecia",
    "low": "Low risk of androgenetic alopecia (at analyzed loci)",
    "ar_note": (
        "The AR gene (androgen receptor) is on the X chromosome — you inherited "
        "this variant from your MOTHER. Looking at your maternal grandfather is "
        "more informative than your father."
    ),
}


# =============================================================================
# Freckling result translations (summary strings from analyze_phenotype)
# =============================================================================

FRECKLING_EN = {
    "high": "High tendency for freckles",
    "moderate": "Moderate tendency for freckles",
    "low": "Low tendency for freckles",
}


# =============================================================================
# Hair texture fallback
# =============================================================================

TEXTURE_EN = {
    "not_available": "Information not available",
}


# =============================================================================
# Ancestry conclusion templates (for _build_ancestry_conclusions)
# =============================================================================

ANCESTRY_EN = {
    # Population names (adjective form)
    "pop_names": {
        "EUR": "European",
        "AFR": "African",
        "AMR": "Amerindian (Indigenous peoples of the Americas)",
        "EAS": "East Asian",
    },
    # Population region descriptions
    "pop_regions": {
        "EUR": "Europe (Portugal, Spain, Italy, France, Germany and other European countries)",
        "AFR": "Africa (West, Central and East Africa)",
        "AMR": "the Americas (pre-Columbian indigenous populations of South, Central and North America)",
        "EAS": "East Asia (China, Japan, Korea and Southeast Asia)",
    },
    # Population labels (noun form, used in UI)
    "pop_labels": {
        "EUR": "European",
        "AFR": "African",
        "AMR": "Amerindian",
        "EAS": "East Asian",
    },

    # Primary ancestry templates (keyed by threshold)
    "predominance_high": (
        "Your genetic composition indicates a {pop} predominance ({pct}%). "
        "This means most of your ancestors likely came from {region}."
    ),
    "predominance_moderate": (
        "Your genetic composition shows a significant admixture, with the "
        "largest contribution being {pop} ({pct}%). "
        "This reflects ancestors from {region}."
    ),
    "predominance_low": (
        "Your genetic composition is highly admixed, without a strongly "
        "predominant ancestry. The largest contribution is {pop} ({pct}%)."
    ),

    # Secondary ancestry
    "secondary": (
        "The second largest contribution is {pop} ({pct}%), "
        "indicating ancestors from {region}."
    ),

    # Mixed heritage context
    "mixed": (
        "You show contributions from {count} continental groups: {groups}. "
        "This admixture profile is typical of Latin American populations, "
        "especially Brazilian, which historically received European, "
        "African, and Amerindian contributions."
    ),

    # Confidence notes
    "confidence_good": (
        "This estimate is based on {n} genetic markers, which provides "
        "a good indication of your continental composition."
    ),
    "confidence_moderate": (
        "This estimate uses {n} markers — sufficient for a general indication, "
        "but less precise than commercial tests."
    ),
    "confidence_low": (
        "This estimate uses only {n} markers — consider it a preliminary "
        "indication. Commercial tests use thousands."
    ),

    # Disclaimer (always appended)
    "disclaimer": (
        "IMPORTANT: These percentages represent CONTINENTAL ancestry "
        "(large population groups), not specific countries or ethnicities. "
        "For sub-regions (e.g., Western European vs. Iberian), commercial tests "
        "like Genera, 23andMe or AncestryDNA use proprietary reference panels "
        "with thousands of markers."
    ),
}
