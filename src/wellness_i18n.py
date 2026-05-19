"""
English translations for all wellness panel SNP texts.

Maps rsid -> {"trait_en": "...", "variants": {genotype: "text_en"}}
Covers all 14 panels: NUTRI, FIT, SKIN, AGING, SENSORY, SLEEP, LONGEVITY,
MENTAL, FOOD, THYROID, EYES, BONES, ALLERGY, AUTOIMMUNE.
"""

# Panel display names in English (maps panel key -> name_full EN)
PANEL_NAMES_EN = {
    "nutri": "Nutrition and Metabolism",
    "fit": "Physical Fitness",
    "skin": "Skin and Dermatology",
    "aging": "Aging and Longevity",
    "sensory": "Sensory Perception",
    "sleep": "Sleep and Chronobiology",
    "longevity": "Longevity",
    "mental": "Mental Health and Neurochemistry",
    "food": "Food Sensitivities",
    "thyroid": "Thyroid",
    "eyes": "Eye Health",
    "bones": "Bone Health",
    "allergy": "Atopic Predisposition and Allergies",
    "autoimmune": "Autoimmune Predisposition",
    "body_chemistry": "Body Chemistry (sweat, earwax, odor)",
}


WELLNESS_EN = {
    # ═══════════════════════════════════════════════════════════════════════════
    # NUTRI — Nutrition and Metabolism
    # ═══════════════════════════════════════════════════════════════════════════
    "rs1801133": {
        "trait_en": "Folate Metabolism",
        "variants": {
            "GG": "Normal folic acid to methylfolate conversion. Standard folic acid supplementation is effective.",
            "AG": "~35% reduction in folic acid conversion. Prefer methylfolate (L-5-MTHF) over synthetic folic acid.",
            "GA": "~35% reduction in folic acid conversion. Prefer methylfolate (L-5-MTHF).",
            "AA": "~70% reduction in MTHFR activity. Use methylfolate instead of folic acid. Monitor homocysteine.",
        },
    },
    "rs4988235": {
        "trait_en": "Lactose Tolerance",
        "variants": {
            "TT": "Lactase persistence — you tolerate lactose normally throughout life.",
            "TC": "One persistence copy — likely lactose tolerant.",
            "CT": "One persistence copy — likely lactose tolerant.",
            "CC": "Genetic lactose intolerance. Fermented dairy (yogurt, aged cheeses) is generally tolerated. Consider lactase enzyme.",
        },
    },
    "rs174547": {
        "trait_en": "Omega-3 Conversion",
        "variants": {
            "TT": "Good conversion of ALA (flaxseed, chia) to EPA/DHA. Plant-based omega-3 sources are effective.",
            "TC": "Moderate conversion. Include fatty fish or fish oil/algae supplement.",
            "CT": "Moderate conversion. Include fatty fish or fish oil/algae supplement.",
            "CC": "Poor ALA to EPA/DHA conversion. Plant sources are insufficient — use fish oil or algae (1-2g EPA+DHA/day).",
        },
    },
    "rs2282679": {
        "trait_en": "Vitamin D",
        "variants": {
            "GG": "Normal vitamin D binding protein levels. Sun exposure and diet are generally sufficient.",
            "GT": "Tendency toward lower vitamin D levels. Supplement 2000-4000 IU/day of D3.",
            "TG": "Tendency toward lower vitamin D levels. Supplement 2000-4000 IU/day of D3.",
            "TT": "Strong predisposition to vitamin D deficiency. Supplement 4000-5000 IU/day of D3. Test 25-OH-D.",
        },
    },
    "rs5082": {
        "trait_en": "Saturated Fat Sensitivity",
        "variants": {
            "GG": "Normal response to saturated fat. A balanced diet is sufficient.",
            "GA": "Moderate sensitivity to saturated fat.",
            "AG": "Moderate sensitivity to saturated fat.",
            "AA": "High sensitivity — saturated fat correlates more strongly with weight gain. Limit butter, fatty meat, coconut. Prefer olive oil, avocado, nuts.",
        },
    },
    "rs7903146": {
        "trait_en": "Type 2 Diabetes Risk",
        "variants": {
            "CC": "Normal risk of type 2 diabetes.",
            "CT": "1.4x increased risk. Monitor blood glucose and HbA1c annually. Low refined sugar diet.",
            "TC": "1.4x increased risk. Monitor blood glucose and HbA1c annually.",
            "TT": "2x increased risk. Annual HbA1c mandatory. Low-glycemic diet, regular exercise, weight control.",
        },
    },
    "rs11568820": {
        "trait_en": "Beta-carotene to Vitamin A Conversion",
        "variants": {
            "GG": "Good conversion of beta-carotene (carrots, sweet potato) to active vitamin A.",
            "GA": "Reduced conversion. Include preformed sources: eggs, liver, fish.",
            "AG": "Reduced conversion. Include preformed vitamin A sources.",
            "AA": "Poor conversion. Do not rely solely on vegetables for vitamin A — consume eggs, liver, dairy.",
        },
    },
    "rs762551": {
        "trait_en": "Caffeine Metabolism",
        "variants": {
            "AA": "Fast caffeine metabolizer. Can tolerate coffee without increased cardiovascular risk.",
            "AC": "Intermediate metabolizer. Caffeine persists ~5-6h. Limit to morning hours.",
            "CA": "Intermediate metabolizer. Limit caffeine to morning hours.",
            "CC": "Slow metabolizer. Caffeine persists 8-12h. Increased cardiovascular risk with high intake. Maximum 1 cup/day, morning only.",
        },
    },
    "rs1229984": {
        "trait_en": "Alcohol Metabolism",
        "variants": {
            "CC": "Slow alcohol metabolism — effects last longer. Moderation recommended.",
            "CT": "Intermediate alcohol metabolism.",
            "TC": "Intermediate alcohol metabolism.",
            "TT": "Fast metabolism — converts alcohol to acetaldehyde rapidly. Combined with slow ALDH2, causes flushing.",
        },
    },
    "rs671": {
        "trait_en": "Alcohol Tolerance",
        "variants": {
            "GG": "Normal acetaldehyde clearance. Standard alcohol tolerance.",
            "GA": "ALDH2 deficient — acetaldehyde accumulates (flushing, nausea). Increased risk of esophageal cancer with regular alcohol consumption.",
            "AG": "ALDH2 deficient — increased risk of esophageal cancer with alcohol. Minimize consumption.",
            "AA": "Severely ALDH2 deficient. Alcohol strongly discouraged — significant cancer risk.",
        },
    },
    "rs1799945": {
        "trait_en": "Iron Absorption",
        "variants": {
            "CC": "Normal iron absorption.",
            "CG": "HFE H63D carrier — slightly increased absorption. Monitor ferritin. Avoid unnecessary iron supplements.",
            "GC": "HFE H63D carrier — monitor ferritin periodically.",
            "GG": "HFE H63D homozygous — risk of iron accumulation. Monitor ferritin annually. Donate blood if ferritin is elevated.",
        },
    },
    "rs1800562": {
        "trait_en": "Hereditary Hemochromatosis",
        "variants": {
            "GG": "No C282Y variant. Normal iron absorption.",
            "GA": "HFE C282Y carrier — risk of hemochromatosis if combined with H63D. Monitor ferritin.",
            "AG": "HFE C282Y carrier — monitor ferritin.",
            "AA": "HFE C282Y homozygous — high risk of hemochromatosis. Phlebotomy may be necessary. Consult a hematologist.",
        },
    },
    "rs7946": {
        "trait_en": "Choline Requirement",
        "variants": {
            "CC": "Adequate endogenous phosphatidylcholine production.",
            "CT": "Reduced production. Increase dietary choline: eggs (2/day = ~300mg), liver, fish.",
            "TC": "Reduced choline production. Increase egg and liver consumption.",
            "TT": "Significantly reduced production. Consider choline supplement (250-500mg CDP-choline or phosphatidylcholine).",
        },
    },
    "rs1802059": {
        "trait_en": "Vitamin B12 Recycling",
        "variants": {
            "GG": "Efficient B12 (methylcobalamin) recycling.",
            "GA": "Reduced recycling. Use methylcobalamin instead of cyanocobalamin.",
            "AG": "Reduced B12 recycling.",
            "AA": "Significantly reduced recycling. Use sublingual methylcobalamin 1000-5000mcg. Test B12 and methylmalonic acid.",
        },
    },
    "rs4880": {
        "trait_en": "Antioxidant Defense",
        "variants": {
            "TT": "High SOD2 activity — efficient mitochondrial antioxidant defense.",
            "TC": "Intermediate SOD2 activity — adequate defense.",
            "CT": "Intermediate SOD2 activity.",
            "CC": "Reduced SOD2 activity. Diet rich in antioxidants (berries, colorful vegetables). Consider CoQ10.",
        },
    },
    "rs1800795": {
        "trait_en": "Baseline Inflammation",
        "variants": {
            "CC": "Normal IL-6 levels.",
            "CG": "Intermediate IL-6 levels.",
            "GC": "Intermediate IL-6 levels.",
            "GG": "Elevated baseline IL-6. Anti-inflammatory diet: omega-3, vegetables, turmeric. Adequate sleep is essential (sleep deprivation raises IL-6).",
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # FIT — Physical Fitness
    # ═══════════════════════════════════════════════════════════════════════════
    "rs1815739": {
        "trait_en": "Muscle Fiber Type",
        "variants": {
            "CC": "Alpha-actinin-3 present — fast-twitch fibers. Advantage in explosive activities: sprinting, jumping, heavy weightlifting.",
            "CT": "Mixed profile — versatile for both power and endurance. Responds well to varied training.",
            "TC": "Mixed profile — versatile for power and endurance.",
            "TT": "No alpha-actinin-3 — favors endurance. Advantage in long-distance running, cycling, swimming.",
        },
    },
    "rs8192678": {
        "trait_en": "Mitochondrial Biogenesis",
        "variants": {
            "CC": "Normal PGC-1alpha — good capacity to generate new mitochondria with exercise.",
            "CT": "Reduced PGC-1alpha. Aerobic exercise is even more important for you — it stimulates mitochondrial biogenesis.",
            "TC": "Reduced PGC-1alpha. Prioritize aerobic training.",
            "TT": "Significantly reduced PGC-1alpha. Regular aerobic training is essential for maintaining mitochondrial health. HIIT may be particularly beneficial.",
        },
    },
    "rs1042713": {
        "trait_en": "Fat Burning During Exercise",
        "variants": {
            "GG": "ADRB2 Gly16 — excellent fat mobilization during exercise. Cardio and HIIT are particularly effective for body composition.",
            "GA": "Moderate fat mobilization during exercise.",
            "AG": "Moderate fat mobilization.",
            "AA": "Standard fat mobilization. Resistance training can complement cardio for body composition.",
        },
    },
    "rs6265": {
        "trait_en": "Neuroplasticity and Exercise",
        "variants": {
            "CC": "BDNF Val66Val — normal neurotrophic factor production. Exercise potentiates cognition normally.",
            "CT": "BDNF Val66Met — reduced production. Exercise is ESSENTIAL to compensate — it is the best natural BDNF stimulator.",
            "TC": "Reduced BDNF. Regular exercise is crucial for neuroplasticity.",
            "TT": "BDNF Met66Met — significantly reduced production. Prioritize daily exercise, continuous learning, and social interaction. Aerobic exercise 5x/week.",
        },
    },
    "rs4680": {
        "trait_en": "Recovery and Stress",
        "variants": {
            "GG": "Fast COMT (Val/Val) — 'warrior'. Dopamine clears quickly. Stress resilient but may need more stimulation for focus. Supports high-intensity training.",
            "GA": "Intermediate COMT — balance between focus and resilience. Good profile for varied training.",
            "AG": "Intermediate COMT.",
            "AA": "Slow COMT (Met/Met) — 'strategist'. High baseline focus but stress-sensitive. Overtraining more likely. Include yoga, meditation, and periodize rest.",
        },
    },
    "rs1799971": {
        "trait_en": "Pain Response and Endorphins",
        "variants": {
            "AA": "Normal opioid receptor. Standard endorphin response to exercise.",
            "AG": "Altered opioid receptor. May need more exercise to feel 'runner's high'. Inform anesthesiologist before surgeries.",
            "GA": "Altered receptor. Analgesic dosing may need adjustment.",
            "GG": "Significantly altered receptor. Inform all physicians about this genotype before analgesic prescriptions.",
        },
    },
    "rs5443": {
        "trait_en": "Weight Gain Tendency",
        "variants": {
            "CC": "Normal G-protein signaling. Weight responds normally to diet and exercise.",
            "CT": "GNB3 C825T — slightly increased tendency for weight gain. Regular exercise is particularly important.",
            "TC": "Slightly increased tendency for weight gain.",
            "TT": "GNB3 C825T homozygous — greater tendency for weight gain and hypertension. Regular aerobic exercise and dietary control are essential.",
        },
    },
    "rs699": {
        "trait_en": "Blood Pressure and Exercise",
        "variants": {
            "CC": "Normal angiotensinogen levels.",
            "CT": "AGT M235T — slight tendency toward elevated blood pressure. Aerobic exercise helps regulate.",
            "TC": "Slight tendency toward elevated blood pressure.",
            "TT": "AGT M235T homozygous — increased risk of hypertension. 150+ min/week of aerobic exercise. Monitor blood pressure.",
        },
    },
    "rs5186": {
        "trait_en": "Angiotensin Receptor and Exercise",
        "variants": {
            "AA": "Normal AGTR1 receptor.",
            "AC": "Increased AGTR1 — higher risk of hypertension. Aerobic exercise and sodium restriction are beneficial.",
            "CA": "Increased AGTR1. Monitor blood pressure.",
            "CC": "High AGTR1 — blood pressure monitoring essential. Regular aerobic exercise as first-line prevention.",
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # SKIN — Skin and Dermatology
    # ═══════════════════════════════════════════════════════════════════════════
    "rs2228479": {
        "trait_en": "Photoaging",
        "variants": {
            "GG": "Normal melanin production. Standard skin aging with adequate sun protection.",
            "GA": "MC1R V92M — accelerated skin aging. Use SPF 30+ sunscreen daily. Consider topical retinoids and vitamin C serum.",
            "AG": "Accelerated skin aging. Daily SPF 30+.",
            "AA": "MC1R homozygous — significant photoaging. SPF 50+ mandatory. Avoid prolonged sun exposure. Topical retinoids + antioxidants recommended.",
        },
    },
    # rs1800795 in SKIN context (IL6 - Skin Inflammation)
    # Note: rsid already defined in NUTRI; in the actual panel the trait differs.
    # The SKIN-specific texts are provided here as overrides would need panel context.
    # Since we map rsid globally, we use the NUTRI version above.
    # The skin-specific trait/texts for rs1800795:
    #   trait: "Skin Inflammation"
    #   GG: "Tendency toward elevated skin inflammation. Anti-inflammatory diet benefits the skin. Omega-3 and essential fatty acids help. Avoid ultra-processed foods."
    # (Handled via panel-level lookup in the app; this dict uses last-write-wins for shared rsids)

    # rs4880 in SKIN context (SOD2 - Skin Antioxidant Protection)
    # rs2282679 in SKIN context (GC - Vitamin D and Skin Health)
    # rs1801133 in SKIN context (MTHFR - Collagen and Methylation)
    # These share rsids with NUTRI. See note above.

    # ═══════════════════════════════════════════════════════════════════════════
    # AGING — Aging and Longevity
    # ═══════════════════════════════════════════════════════════════════════════
    "rs429358": {
        "trait_en": "Alzheimer's Risk (partial — see conclusions for full isoform)",
        "variants": {
            "TT": "No APOE e4 allele (rs429358=TT). Baseline risk. See rs7412 for full isoform (E2 or E3).",
            "TC": "APOE e4 heterozygous (rs429358=TC). If rs7412=CC -> E3/E4 (~3x Alzheimer's risk). If rs7412=CT -> E2/E4 (mixed risks). See conclusions for combined result.",
            "CT": "APOE e4 heterozygous (rs429358=CT). See conclusions for full isoform with rs7412.",
            "CC": "APOE e4/e4 (rs429358=CC). ~12-15x Alzheimer's risk. Aggressive prevention: daily exercise, Mediterranean diet, sleep, cardiovascular control. Consult a neurologist.",
        },
    },
    "rs5882": {
        "trait_en": "Lipid Profile and Longevity",
        "variants": {
            "GG": "Normal cholesterol transfer between lipoproteins.",
            "GA": "CETP I405V — tendency toward higher HDL. Associated with exceptional longevity in studies. Protective factor.",
            "AG": "CETP I405V — favorable lipid profile.",
            "AA": "CETP I405V homozygous — elevated HDL, strong association with longevity. Continue maintaining a healthy lifestyle.",
        },
    },
    # rs6265 in AGING context (BDNF - Brain Health in Aging)
    # rs1800795 in AGING context (IL6 - Chronic Inflammation and Aging)
    # rs4880 in AGING context (SOD2 - Oxidative Stress and Aging)
    # rs2228479 in AGING context (MC1R - Skin Aging)
    # These share rsids with panels above.

    # ═══════════════════════════════════════════════════════════════════════════
    # SENSORY — Sensory Perception
    # ═══════════════════════════════════════════════════════════════════════════
    "rs713598": {
        "trait_en": "Bitter Taste Sensitivity",
        "variants": {
            "GG": "Average taster — perceives bitterness moderately. Broccoli, coffee, and IPA beer taste standard.",
            "GC": "Partial super-taster — increased bitter sensitivity. May reject cruciferous vegetables (broccoli, kale) and strong coffee.",
            "CG": "Increased bitter sensitivity. Tendency to reject broccoli and strong coffee.",
            "CC": "Super-taster — intense bitterness. Broccoli, arugula, black coffee, and IPA beer may be intolerable. Cooking vegetables and adding fat reduces bitterness.",
        },
    },
    "rs72921001": {
        "trait_en": "Cilantro Perception",
        "variants": {
            "CC": "Normal cilantro perception — herbaceous flavor pleasant for most.",
            "CA": "Carrier of the 'soap' allele — may perceive cilantro as soapy or metallic. About 14% of the population has this variant.",
            "AC": "May perceive cilantro as soapy.",
            "AA": "Strong soapy taste perception from cilantro. Substitute with parsley, chives, or basil in recipes.",
        },
    },
    "rs2274333": {
        "trait_en": "Umami and Flavor Perception",
        "variants": {
            "AA": "Normal gustin (salivary protein) production. Standard flavor perception.",
            "AG": "Reduced gustin production — flavor sensitivity may be lower. May prefer more heavily seasoned foods.",
            "GA": "Reduced flavor sensitivity.",
            "GG": "Significantly reduced gustin production. May need more seasoning to perceive flavors. Tendency to prefer saltier/spicier foods.",
        },
    },
    "rs4481887": {
        "trait_en": "Asparagus Urine Odor Detection",
        "variants": {
            "GG": "Can detect the characteristic asparagus odor in urine. About 40% of people cannot.",
            "GA": "Intermediate asparagus odor detection.",
            "AG": "Intermediate asparagus odor detection.",
            "AA": "Cannot detect asparagus odor in urine — specific anosmia. Genetic curiosity with no clinical impact.",
        },
    },
    "rs10246939": {
        "trait_en": "Glucosinolate Sensitivity",
        "variants": {
            "CC": "Standard perception of glucosinolates (bitter compounds in broccoli, Brussels sprouts, cabbage).",
            "CT": "Increased glucosinolate sensitivity. May avoid cruciferous vegetables, which are rich in anti-cancer compounds.",
            "TC": "Increased sensitivity. Cooking reduces the bitterness of cruciferous vegetables.",
            "TT": "High sensitivity. Try preparing cruciferous vegetables roasted with olive oil and garlic — heat destroys some of the bitter glucosinolates while retaining the benefits.",
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # SLEEP — Sleep and Chronobiology
    # ═══════════════════════════════════════════════════════════════════════════
    "rs1801260": {
        "trait_en": "Chronotype (Owl vs Lark)",
        "variants": {
            "AA": "Standard chronotype — not strongly morning nor evening. A regular routine helps maintain a healthy rhythm.",
            "AG": "Moderate evening tendency ('owl' chronotype). May have difficulty falling asleep early. Morning sunlight exposure helps recalibrate.",
            "GA": "Moderate evening tendency.",
            "GG": "Strong evening tendency — genetic 'night owl'. Difficulty with morning schedules is likely. Bright morning sunlight (10-15min) and avoiding screens at night are essential.",
        },
    },
    "rs2305160": {
        "trait_en": "Circadian Phase",
        "variants": {
            "CC": "Standard circadian rhythm duration (~24h). Regular sleep phase.",
            "CT": "Slightly advanced circadian phase — may feel sleepy earlier and wake earlier naturally.",
            "TC": "Slightly advanced circadian phase.",
            "TT": "Advanced sleep phase syndrome — tendency to sleep and wake very early. If bothersome, bright light in the late afternoon can delay the biological clock.",
        },
    },
    "rs57875989": {
        "trait_en": "Sleep Need (Short Sleeper)",
        "variants": {
            "CC": "Standard sleep need — 7-9 hours for optimal functioning.",
            "CT": "Carrier of short sleep variant — may function well with 6-6.5 hours of sleep. Rare variant identified in families of 'natural short sleepers'.",
            "TC": "Possible natural short sleeper.",
            "TT": "Genetic natural short sleeper — may feel fully recovered with ~6 hours. Extremely rare.",
        },
    },
    "rs73598374": {
        "trait_en": "Deep Sleep Efficiency",
        "variants": {
            "CC": "Normal adenosine metabolism — standard sleep pressure buildup and deep sleep quality.",
            "CT": "Altered adenosine metabolism — may have more intense and restorative deep sleep. Tendency to sleep more deeply.",
            "TC": "Potentially more intense deep sleep.",
            "TT": "Very intense deep sleep — significantly altered adenosine metabolism. Waking may be more difficult, but sleep is more restorative.",
        },
    },
    "rs4753426": {
        "trait_en": "Melatonin Sensitivity",
        "variants": {
            "CC": "Standard melatonin receptor. Circadian rhythm responds normally to darkness.",
            "CT": "Altered melatonin receptor — may need more darkness to initiate sleep. Also associated with metabolic risk if eating late.",
            "TC": "Altered melatonin receptor. Avoid eating 2-3h before bedtime.",
            "TT": "Significantly altered melatonin receptor. Total blackout in the bedroom, avoid screens 1h before bed. Do not eat after 8pm — increased metabolic risk.",
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # LONGEVITY — Longevity
    # ═══════════════════════════════════════════════════════════════════════════
    "rs2802292": {
        "trait_en": "Longevity Gene",
        "variants": {
            "TT": "Standard FOXO3 variant. Longevity depends primarily on lifestyle.",
            "TG": "Carrier of the FOXO3 longevity allele — associated with longer life in multiple populations (Japanese, German, American). Protective factor.",
            "GT": "Carrier of the FOXO3 longevity allele.",
            "GG": "Homozygous for the FOXO3 longevity allele — strong association with centenarian life in global studies. FOXO3 regulates DNA repair, autophagy, and oxidative stress resistance.",
        },
    },
    # rs5882 already defined in AGING section above (CETP)
    "rs1042522": {
        "trait_en": "DNA Repair Efficiency",
        "variants": {
            "GG": "p53 Pro72 — slightly slower apoptosis, but better DNA repair. Slightly associated with greater longevity.",
            "GC": "p53 heterozygous — balance between repair efficiency and damage response.",
            "CG": "Balance between apoptosis and repair.",
            "CC": "p53 Arg72 — more efficient apoptosis (eliminates damaged cells faster). Better chemotherapy response if needed.",
        },
    },
    "rs4420638": {
        "trait_en": "APOE Longevity Cluster",
        "variants": {
            "AA": "Protective variant in the APOE cluster — associated with lower Alzheimer's risk and greater longevity.",
            "AG": "Intermediate profile in the APOE longevity cluster.",
            "GA": "Intermediate profile.",
            "GG": "Risk variant in the APOE cluster. Regular exercise, Mediterranean diet, and cardiovascular control are especially important for you.",
        },
    },
    "rs2069837": {
        "trait_en": "Inflammation and Healthy Aging",
        "variants": {
            "AA": "Standard IL-6 level. Normal-paced inflammaging.",
            "AG": "Reduced IL-6 production — less inflammaging. Positive factor for healthy aging.",
            "GA": "Lower chronic inflammation — favors longevity.",
            "GG": "Significantly reduced IL-6. Excellent anti-inflammatory profile for healthy aging.",
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # MENTAL — Mental Health and Neurochemistry
    # ═══════════════════════════════════════════════════════════════════════════
    "rs25531": {
        "trait_en": "Serotonin Transporter",
        "variants": {
            "AA": "High serotonin transporter expression (long 5-HTTLPR). Greater resilience to emotional stress and lower risk of reactive depression.",
            "AG": "Intermediate expression — moderate sensitivity to emotional stress. Social support network and physical activity help maintain balance.",
            "GA": "Moderate sensitivity to emotional stress.",
            "GG": "Low 5-HTT expression — greater sensitivity to negative experiences. Regular exercise, meditation, and cognitive-behavioral therapy are particularly beneficial. Seek professional support when needed.",
        },
    },
    # rs4680 already defined in FIT section above (COMT)
    # rs6265 already defined in FIT section above (BDNF)
    "rs1800497": {
        "trait_en": "Dopamine Receptors and Reward",
        "variants": {
            "GG": "Normal D2 dopamine receptor density. Balanced reward system.",
            "GA": "DRD2 Taq1A — lower receptor density. May seek more stimulation (coffee, social media, gaming). Exercise and creative hobbies satisfy this need in a healthy way.",
            "AG": "Lower dopamine receptor density. Increased reward seeking.",
            "AA": "Significantly reduced D2 density. Greater vulnerability to compulsive behaviors (social media, gaming, shopping). Regular exercise and structured routines are protective. Seek support if you notice compulsive patterns.",
        },
    },
    "rs53576": {
        "trait_en": "Oxytocin Receptor and Empathy",
        "variants": {
            "GG": "High oxytocin sensitivity — strong tendency toward empathy, social bonding, and trust. Social relationships are very important for your well-being.",
            "GA": "Intermediate oxytocin sensitivity — balance between empathy and emotional autonomy.",
            "AG": "Intermediate oxytocin sensitivity.",
            "AA": "Lower oxytocin sensitivity — may perceive fewer social cues and have less need for physical contact. Not 'better' or 'worse', simply different. Can be advantageous in situations requiring objectivity.",
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # FOOD — Food Sensitivities
    # ═══════════════════════════════════════════════════════════════════════════
    "rs2187668": {
        "trait_en": "Celiac Disease Predisposition",
        "variants": {
            "CC": "No HLA-DQ2.5 allele — very low risk of celiac disease. Can consume gluten normally.",
            "CT": "HLA-DQ2.5 carrier — genetic predisposition to celiac disease. Does NOT mean you have celiac (~3% of carriers develop it). If gastrointestinal symptoms, get anti-transglutaminase serology.",
            "TC": "HLA-DQ2.5 carrier. Predisposition, not diagnosis.",
            "TT": "HLA-DQ2.5 homozygous — significantly increased risk of celiac disease. Anti-transglutaminase IgA serology recommended. If positive, duodenal biopsy confirms. Do NOT remove gluten from diet before testing — it invalidates the result.",
        },
    },
    "rs7775228": {
        "trait_en": "Celiac Type 2 (HLA-DQ8)",
        "variants": {
            "CC": "No HLA-DQ8 risk allele. Low additional celiac risk via this pathway.",
            "CT": "HLA-DQ8 carrier — additional celiac predisposition (5-10% of celiacs are DQ8+ without DQ2). Relevant if DQ2 is also positive.",
            "TC": "HLA-DQ8 carrier.",
            "TT": "HLA-DQ8 homozygous. Combined with DQ2, significantly increases risk. Celiac serology recommended if symptomatic.",
        },
    },
    "rs602662": {
        "trait_en": "Secretor Status (Microbiome and B12)",
        "variants": {
            "GG": "Secretor — produces ABH antigens on mucosal surfaces. Diversified gut microbiome. Absorbs vitamin B12 normally via intrinsic pathway.",
            "GA": "Secretor (one copy) — normal microbiome profile and B12 absorption.",
            "AG": "Secretor. Normal absorption.",
            "AA": "Non-secretor (~20% of population) — different microbiome, may have lower B12 levels and greater norovirus resistance. Monitor B12 and consider supplementation.",
        },
    },
    # rs4988235 already defined in NUTRI section above (MCM6/LCT)
    "rs182549": {
        "trait_en": "Lactase Persistence (European)",
        "variants": {
            "CC": "European lactase persistence allele. Maintains lactase production in adulthood.",
            "CT": "One copy — likely lactose tolerant.",
            "TC": "One persistence copy.",
            "TT": "No European persistence allele. High probability of lactose intolerance in adulthood. Fermented dairy and lactase enzyme are alternatives.",
        },
    },
    # rs1800497 already defined in MENTAL section above (DRD2/ANKK1)
    # In FOOD context the trait is "Compulsive Eating Behavior"

    # ═══════════════════════════════════════════════════════════════════════════
    # THYROID — Thyroid
    # ═══════════════════════════════════════════════════════════════════════════
    "rs965513": {
        "trait_en": "Thyroid Disease Predisposition",
        "variants": {
            "GG": "No FOXE1 risk allele. Standard thyroid disease risk.",
            "GA": "FOXE1 variant carrier — 1.4x risk of hypothyroidism/Hashimoto's. Monitor TSH annually, especially if female.",
            "AG": "FOXE1 carrier. Annual TSH recommended.",
            "AA": "FOXE1 homozygous — ~2x risk of autoimmune thyroid disease. Annual TSH + anti-TPO mandatory. Symptoms: unexplained fatigue, weight gain, dry skin, cold sensitivity.",
        },
    },
    "rs2476601": {
        "trait_en": "Thyroid Autoimmunity (and others)",
        "variants": {
            "GG": "No PTPN22 risk variant. Standard autoimmunity risk.",
            "GA": "PTPN22 R620W variant — increased risk of Hashimoto's thyroiditis, rheumatoid arthritis, and type 1 diabetes. This gene is a central regulator of autoimmunity.",
            "AG": "PTPN22 R620W carrier. Increased autoimmunity risk.",
            "AA": "PTPN22 homozygous — significantly increased risk of multiple autoimmune diseases. Follow-up with endocrinologist and rheumatologist recommended.",
        },
    },
    "rs179247": {
        "trait_en": "TSH Receptor and Graves' Disease",
        "variants": {
            "AA": "Standard TSH receptor. Baseline Graves' disease risk.",
            "AT": "TSH receptor variant — slightly increased risk of hyperthyroidism (Graves'). Watch for: tachycardia, weight loss, tremor, irritability.",
            "TA": "TSHR variant. Watch for hyperthyroidism symptoms.",
            "TT": "Increased Graves' disease risk (autoimmune hyperthyroidism). If symptomatic: TSH + free T4 + TRAb. More common in women aged 20-40.",
        },
    },
    "rs3184504": {
        "trait_en": "Autoimmunity and Thyroid",
        "variants": {
            "CC": "Standard SH2B3 variant. Normal immune regulation.",
            "CT": "SH2B3 rs3184504 — associated with increased risk of Hashimoto's and hypothyroidism. Also linked to celiac disease and type 1 diabetes.",
            "TC": "SH2B3 carrier. Moderate risk.",
            "TT": "SH2B3 homozygous — elevated autoimmune risk profile (thyroid + celiac + T1D). TSH + anti-TPO + anti-tTG recommended.",
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # EYES — Eye Health
    # ═══════════════════════════════════════════════════════════════════════════
    "rs10490924": {
        "trait_en": "Macular Degeneration (AMD) — Main Locus",
        "variants": {
            "GG": "No ARMS2 risk allele. Standard AMD risk.",
            "GT": "ARMS2 A69S carrier — ~2.5x risk of age-related macular degeneration (AMD). Annual fundus exam after age 50. Lutein + zeaxanthin may help.",
            "TG": "ARMS2 carrier. Annual eye exam after age 50.",
            "TT": "ARMS2 homozygous — ~7x AMD risk. Annual fundus exam mandatory after age 40. Supplement AREDS2 (lutein, zeaxanthin, omega-3). Do not smoke — smoking multiplies the risk.",
        },
    },
    "rs1061170": {
        "trait_en": "Complement and AMD",
        "variants": {
            "TT": "CFH Y402H reference. Standard AMD risk.",
            "TC": "CFH Y402H heterozygous — ~2x AMD risk. The complement system contributes to retinal inflammation. Anti-inflammatory diet and UV protection are beneficial.",
            "CT": "CFH carrier. UV protection and anti-inflammatory diet recommended.",
            "CC": "CFH Y402H homozygous — ~5-7x AMD risk. Regular eye exams essential. AREDS2, UV-protective glasses, do not smoke.",
        },
    },
    "rs2285714": {
        "trait_en": "Complement Regulation and AMD",
        "variants": {
            "CC": "Normal complement regulation. No increased risk from this locus.",
            "CT": "CFI variant — additional contribution to AMD risk via complement dysregulation.",
            "TC": "CFI carrier. Contribution to AMD risk.",
            "TT": "CFI homozygous — increased AMD risk. Combined with CFH and ARMS2, total risk may be very high.",
        },
    },
    "rs1048661": {
        "trait_en": "Exfoliation Glaucoma",
        "variants": {
            "GG": "LOXL1 reference. Standard glaucoma risk.",
            "GT": "LOXL1 variant — associated with exfoliation syndrome and glaucoma. Annual intraocular pressure measurement recommended after age 40.",
            "TG": "LOXL1 carrier. Annual ocular pressure measurement.",
            "TT": "LOXL1 homozygous — significantly increased risk of exfoliation glaucoma. Complete annual eye exam (pressure + visual field + OCT).",
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # BONES — Osteoporosis and Bone Health
    # ═══════════════════════════════════════════════════════════════════════════
    "rs2228570": {
        "trait_en": "Vitamin D Receptor and Bone Density",
        "variants": {
            "CC": "VDR FokI CC — efficient calcium absorption. Bone density favored with adequate calcium and vitamin D intake.",
            "CT": "VDR FokI intermediate — calcium absorption may be moderately reduced. Supplement vitamin D3 and ensure 1000mg/day of calcium.",
            "TC": "VDR intermediate. Attention to calcium and vitamin D.",
            "TT": "VDR FokI TT — reduced calcium absorption. Increased osteoporosis risk. Vitamin D3 (2000-4000IU), calcium (1200mg), and weight-bearing exercise are essential.",
        },
    },
    "rs1800012": {
        "trait_en": "Type I Collagen and Fracture Risk",
        "variants": {
            "GG": "COL1A1 reference — normal type I collagen production. Standard bone strength.",
            "GT": "COL1A1 Sp1 — altered collagen production. Slightly increased fracture risk. Weight-bearing exercise (walking, light jogging, weight training) strengthens bones.",
            "TG": "COL1A1 Sp1 carrier. Weight-bearing exercise recommended.",
            "TT": "COL1A1 Sp1 homozygous — significantly increased osteoporosis and fracture risk. Baseline bone densitometry recommended. Weight-bearing exercise + vitamin D + calcium.",
        },
    },
    "rs3736228": {
        "trait_en": "Wnt Pathway and Bone Mass",
        "variants": {
            "CC": "LRP5 reference — normal Wnt pathway for bone formation.",
            "CT": "LRP5 A1330V — reduced Wnt pathway. Lower bone formation. Resistance and weight-bearing exercise are especially important.",
            "TC": "LRP5 carrier. Prioritize resistance exercise.",
            "TT": "LRP5 homozygous — significantly reduced bone formation. Risk of early-onset osteoporosis. Bone densitometry, vitamin D, calcium, and resistance exercise are critical.",
        },
    },
    "rs4870044": {
        "trait_en": "Estrogen Receptor and Bone Mass",
        "variants": {
            "CC": "ESR1 reference — normal estrogen response for bone maintenance.",
            "CT": "ESR1 variant — reduced estrogen response. Postmenopausal women: increased risk of bone loss. Discuss hormone therapy with gynecologist.",
            "TC": "ESR1 carrier. Attention in postmenopause.",
            "TT": "ESR1 homozygous — significantly reduced estrogen response. High postmenopausal osteoporosis risk. Early bone densitometry + hormone therapy evaluation.",
        },
    },
    # rs2282679 already defined in NUTRI section above (GC - Vitamin D)

    # ═══════════════════════════════════════════════════════════════════════════
    # ALLERGY — Atopic Predisposition and Allergies
    # ═══════════════════════════════════════════════════════════════════════════
    "rs7216389": {
        "trait_en": "Asthma Predisposition",
        "variants": {
            "TT": "No risk allele at the 17q21 locus. Standard asthma risk.",
            "TC": "Carrier of the main asthma risk locus (17q21). ~1.4x risk. Particularly relevant if childhood onset. Avoid smoking (active and passive).",
            "CT": "Carrier of asthma risk (17q21). Moderately increased risk.",
            "CC": "Homozygous for the 17q21 locus — significantly increased asthma risk, especially early-onset. If respiratory symptoms: spirometry with bronchodilator.",
        },
    },
    "rs20541": {
        "trait_en": "IgE Production and Atopy",
        "variants": {
            "GG": "Standard IL-13. Normal IgE production. Baseline atopy risk.",
            "GA": "IL-13 R130Q — increased IgE production. Predisposition to allergic rhinitis, atopic dermatitis, and asthma. Antihistamines may be needed more frequently.",
            "AG": "IL-13 variant. Increased atopic tendency.",
            "AA": "IL-13 R130Q homozygous — significantly elevated IgE production. Strongly atopic profile. An allergist can help with preventive management (immunotherapy, environmental control).",
        },
    },
    "rs2228145": {
        "trait_en": "Allergic Inflammation and Eczema",
        "variants": {
            "AA": "Standard IL-6R. Normal inflammatory signaling.",
            "AC": "IL-6R D358A — altered inflammatory signaling. May influence atopic dermatitis and cutaneous inflammatory response. Skin hydration and emollients help.",
            "CA": "IL-6R variant. Attention to cutaneous inflammation.",
            "CC": "IL-6R D358A homozygous — paradoxically protective for some inflammatory diseases (rheumatoid arthritis). Complex inflammatory profile.",
        },
    },
    "rs1800925": {
        "trait_en": "Allergic Rhinitis",
        "variants": {
            "CC": "Normal IL-13 expression. Standard allergic rhinitis risk.",
            "CT": "Altered IL-13 promoter — increased expression. Predisposition to seasonal and perennial allergic rhinitis. Environmental control (dust mites, pollen) is important.",
            "TC": "Increased IL-13 expression. Tendency toward allergic rhinitis.",
            "TT": "Significantly elevated IL-13 expression. High-risk profile for chronic allergic rhinitis. Immunotherapy (allergy shots) may be discussed with an allergist.",
        },
    },
    "rs10156191": {
        "trait_en": "Histamine Degradation (DAO)",
        "variants": {
            "CC": "Normal diamine oxidase (DAO) activity. Degrades dietary histamine efficiently.",
            "CT": "Reduced DAO activity — may have histamine intolerance: headaches, urticaria, nasal congestion after fermented foods, wine, aged cheeses. Try a low-histamine diet for 2-4 weeks as a test.",
            "TC": "Reduced DAO. Attention to histamine-rich foods.",
            "TT": "Significantly reduced DAO — histamine intolerance likely. Avoid: red wine, aged cheeses, cured meats, fermented foods, canned fish. DAO supplement before meals may help (discuss with physician).",
        },
    },
    "rs1049793": {
        "trait_en": "Histamine Metabolism (HNMT)",
        "variants": {
            "CC": "Normal histamine methylation via HNMT. Efficient histamine processing in the central nervous system.",
            "CG": "Reduced HNMT — slower brain histamine metabolism. May influence sleep, anxiety, and sensitivity to histamine-rich foods.",
            "GC": "HNMT variant. Reduced histamine metabolism.",
            "GG": "Significantly reduced HNMT. Combined with low DAO, creates a high histamine sensitivity profile. Low-histamine diet and environmental control can make a significant difference.",
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTOIMMUNE — Autoimmune Predisposition
    # ═══════════════════════════════════════════════════════════════════════════
    # rs2476601 already defined in THYROID section above (PTPN22)
    "rs7574865": {
        "trait_en": "Lupus and Rheumatoid Arthritis",
        "variants": {
            "GG": "Standard STAT4. Baseline risk of lupus and rheumatoid arthritis.",
            "GT": "STAT4 variant — ~1.5x risk of systemic lupus erythematosus (SLE) and rheumatoid arthritis. More relevant in women (lupus affects women 9x more).",
            "TG": "STAT4 carrier. Predisposition to lupus.",
            "TT": "STAT4 homozygous — ~2x lupus risk. If symptoms (joint pain, facial rash, fatigue, photosensitivity): ANA and anti-DNA testing. Lupus is treatable if diagnosed early.",
        },
    },
    "rs2241880": {
        "trait_en": "Crohn's Disease / IBD",
        "variants": {
            "AA": "Standard ATG16L1. Normal intestinal autophagy.",
            "AG": "ATG16L1 T300A — altered intestinal autophagy. ~1.4x Crohn's disease risk. Anti-inflammatory diet and probiotics may help. If chronic gastrointestinal symptoms: investigate IBD.",
            "GA": "ATG16L1 carrier. Predisposition to Crohn's disease.",
            "GG": "ATG16L1 T300A homozygous — increased Crohn's risk. Watch for chronic diarrhea, abdominal pain, unexplained weight loss. Investigate with colonoscopy if symptoms persist.",
        },
    },
    "rs4349859": {
        "trait_en": "Ankylosing Spondylitis",
        "variants": {
            "GG": "No HLA-B27 marker at this locus. Low ankylosing spondylitis risk.",
            "GA": "HLA-B27-proximal marker positive — strongly associated with ankylosing spondylitis (chronic inflammatory back pain). HLA-B27 has OR ~100x, but only ~5% of carriers develop the disease. If back pain worsens with rest and improves with exercise: investigate with rheumatologist.",
            "AG": "HLA-B27-proximal positive. Investigate if inflammatory back pain.",
            "AA": "Strong HLA-B27 marker. Significant ankylosing spondylitis risk. Chronic low back pain (>3 months, worsens with rest, improves with movement) should be investigated by a rheumatologist.",
        },
    },
    "rs12191877": {
        "trait_en": "Psoriasis",
        "variants": {
            "CC": "No HLA-C risk allele for psoriasis.",
            "CT": "HLA-C risk allele carrier — predisposition to psoriasis (reddish plaques with scales on the skin). Stress is a common trigger. A dermatologist can guide early treatment.",
            "TC": "Carrier of psoriasis risk.",
            "TT": "Increased psoriasis risk. If skin lesions: consult a dermatologist. Psoriasis has effective treatments (biologics, topicals). Also associated with psoriatic arthritis and cardiovascular risk.",
        },
    },
    "rs6897932": {
        "trait_en": "Multiple Sclerosis",
        "variants": {
            "CC": "Standard IL-7R. Baseline multiple sclerosis (MS) risk.",
            "CT": "IL-7R variant — slightly increased multiple sclerosis risk. MS is multifactorial (genetics + Epstein-Barr virus + vitamin D). Maintaining adequate vitamin D levels may be protective.",
            "TC": "IL-7R carrier. Slight MS risk.",
            "TT": "IL-7R homozygous — increased MS risk. If neurological symptoms (tingling, weakness, double vision, extreme fatigue): consult a neurologist. MS is treatable if diagnosed early.",
        },
    },
    "rs6457617": {
        "trait_en": "Rheumatoid Arthritis (Shared Epitope)",
        "variants": {
            "TT": "No HLA-DRB1 shared epitope tag here. Baseline seropositive rheumatoid arthritis risk.",
            "TC": "Carrier of HLA-DRB1 tag (often DRB1*04) — increased seropositive RA risk (OR ~2-3x). If prolonged morning stiffness in hands/wrists or symmetric joint pain: investigate with a rheumatologist (RF, anti-CCP).",
            "CT": "HLA-DRB1 shared epitope carrier. Predisposition to seropositive RA.",
            "CC": "Homozygous HLA-DRB1 shared epitope — significantly increased seropositive RA risk (OR up to ~5x for some combinations). Smoking dramatically multiplies this risk. Early joint symptoms deserve attention — early diagnosis changes prognosis substantially.",
        },
    },
    "rs34536443": {
        "trait_en": "Autoimmune Protection (TYK2 P1104A)",
        "variants": {
            "CC": "Standard TYK2. No additional protective effect against autoimmune disease.",
            "CG": "Carrier of TYK2 P1104A (loss-of-function) — PROTECTIVE against multiple autoimmune conditions: lupus, rheumatoid arthritis, psoriasis, Crohn's disease, ankylosing spondylitis (OR ~0.5-0.7). Slightly less reactive immunity without substantially compromising defense. Carrier frequency ~3-10% in Europeans.",
            "GC": "TYK2 P1104A carrier — partial protection against autoimmune disease.",
            "GG": "Homozygous TYK2 P1104A — stronger autoimmune protection (rare, <1%). The trade-off may be slightly increased susceptibility to mycobacterial and certain viral infections.",
        },
    },
    "rs231775": {
        "trait_en": "Thyroid and Endocrine Autoimmunity (CTLA4 +49 A/G)",
        "variants": {
            "AA": "Standard CTLA4. Baseline risk for Graves' disease, Hashimoto's thyroiditis, type 1 diabetes, vitiligo.",
            "AG": "CTLA4 +49 G variant — ~1.2-1.5x risk for endocrine autoimmunity: Graves' disease (hyperthyroidism), Hashimoto's thyroiditis, type 1 diabetes, vitiligo. Periodic TSH/T4 monitoring worthwhile, especially with thyroid symptoms.",
            "GA": "CTLA4 +49 G carrier. Increased thyroid autoimmunity risk.",
            "GG": "Homozygous CTLA4 +49 G — more consistent risk for endocrine autoimmunity. Annual TSH, anti-TPO, anti-thyroglobulin worth considering. Also fasting glucose if family history of T1D.",
        },
    },
    "rs2004640": {
        "trait_en": "Systemic Lupus Erythematosus (IRF5 / Interferon)",
        "variants": {
            "GG": "Standard IRF5. No lupus risk allele at this locus.",
            "GT": "IRF5 T variant — creates an alternative splice site that boosts IRF5 (interferon regulatory factor 5) expression. ~1.6x risk of systemic lupus erythematosus (SLE). Lupus affects women 9x more often; symptoms: joint pain, butterfly facial rash, fatigue, photosensitivity.",
            "TG": "IRF5 T carrier. Lupus predisposition via the type I interferon pathway.",
            "TT": "Homozygous IRF5 T — increased SLE risk. Combined with STAT4 variants, risk multiplies (additive effect). With compatible symptoms: ANA, anti-dsDNA, complement C3/C4 with a rheumatologist.",
        },
    },
    "rs13277113": {
        "trait_en": "Lupus and B-Lymphocyte Predisposition (BLK)",
        "variants": {
            "GG": "Standard BLK. Normal B-lymphocyte signaling.",
            "GA": "BLK A variant — reduces B-lymphoid tyrosine kinase expression, affecting B-cell activation. ~1.4x lupus risk. Also linked to rheumatoid arthritis and Sjögren syndrome (dry mouth/eyes).",
            "AG": "BLK A carrier. Increased SLE risk.",
            "AA": "Homozygous BLK A — increased risk of lupus and other B-cell-mediated autoimmune disease. Risk compounds when combined with IRF5 or STAT4 variants.",
        },
    },
    "rs1143679": {
        "trait_en": "Lupus (ITGAM R77H, Leukocyte Adhesion)",
        "variants": {
            "GG": "Standard ITGAM. Normal leukocyte adhesion and immune-complex clearance.",
            "GA": "ITGAM R77H variant — alters leukocyte adhesion and immune-complex phagocytosis. ~1.7-2x lupus risk, with stronger effect in European and Hispanic populations. Also associated with lupus nephritis (kidney involvement in SLE).",
            "AG": "ITGAM R77H carrier. Increased SLE risk.",
            "AA": "Homozygous ITGAM R77H — substantial lupus risk in European/Hispanic populations. Watch for renal symptoms (proteinuria, hypertension) in addition to systemic ones — elevated lupus-nephritis risk.",
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # BODY CHEMISTRY — Sweat composition, earwax, axillary odor
    # ═══════════════════════════════════════════════════════════════════════════
    "rs17822931": {
        "trait_en": "Earwax Type and Body Odor",
        "variants": {
            "CC": "Functional ABCC11 alleles — wet earwax and typical apocrine sweat production. Most common profile in European and African populations. Measures sweat composition, not volume.",
            "CT": "Heterozygous — typically wet earwax, normal-to-slightly-reduced apocrine sweat production.",
            "TC": "Heterozygous — typically wet earwax, normal-to-slightly-reduced apocrine sweat production.",
            "TT": "Both alleles non-functional — dry earwax and significantly reduced axillary apocrine sweat (less characteristic body odor). Common in East Asian populations (~80-95%), rare in European (~3%). Does not predict sweating volume, only composition.",
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# Panel-specific overrides for SNPs that appear in multiple panels
# with different trait names and texts.
# Key: (panel_key, rsid) -> {"trait_en": ..., "variants": {...}}
# ═══════════════════════════════════════════════════════════════════════════════

WELLNESS_EN_PANEL_OVERRIDES = {
    # SKIN panel overrides
    ("skin", "rs1800795"): {
        "trait_en": "Skin Inflammation",
        "variants": {
            "CC": "Normal baseline skin inflammation.",
            "CG": "Moderate inflammation.",
            "GC": "Moderate inflammation.",
            "GG": "Tendency toward elevated skin inflammation. Anti-inflammatory diet benefits the skin. Omega-3 and essential fatty acids help. Avoid ultra-processed foods.",
        },
    },
    ("skin", "rs4880"): {
        "trait_en": "Skin Antioxidant Protection",
        "variants": {
            "TT": "High antioxidant protection — cutaneous oxidative stress well managed.",
            "TC": "Adequate antioxidant protection.",
            "CT": "Adequate antioxidant protection.",
            "CC": "Reduced antioxidant protection. Vitamin C serum (L-ascorbic acid 10-20%) and topical vitamin E compensate. Diet rich in antioxidants.",
        },
    },
    ("skin", "rs2282679"): {
        "trait_en": "Vitamin D and Skin Health",
        "variants": {
            "GG": "Adequate vitamin D levels for skin health.",
            "GT": "Tendency toward lower vitamin D — affects skin cell renewal. Supplement D3.",
            "TG": "Lower vitamin D. Supplement D3.",
            "TT": "Likely vitamin D deficiency — impacts skin barrier and renewal. Supplement 4000-5000 IU D3/day.",
        },
    },
    ("skin", "rs1801133"): {
        "trait_en": "Collagen and Methylation",
        "variants": {
            "GG": "Normal methylation — adequate collagen production and cell renewal.",
            "AG": "Reduced methylation may affect long-term collagen synthesis. Methylfolate and B12 help.",
            "GA": "Reduced methylation. Support with methylfolate.",
            "AA": "Significantly reduced methylation — potential impact on collagen production and skin DNA repair. Methylfolate + B12 + choline.",
        },
    },

    # AGING panel overrides
    ("aging", "rs6265"): {
        "trait_en": "Brain Health in Aging",
        "variants": {
            "CC": "Normal BDNF — good baseline neuroplasticity. Exercise and continuous learning maintain brain health.",
            "CT": "Reduced BDNF — more vulnerable to cognitive decline with age. Aerobic exercise is the most potent BDNF stimulator.",
            "TC": "Reduced BDNF. Prioritize exercise and cognitive stimulation.",
            "TT": "Significantly reduced BDNF. Daily exercise, learning new skills, active socialization, and quality sleep are critical for maintaining cognitive health.",
        },
    },
    ("aging", "rs1800795"): {
        "trait_en": "Chronic Inflammation and Aging",
        "variants": {
            "CC": "Normal IL-6 — standard inflammaging progression.",
            "CG": "Intermediate IL-6.",
            "GC": "Intermediate IL-6.",
            "GG": "Elevated IL-6 — accelerated inflammaging. Natural anti-inflammatories: omega-3, turmeric, regular exercise, adequate sleep. Avoid obesity (adipose tissue produces IL-6).",
        },
    },
    ("aging", "rs4880"): {
        "trait_en": "Oxidative Stress and Aging",
        "variants": {
            "TT": "High SOD2 activity — efficient mitochondrial free radical neutralization. Protective factor against aging.",
            "TC": "Intermediate SOD2 — adequate defense against free radicals.",
            "CT": "Intermediate SOD2.",
            "CC": "Reduced SOD2 — greater mitochondrial oxidative damage accumulation. CoQ10 (100-200mg/day), antioxidant-rich diet, and exercise help compensate.",
        },
    },
    ("aging", "rs2228479"): {
        "trait_en": "Skin Aging",
        "variants": {
            "GG": "Standard skin aging.",
            "GA": "Accelerated skin aging. Daily SPF and topical retinoids reduce impact.",
            "AG": "Accelerated skin aging.",
            "AA": "Significantly accelerated skin aging. Strict sun protection + retinoids + topical antioxidants.",
        },
    },

    # LONGEVITY panel overrides for shared rsids
    ("longevity", "rs5882"): {
        "trait_en": "HDL and Exceptional Longevity",
        "variants": {
            "GG": "Standard cholesterol transfer between lipoproteins.",
            "GA": "CETP I405V — tendency toward higher HDL. Associated with exceptional longevity in Ashkenazi centenarian studies.",
            "AG": "Favorable lipid profile for longevity.",
            "AA": "CETP I405V homozygous — consistently elevated HDL. Strong association with exceptional longevity and cardiovascular protection.",
        },
    },

    # MENTAL panel overrides
    ("mental", "rs4680"): {
        "trait_en": "Dopamine Balance",
        "variants": {
            "GG": "Fast COMT (Val/Val) — 'warrior'. Dopamine clears quickly: resilient under pressure, but may seek excessive stimulation. Good in emergency situations.",
            "GA": "Intermediate COMT — balance between sustained focus and stress resilience. Flexible profile.",
            "AG": "Intermediate COMT.",
            "AA": "Slow COMT (Met/Met) — 'strategist'. Elevated dopamine: exceptional focus and superior working memory, but vulnerable to anxiety under pressure. Meditation, yoga, and a calm environment optimize performance.",
        },
    },
    ("mental", "rs6265"): {
        "trait_en": "Neuroplasticity and Mood",
        "variants": {
            "CC": "BDNF Val66Val — normal neurotrophic factor production. Good neuroplasticity and exercise response for mood.",
            "CT": "BDNF Val66Met — reduced production. Aerobic exercise is the most potent BDNF stimulator and should be a priority for mental health. Meditation also helps.",
            "TC": "Reduced BDNF. Exercise is essential for mental health.",
            "TT": "BDNF Met66Met — significantly reduced production. DAILY exercise is critical for maintaining mood and cognition. Consider preventive psychological follow-up.",
        },
    },

    # FOOD panel overrides
    ("food", "rs4988235"): {
        "trait_en": "Lactose Intolerance",
        "variants": {
            "TT": "Lactase persistence — tolerates lactose throughout life. Can consume milk and dairy without restriction.",
            "TC": "One persistence copy — likely lactose tolerant.",
            "CT": "One persistence copy.",
            "CC": "Genetic lactose intolerance — lactase production decreases in adulthood. Fermented dairy (yogurt, kefir, aged cheeses) is generally tolerated. Use lactase enzyme before consuming milk.",
        },
    },
    ("food", "rs1800497"): {
        "trait_en": "Compulsive Eating Behavior",
        "variants": {
            "GG": "Balanced food reward system. Satiety and satisfaction with normal portions.",
            "GA": "Taq1A — lower reward receptor activation from food. May need more food to feel satisfied. Eating slowly and without distractions helps.",
            "AG": "Tendency to eat more to feel satisfaction.",
            "AA": "Significantly reduced reward receptors. Greater risk of emotional eating and binge eating. Mindful eating, pre-portioned servings, and regular exercise as an alternative dopamine source.",
        },
    },

    # AUTOIMMUNE panel overrides
    ("autoimmune", "rs2476601"): {
        "trait_en": "General Autoimmune Predisposition",
        "variants": {
            "GG": "Standard PTPN22. Baseline autoimmune disease risk.",
            "GA": "PTPN22 R620W — variant associated with multiple autoimmune diseases: Hashimoto's thyroiditis, rheumatoid arthritis, lupus, type 1 diabetes. ~1.5-2x risk for each condition individually.",
            "AG": "PTPN22 R620W carrier. Increased autoimmune predisposition.",
            "AA": "PTPN22 R620W homozygous — significantly increased risk of multiple autoimmune diseases. Monitoring TSH, blood glucose, and inflammatory markers recommended.",
        },
    },

    # BONES panel overrides
    ("bones", "rs2282679"): {
        "trait_en": "Vitamin D and Bone Health",
        "variants": {
            "GG": "Normal vitamin D transport. Adequate levels with sun exposure and diet.",
            "GT": "Tendency toward lower vitamin D — affects calcium absorption and bone health. Supplement D3 2000-4000IU/day.",
            "TG": "Reduced vitamin D. Supplement D3.",
            "TT": "Likely vitamin D deficiency — direct impact on bone mineralization. Supplement D3 4000-5000IU/day + monitor 25-OH-D biannually.",
        },
    },
}
