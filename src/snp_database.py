"""
Curated SNP database — ~200 well-researched, actionable SNPs.

Each entry maps an rsID to its gene, category, and genotype interpretations.
Sources: CPIC guidelines, PharmGKB, SNPedia, peer-reviewed GWAS.

Magnitude scale (0–6):
  0 = informational only
  1 = low impact, minor effect
  2 = moderate, worth noting
  3 = high impact, actionable
  4–6 = very high impact, requires attention
"""

CURATED_SNPS = {

    # ═══════════════════════════════════════════════════════════════════════════
    # DRUG METABOLISM (Pharmacogenomics)
    # ═══════════════════════════════════════════════════════════════════════════

    "rs762551": {
        "gene": "CYP1A2", "category": "Drug Metabolism",
        "variants": {
            "AA": {"status": "fast", "desc": "Fast caffeine metabolizer — clears caffeine quickly, lower cardiovascular risk from coffee", "magnitude": 1},
            "AC": {"status": "intermediate", "desc": "Intermediate caffeine metabolizer — moderate clearance, ~5–6hr half-life", "magnitude": 2},
            "CC": {"status": "slow", "desc": "Slow caffeine metabolizer — caffeine lingers 8–12hrs, increased cardiovascular risk with high intake", "magnitude": 3},
        },
    },
    "rs4244285": {
        "gene": "CYP2C19", "category": "Drug Metabolism",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal CYP2C19 — standard drug metabolism", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate CYP2C19 (*2 carrier) — clopidogrel less effective", "magnitude": 3},
            "AG": {"status": "intermediate", "desc": "Intermediate CYP2C19 (*2 carrier) — clopidogrel less effective", "magnitude": 3},
            "AA": {"status": "poor", "desc": "Poor CYP2C19 (*2/*2) — clopidogrel ineffective, use alternative antiplatelet", "magnitude": 4},
        },
    },
    "rs12248560": {
        "gene": "CYP2C19", "category": "Drug Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal CYP2C19 metabolism", "magnitude": 0},
            "CT": {"status": "rapid", "desc": "Rapid CYP2C19 (*17) — faster metabolism of PPIs, some antidepressants", "magnitude": 2},
            "TC": {"status": "rapid", "desc": "Rapid CYP2C19 (*17) — faster metabolism of PPIs, some antidepressants", "magnitude": 2},
            "TT": {"status": "ultrarapid", "desc": "Ultrarapid CYP2C19 (*17/*17) — significantly faster drug metabolism", "magnitude": 3},
        },
    },
    "rs1799853": {
        "gene": "CYP2C9", "category": "Drug Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal CYP2C9 — standard warfarin/NSAID metabolism", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Intermediate CYP2C9 (*2) — warfarin dose reduction needed", "magnitude": 3},
            "TC": {"status": "intermediate", "desc": "Intermediate CYP2C9 (*2) — warfarin dose reduction needed", "magnitude": 3},
            "TT": {"status": "poor", "desc": "Poor CYP2C9 (*2/*2) — significant warfarin sensitivity", "magnitude": 4},
        },
    },
    "rs1057910": {
        "gene": "CYP2C9", "category": "Drug Metabolism",
        "variants": {
            "AA": {"status": "normal", "desc": "Normal CYP2C9 function", "magnitude": 0},
            "AC": {"status": "intermediate", "desc": "Intermediate CYP2C9 (*3) — warfarin dose reduction", "magnitude": 3},
            "CA": {"status": "intermediate", "desc": "Intermediate CYP2C9 (*3) — warfarin dose reduction", "magnitude": 3},
            "CC": {"status": "poor", "desc": "Poor CYP2C9 (*3/*3) — high warfarin sensitivity", "magnitude": 4},
        },
    },
    "rs9923231": {
        "gene": "VKORC1", "category": "Drug Metabolism",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal warfarin sensitivity", "magnitude": 0},
            "GA": {"status": "sensitive", "desc": "Increased warfarin sensitivity — lower doses needed", "magnitude": 3},
            "AG": {"status": "sensitive", "desc": "Increased warfarin sensitivity — lower doses needed", "magnitude": 3},
            "AA": {"status": "highly_sensitive", "desc": "Highly warfarin sensitive — significantly lower doses", "magnitude": 4},
        },
    },
    "rs4149056": {
        "gene": "SLCO1B1", "category": "Drug Metabolism",
        "variants": {
            "TT": {"status": "normal", "desc": "Normal statin transport — standard myopathy risk", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate statin transporter — 4x myopathy risk with simvastatin", "magnitude": 3},
            "CT": {"status": "intermediate", "desc": "Intermediate statin transporter — 4x myopathy risk with simvastatin", "magnitude": 3},
            "CC": {"status": "poor", "desc": "Poor statin transporter — 17x myopathy risk, avoid simvastatin", "magnitude": 4},
        },
    },
    "rs3892097": {
        "gene": "CYP2D6", "category": "Drug Metabolism",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal CYP2D6 — standard codeine/tramadol metabolism", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Intermediate CYP2D6 — reduced opioid activation", "magnitude": 3},
            "AG": {"status": "intermediate", "desc": "Intermediate CYP2D6 — reduced opioid activation", "magnitude": 3},
            "AA": {"status": "poor", "desc": "Poor CYP2D6 (*4/*4) — codeine ineffective, tramadol reduced", "magnitude": 4},
        },
    },
    "rs1065852": {
        "gene": "CYP2D6", "category": "Drug Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal CYP2D6 function", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Reduced CYP2D6 function (*10 carrier)", "magnitude": 2},
            "TC": {"status": "intermediate", "desc": "Reduced CYP2D6 function (*10 carrier)", "magnitude": 2},
            "TT": {"status": "poor", "desc": "Poor CYP2D6 metabolizer (*10/*10) — common in Asian populations", "magnitude": 3},
        },
    },
    "rs776746": {
        "gene": "CYP3A5", "category": "Drug Metabolism",
        "variants": {
            "TT": {"status": "expressor", "desc": "CYP3A5 expressor — may need higher tacrolimus doses", "magnitude": 2},
            "TC": {"status": "intermediate", "desc": "Intermediate CYP3A5 expression", "magnitude": 1},
            "CT": {"status": "intermediate", "desc": "Intermediate CYP3A5 expression", "magnitude": 1},
            "CC": {"status": "non_expressor", "desc": "CYP3A5 non-expressor (*3/*3) — standard tacrolimus dosing", "magnitude": 1},
        },
    },
    "rs3918290": {
        "gene": "DPYD", "category": "Drug Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal DPYD — standard fluoropyrimidine tolerance", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Reduced DPYD — 50% dose reduction for 5-FU/capecitabine", "magnitude": 5},
            "TC": {"status": "intermediate", "desc": "Reduced DPYD — 50% dose reduction for 5-FU/capecitabine", "magnitude": 5},
            "TT": {"status": "deficient", "desc": "DPYD deficient — fluoropyrimidines contraindicated (can be fatal)", "magnitude": 6},
        },
    },
    "rs1800460": {
        "gene": "TPMT", "category": "Drug Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal TPMT — standard thiopurine tolerance", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Intermediate TPMT — thiopurine dose reduction recommended", "magnitude": 4},
            "TC": {"status": "intermediate", "desc": "Intermediate TPMT — thiopurine dose reduction recommended", "magnitude": 4},
            "TT": {"status": "poor", "desc": "Poor TPMT — thiopurines can cause severe myelosuppression", "magnitude": 5},
        },
    },
    "rs2395029": {
        "gene": "HLA-B", "category": "Drug Metabolism",
        "variants": {
            "TT": {"status": "normal", "desc": "Low risk of abacavir hypersensitivity", "magnitude": 0},
            "TG": {"status": "carrier", "desc": "HLA-B*5701 carrier — abacavir contraindicated", "magnitude": 5},
            "GT": {"status": "carrier", "desc": "HLA-B*5701 carrier — abacavir contraindicated", "magnitude": 5},
            "GG": {"status": "positive", "desc": "HLA-B*5701 positive — abacavir contraindicated", "magnitude": 5},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # METHYLATION & B-VITAMINS
    # ═══════════════════════════════════════════════════════════════════════════

    "rs1801133": {
        "gene": "MTHFR", "category": "Methylation",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal MTHFR function (C677C)", "magnitude": 0},
            "AG": {"status": "reduced", "desc": "Reduced MTHFR (C677T het) — ~35% reduced activity, consider methylfolate", "magnitude": 2},
            "GA": {"status": "reduced", "desc": "Reduced MTHFR (C677T het) — ~35% reduced activity, consider methylfolate", "magnitude": 2},
            "AA": {"status": "significantly_reduced", "desc": "Significantly reduced MTHFR (C677T hom) — ~70% reduced, use methylfolate", "magnitude": 3},
        },
    },
    "rs1801131": {
        "gene": "MTHFR", "category": "Methylation",
        "variants": {
            "AA": {"status": "normal", "desc": "Normal MTHFR A1298C function", "magnitude": 0},
            "AC": {"status": "reduced", "desc": "Reduced MTHFR A1298C (heterozygous)", "magnitude": 1},
            "CA": {"status": "reduced", "desc": "Reduced MTHFR A1298C (heterozygous)", "magnitude": 1},
            "CC": {"status": "significantly_reduced", "desc": "Significantly reduced MTHFR A1298C", "magnitude": 2},
            "GT": {"status": "reduced", "desc": "Reduced MTHFR A1298C (opposite strand, heterozygous)", "magnitude": 1},
            "TG": {"status": "reduced", "desc": "Reduced MTHFR A1298C (opposite strand, heterozygous)", "magnitude": 1},
            "TT": {"status": "significantly_reduced", "desc": "Significantly reduced MTHFR A1298C (opposite strand)", "magnitude": 2},
            "GG": {"status": "normal", "desc": "Normal MTHFR A1298C (opposite strand)", "magnitude": 0},
        },
    },
    "rs1802059": {
        "gene": "MTRR", "category": "Methylation",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal MTRR — efficient B12 recycling", "magnitude": 0},
            "GA": {"status": "reduced", "desc": "Reduced MTRR — may need higher B12 intake", "magnitude": 1},
            "AG": {"status": "reduced", "desc": "Reduced MTRR — may need higher B12 intake", "magnitude": 1},
            "AA": {"status": "significantly_reduced", "desc": "Significantly reduced MTRR — functional B12 deficiency risk, use methylcobalamin", "magnitude": 2},
        },
    },
    "rs4680": {
        "gene": "COMT", "category": "Neurotransmitters",
        "variants": {
            "GG": {"status": "fast", "desc": "Fast COMT (Val/Val) — rapid dopamine clearance, stress resilient but lower baseline focus", "magnitude": 1},
            "GA": {"status": "intermediate", "desc": "Intermediate COMT (Val/Met) — balanced dopamine metabolism", "magnitude": 1},
            "AG": {"status": "intermediate", "desc": "Intermediate COMT (Val/Met) — balanced dopamine metabolism", "magnitude": 1},
            "AA": {"status": "slow", "desc": "Slow COMT (Met/Met) — high baseline dopamine, better focus but stress-sensitive", "magnitude": 2},
        },
    },
    "rs7946": {
        "gene": "PEMT", "category": "Methylation",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal PEMT — adequate endogenous choline production", "magnitude": 0},
            "CT": {"status": "reduced", "desc": "Reduced PEMT — increase dietary choline (eggs, liver)", "magnitude": 1},
            "TC": {"status": "reduced", "desc": "Reduced PEMT — increase dietary choline (eggs, liver)", "magnitude": 1},
            "TT": {"status": "significantly_reduced", "desc": "Significantly reduced PEMT — higher choline requirement, supplement if needed", "magnitude": 2},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # NEUROTRANSMITTERS & COGNITION
    # ═══════════════════════════════════════════════════════════════════════════

    "rs6265": {
        "gene": "BDNF", "category": "Neurotransmitters",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal BDNF (Val66Val) — standard activity-dependent neuroplasticity", "magnitude": 0},
            "CT": {"status": "reduced", "desc": "Reduced BDNF (Val66Met) — exercise is critical for BDNF production", "magnitude": 2},
            "TC": {"status": "reduced", "desc": "Reduced BDNF (Val66Met) — exercise is critical for BDNF production", "magnitude": 2},
            "TT": {"status": "significantly_reduced", "desc": "Significantly reduced BDNF (Met66Met) — prioritize exercise, learning, social activity", "magnitude": 3},
        },
    },
    "rs1800497": {
        "gene": "ANKK1/DRD2", "category": "Neurotransmitters",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal D2 receptor density", "magnitude": 0},
            "GA": {"status": "reduced", "desc": "Reduced D2 receptor density (Taq1A het) — may seek more stimulation", "magnitude": 1},
            "AG": {"status": "reduced", "desc": "Reduced D2 receptor density (Taq1A het) — may seek more stimulation", "magnitude": 1},
            "AA": {"status": "significantly_reduced", "desc": "Significantly reduced D2 receptors — higher reward-seeking, addiction awareness", "magnitude": 2},
        },
    },
    "rs53576": {
        "gene": "OXTR", "category": "Neurotransmitters",
        "variants": {
            "GG": {"status": "high_empathy", "desc": "Higher oxytocin receptor expression — strong social bonding, empathy", "magnitude": 1},
            "GA": {"status": "intermediate", "desc": "Intermediate oxytocin receptor expression", "magnitude": 0},
            "AG": {"status": "intermediate", "desc": "Intermediate oxytocin receptor expression", "magnitude": 0},
            "AA": {"status": "lower", "desc": "Lower oxytocin receptor expression — may need more effort in social bonding", "magnitude": 1},
        },
    },
    "rs4570625": {
        "gene": "TPH2", "category": "Neurotransmitters",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal serotonin synthesis", "magnitude": 0},
            "GT": {"status": "reduced", "desc": "Reduced TPH2 expression — lower serotonin production capacity", "magnitude": 1},
            "TG": {"status": "reduced", "desc": "Reduced TPH2 expression — lower serotonin production capacity", "magnitude": 1},
            "TT": {"status": "significantly_reduced", "desc": "Significantly reduced serotonin synthesis — mindfulness and exercise help", "magnitude": 2},
        },
    },
    "rs1799971": {
        "gene": "OPRM1", "category": "Neurotransmitters",
        "variants": {
            "AA": {"status": "normal", "desc": "Normal mu-opioid receptor", "magnitude": 0},
            "AG": {"status": "altered", "desc": "Altered opioid receptor (A118G) — may need different pain management dosing", "magnitude": 2},
            "GA": {"status": "altered", "desc": "Altered opioid receptor (A118G) — may need different pain management dosing", "magnitude": 2},
            "GG": {"status": "significantly_altered", "desc": "Significantly altered opioid receptor — inform anesthesiologist", "magnitude": 3},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # CAFFEINE
    # ═══════════════════════════════════════════════════════════════════════════

    "rs5751876": {
        "gene": "ADORA2A", "category": "Caffeine Response",
        "variants": {
            "CC": {"status": "lower_sensitivity", "desc": "Lower caffeine anxiety sensitivity", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Moderate caffeine anxiety sensitivity", "magnitude": 1},
            "TC": {"status": "intermediate", "desc": "Moderate caffeine anxiety sensitivity", "magnitude": 1},
            "TT": {"status": "anxiety_prone", "desc": "Higher caffeine anxiety — consider L-theanine pairing or green tea", "magnitude": 2},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # CARDIOVASCULAR
    # ═══════════════════════════════════════════════════════════════════════════

    "rs5186": {
        "gene": "AGTR1", "category": "Cardiovascular",
        "variants": {
            "AA": {"status": "normal", "desc": "Normal angiotensin II receptor function", "magnitude": 0},
            "AC": {"status": "increased", "desc": "Increased AGTR1 activity — higher hypertension risk, ARBs may be especially effective", "magnitude": 2},
            "CA": {"status": "increased", "desc": "Increased AGTR1 activity — higher hypertension risk", "magnitude": 2},
            "CC": {"status": "high", "desc": "High AGTR1 activity — monitor blood pressure closely", "magnitude": 3},
        },
    },
    "rs4340": {
        "gene": "ACE", "category": "Cardiovascular",
        "variants": {
            "II": {"status": "low", "desc": "Lower ACE activity — endurance advantage, lower BP tendency", "magnitude": 0},
            "ID": {"status": "intermediate", "desc": "Intermediate ACE activity", "magnitude": 1},
            "DI": {"status": "intermediate", "desc": "Intermediate ACE activity", "magnitude": 1},
            "DD": {"status": "high", "desc": "Higher ACE activity — hypertension risk, ACE inhibitors effective", "magnitude": 2},
        },
    },
    "rs699": {
        "gene": "AGT", "category": "Cardiovascular",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal angiotensinogen levels", "magnitude": 0},
            "CT": {"status": "increased", "desc": "Increased angiotensinogen (M235T het) — slight BP risk", "magnitude": 1},
            "TC": {"status": "increased", "desc": "Increased angiotensinogen (M235T het) — slight BP risk", "magnitude": 1},
            "TT": {"status": "high", "desc": "High angiotensinogen — increased hypertension risk", "magnitude": 2},
        },
    },
    "rs5443": {
        "gene": "GNB3", "category": "Cardiovascular",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal G-protein signaling", "magnitude": 0},
            "CT": {"status": "increased", "desc": "GNB3 C825T het — increased hypertension and obesity risk", "magnitude": 1},
            "TC": {"status": "increased", "desc": "GNB3 C825T het — increased hypertension and obesity risk", "magnitude": 1},
            "TT": {"status": "high", "desc": "GNB3 C825T hom — higher hypertension and weight gain risk", "magnitude": 2},
        },
    },
    "rs1799963": {
        "gene": "F2", "category": "Cardiovascular",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal prothrombin — standard clotting risk", "magnitude": 0},
            "GA": {"status": "carrier", "desc": "Prothrombin G20210A carrier — 3x VTE risk, caution with hormonal contraceptives", "magnitude": 3},
            "AG": {"status": "carrier", "desc": "Prothrombin G20210A carrier — 3x VTE risk", "magnitude": 3},
            "AA": {"status": "homozygous", "desc": "Prothrombin G20210A homozygous — significant clotting risk", "magnitude": 4},
        },
    },
    "rs6025": {
        "gene": "F5", "category": "Cardiovascular",
        "variants": {
            "CC": {"status": "normal", "desc": "No Factor V Leiden — normal clotting", "magnitude": 0},
            "CT": {"status": "carrier", "desc": "Factor V Leiden carrier — 5–10x VTE risk, avoid estrogen-based contraceptives", "magnitude": 4},
            "TC": {"status": "carrier", "desc": "Factor V Leiden carrier — 5–10x VTE risk", "magnitude": 4},
            "TT": {"status": "homozygous", "desc": "Factor V Leiden homozygous — 50–100x VTE risk, hematologist essential", "magnitude": 5},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # NUTRITION
    # ═══════════════════════════════════════════════════════════════════════════

    "rs2282679": {
        "gene": "GC", "category": "Nutrition",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal vitamin D binding protein", "magnitude": 0},
            "GT": {"status": "low", "desc": "Lower vitamin D levels — supplement 2000–4000 IU D3 daily", "magnitude": 2},
            "TG": {"status": "low", "desc": "Lower vitamin D levels — supplement 2000–4000 IU D3 daily", "magnitude": 2},
            "TT": {"status": "very_low", "desc": "Significantly lower vitamin D — supplement 4000–5000 IU D3, test levels", "magnitude": 3},
        },
    },
    "rs174547": {
        "gene": "FADS1", "category": "Nutrition",
        "variants": {
            "TT": {"status": "normal", "desc": "Normal omega-3/6 conversion from plant sources", "magnitude": 0},
            "TC": {"status": "reduced", "desc": "Reduced ALA→EPA/DHA conversion — fish oil beneficial", "magnitude": 1},
            "CT": {"status": "reduced", "desc": "Reduced ALA→EPA/DHA conversion — fish oil beneficial", "magnitude": 1},
            "CC": {"status": "low_conversion", "desc": "Poor omega-3 conversion — direct EPA/DHA supplementation important", "magnitude": 2},
        },
    },
    "rs4988235": {
        "gene": "MCM6/LCT", "category": "Nutrition",
        "variants": {
            "TT": {"status": "tolerant", "desc": "Lactose persistent — full dairy tolerance", "magnitude": 0},
            "TC": {"status": "likely_tolerant", "desc": "Likely lactose tolerant — one persistence allele", "magnitude": 0},
            "CT": {"status": "likely_tolerant", "desc": "Likely lactose tolerant — one persistence allele", "magnitude": 0},
            "CC": {"status": "intolerant", "desc": "Lactose intolerant — fermented dairy OK, consider lactase supplements", "magnitude": 2},
        },
    },
    "rs7903146": {
        "gene": "TCF7L2", "category": "Nutrition",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal diabetes risk", "magnitude": 0},
            "CT": {"status": "increased", "desc": "TCF7L2 het — 1.4x type 2 diabetes risk, monitor glucose", "magnitude": 2},
            "TC": {"status": "increased", "desc": "TCF7L2 het — 1.4x type 2 diabetes risk, monitor glucose", "magnitude": 2},
            "TT": {"status": "high", "desc": "TCF7L2 hom — 2x type 2 diabetes risk, regular HbA1c testing", "magnitude": 3},
        },
    },
    "rs5082": {
        "gene": "APOA2", "category": "Nutrition",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal saturated fat response", "magnitude": 0},
            "GA": {"status": "intermediate", "desc": "Moderate saturated fat sensitivity", "magnitude": 1},
            "AG": {"status": "intermediate", "desc": "Moderate saturated fat sensitivity", "magnitude": 1},
            "AA": {"status": "sensitive", "desc": "High saturated fat sensitivity — limit sat fat to <7% calories", "magnitude": 2},
        },
    },
    "rs11568820": {
        "gene": "BCMO1", "category": "Nutrition",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal beta-carotene → vitamin A conversion", "magnitude": 0},
            "GA": {"status": "reduced", "desc": "Reduced beta-carotene conversion — include preformed vitamin A (eggs, liver)", "magnitude": 1},
            "AG": {"status": "reduced", "desc": "Reduced beta-carotene conversion — include preformed vitamin A (eggs, liver)", "magnitude": 1},
            "AA": {"status": "significantly_reduced", "desc": "Poor beta-carotene conversion — need preformed vitamin A sources", "magnitude": 2},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # FITNESS & EXERCISE
    # ═══════════════════════════════════════════════════════════════════════════

    "rs1815739": {
        "gene": "ACTN3", "category": "Fitness",
        "variants": {
            "CC": {"status": "power", "desc": "ACTN3 R577R — full alpha-actinin-3, power/sprint advantage", "magnitude": 1},
            "CT": {"status": "mixed", "desc": "ACTN3 R577X het — balanced power/endurance profile", "magnitude": 1},
            "TC": {"status": "mixed", "desc": "ACTN3 R577X het — balanced power/endurance profile", "magnitude": 1},
            "TT": {"status": "endurance", "desc": "ACTN3 X577X — no alpha-actinin-3, endurance advantage", "magnitude": 1},
        },
    },
    "rs1042713": {
        "gene": "ADRB2", "category": "Fitness",
        "variants": {
            "GG": {"status": "gly16", "desc": "ADRB2 Gly16 — enhanced fat mobilization during exercise", "magnitude": 1},
            "GA": {"status": "intermediate", "desc": "Intermediate ADRB2 — moderate exercise fat-burning", "magnitude": 0},
            "AG": {"status": "intermediate", "desc": "Intermediate ADRB2 — moderate exercise fat-burning", "magnitude": 0},
            "AA": {"status": "arg16", "desc": "ADRB2 Arg16 — standard fat mobilization", "magnitude": 0},
        },
    },
    "rs8192678": {
        "gene": "PPARGC1A", "category": "Fitness",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal PGC-1α — standard mitochondrial biogenesis", "magnitude": 0},
            "CT": {"status": "reduced", "desc": "Reduced PGC-1α — exercise more important for mitochondrial health", "magnitude": 1},
            "TC": {"status": "reduced", "desc": "Reduced PGC-1α — exercise more important for mitochondrial health", "magnitude": 1},
            "TT": {"status": "significantly_reduced", "desc": "Significantly reduced PGC-1α — prioritize aerobic exercise", "magnitude": 2},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # SLEEP & CIRCADIAN
    # ═══════════════════════════════════════════════════════════════════════════

    "rs12363415": {
        "gene": "ARNTL", "category": "Sleep/Circadian",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal circadian rhythm strength", "magnitude": 0},
            "CT": {"status": "altered", "desc": "Altered BMAL1 — may benefit from strong light/dark cues", "magnitude": 1},
            "TC": {"status": "altered", "desc": "Altered BMAL1 — may benefit from strong light/dark cues", "magnitude": 1},
            "TT": {"status": "significantly_altered", "desc": "Significantly altered circadian — strict sleep schedule, morning bright light essential", "magnitude": 2},
        },
    },
    "rs57875989": {
        "gene": "DEC2/BHLHE41", "category": "Sleep/Circadian",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal sleep duration requirement (~7–9 hours)", "magnitude": 0},
            "CT": {"status": "short_sleeper", "desc": "Short sleeper variant — may need less sleep (6–6.5 hrs)", "magnitude": 1},
            "TC": {"status": "short_sleeper", "desc": "Short sleeper variant — may need less sleep (6–6.5 hrs)", "magnitude": 1},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # INFLAMMATION & IMMUNE
    # ═══════════════════════════════════════════════════════════════════════════

    "rs1800795": {
        "gene": "IL6", "category": "Inflammation",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal IL-6 levels", "magnitude": 0},
            "CG": {"status": "intermediate", "desc": "Intermediate IL-6 production", "magnitude": 1},
            "GC": {"status": "intermediate", "desc": "Intermediate IL-6 production", "magnitude": 1},
            "GG": {"status": "high", "desc": "Higher baseline IL-6 — anti-inflammatory diet and omega-3s beneficial", "magnitude": 2},
        },
    },
    "rs2187668": {
        "gene": "HLA-DQA1", "category": "Autoimmune",
        "variants": {
            "CC": {"status": "normal", "desc": "Low celiac disease risk", "magnitude": 0},
            "CT": {"status": "increased_risk", "desc": "HLA-DQ2.5 carrier — ~3% lifetime celiac risk, know the symptoms", "magnitude": 2},
            "TC": {"status": "increased_risk", "desc": "HLA-DQ2.5 carrier — ~3% lifetime celiac risk", "magnitude": 2},
            "TT": {"status": "high_risk", "desc": "Homozygous HLA-DQ2.5 — higher celiac risk, monitor for symptoms", "magnitude": 3},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # DETOXIFICATION
    # ═══════════════════════════════════════════════════════════════════════════

    "rs1801280": {
        "gene": "NAT2", "category": "Detoxification",
        "variants": {
            "TT": {"status": "fast", "desc": "Fast acetylator — standard drug metabolism", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate acetylator", "magnitude": 1},
            "CT": {"status": "intermediate", "desc": "Intermediate acetylator", "magnitude": 1},
            "CC": {"status": "slow", "desc": "Slow acetylator — adjust isoniazid, some sulfonamides", "magnitude": 2},
        },
    },
    "rs4880": {
        "gene": "SOD2", "category": "Detoxification",
        "variants": {
            "TT": {"status": "high_activity", "desc": "High SOD2 (Ala/Ala) — efficient mitochondrial antioxidant defense", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate SOD2 — adequate antioxidant defense", "magnitude": 0},
            "CT": {"status": "intermediate", "desc": "Intermediate SOD2 — adequate antioxidant defense", "magnitude": 0},
            "CC": {"status": "reduced", "desc": "Reduced SOD2 (Val/Val) — consider antioxidant-rich diet, CoQ10", "magnitude": 1},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # SKIN & AGING
    # ═══════════════════════════════════════════════════════════════════════════

    "rs2228479": {
        "gene": "MC1R", "category": "Skin",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal melanin production", "magnitude": 0},
            "GA": {"status": "accelerated", "desc": "MC1R variant — accelerated skin aging, use daily SPF 30+", "magnitude": 2},
            "AG": {"status": "accelerated", "desc": "MC1R variant — accelerated skin aging, use daily SPF 30+", "magnitude": 2},
            "AA": {"status": "significantly_accelerated", "desc": "MC1R homozygous — significant photoaging risk, strict sun protection", "magnitude": 3},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # IRON METABOLISM
    # ═══════════════════════════════════════════════════════════════════════════

    "rs1799945": {
        "gene": "HFE", "category": "Iron Metabolism",
        "variants": {
            "CC": {"status": "normal", "desc": "Normal iron metabolism", "magnitude": 0},
            "CG": {"status": "carrier", "desc": "HFE H63D carrier — periodic ferritin monitoring recommended", "magnitude": 1},
            "GC": {"status": "carrier", "desc": "HFE H63D carrier — periodic ferritin monitoring recommended", "magnitude": 1},
            "GG": {"status": "homozygous", "desc": "HFE H63D homozygous — monitor ferritin, avoid iron supplements", "magnitude": 2},
        },
    },
    "rs1800562": {
        "gene": "HFE", "category": "Iron Metabolism",
        "variants": {
            "GG": {"status": "normal", "desc": "No HFE C282Y — normal iron absorption", "magnitude": 0},
            "GA": {"status": "carrier", "desc": "HFE C282Y carrier — hereditary hemochromatosis carrier, monitor ferritin", "magnitude": 2},
            "AG": {"status": "carrier", "desc": "HFE C282Y carrier — hereditary hemochromatosis carrier, monitor ferritin", "magnitude": 2},
            "AA": {"status": "homozygous", "desc": "HFE C282Y homozygous — high hemochromatosis risk, regular phlebotomy may be needed", "magnitude": 4},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # LONGEVITY
    # ═══════════════════════════════════════════════════════════════════════════

    "rs1042522": {
        "gene": "TP53", "category": "Longevity",
        "variants": {
            "GG": {"status": "pro72", "desc": "TP53 Pro72 — more efficient cell cycle arrest", "magnitude": 0},
            "GC": {"status": "intermediate", "desc": "TP53 Pro72Arg — balanced apoptosis/arrest", "magnitude": 0},
            "CG": {"status": "intermediate", "desc": "TP53 Pro72Arg — balanced apoptosis/arrest", "magnitude": 0},
            "CC": {"status": "arg72", "desc": "TP53 Arg72 — more efficient apoptosis", "magnitude": 1},
        },
    },
    "rs5882": {
        "gene": "CETP", "category": "Longevity",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal CETP — standard HDL/LDL transfer", "magnitude": 0},
            "GA": {"status": "favorable", "desc": "CETP I405V het — favorable HDL profile, longevity association", "magnitude": 1},
            "AG": {"status": "favorable", "desc": "CETP I405V het — favorable HDL profile, longevity association", "magnitude": 1},
            "AA": {"status": "very_favorable", "desc": "CETP I405V hom — higher HDL, strong longevity association", "magnitude": 1},
        },
    },
    # APOE: isoform determined by rs429358 + rs7412 combined (see analyzer.py determine_apoe)
    # The curated SNP database shows these individually but the analyzer resolves the combined isoform
    "rs429358": {
        "gene": "APOE", "category": "Longevity",
        "variants": {
            "TT": {"status": "no_e4", "desc": "No APOE e4 allele — baseline Alzheimer risk", "magnitude": 0},
            "TC": {"status": "e4_carrier", "desc": "APOE e4 heterozygous — combined isoform determined with rs7412", "magnitude": 3},
            "CT": {"status": "e4_carrier", "desc": "APOE e4 heterozygous — combined isoform determined with rs7412", "magnitude": 3},
            "CC": {"status": "e4e4", "desc": "APOE e4/e4 — ~12-15x risk of late-onset Alzheimer's", "magnitude": 4},
        },
    },
    "rs7412": {
        "gene": "APOE", "category": "Longevity",
        "variants": {
            "CC": {"status": "no_e2", "desc": "No APOE e2 allele — isoform E3 or E4 depending on rs429358", "magnitude": 0},
            "CT": {"status": "e2_carrier", "desc": "APOE e2 heterozygous — protective effect if no e4", "magnitude": 0},
            "TC": {"status": "e2_carrier", "desc": "APOE e2 heterozygous", "magnitude": 0},
            "TT": {"status": "e2e2", "desc": "APOE e2/e2 — reduced Alzheimer risk", "magnitude": 1},
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # ALCOHOL METABOLISM
    # ═══════════════════════════════════════════════════════════════════════════

    "rs1229984": {
        "gene": "ADH1B", "category": "Alcohol",
        "variants": {
            "CC": {"status": "slow", "desc": "Slow ADH1B — alcohol effects last longer", "magnitude": 1},
            "CT": {"status": "intermediate", "desc": "Intermediate alcohol metabolism", "magnitude": 0},
            "TC": {"status": "intermediate", "desc": "Intermediate alcohol metabolism", "magnitude": 0},
            "TT": {"status": "fast", "desc": "Fast ADH1B — rapid alcohol to acetaldehyde conversion (Asian flush link)", "magnitude": 2},
        },
    },
    "rs671": {
        "gene": "ALDH2", "category": "Alcohol",
        "variants": {
            "GG": {"status": "normal", "desc": "Normal ALDH2 — efficient acetaldehyde clearance", "magnitude": 0},
            "GA": {"status": "deficient", "desc": "ALDH2*2 carrier — alcohol flush, increased esophageal cancer risk with drinking", "magnitude": 3},
            "AG": {"status": "deficient", "desc": "ALDH2*2 carrier — alcohol flush, increased cancer risk with alcohol", "magnitude": 3},
            "AA": {"status": "severely_deficient", "desc": "ALDH2*2 homozygous — severe flush, alcohol strongly discouraged", "magnitude": 4},
        },
    },
}
