"""
Medical specialty referral catalog for Gene Lens findings.

This module is the single source of truth for "when the AI mentions
finding X, which specialty should it route the user to". It exists for
two reasons:

1. **System prompt grounding.** `format_for_prompt(lang)` renders a short
   bullet block that gets inlined into SYSTEM_PROMPT_PT / SYSTEM_PROMPT_EN
   so the model has a concrete map, not a vague "talk to a doctor".

2. **Future context injection.** When `_build_chat_context` detects a
   high-impact finding in the user's analysis, it can pull the matching
   entry's `notes_pt` / `notes_en` (clinical context + SUS/insurance
   pathway) into the chat context. Not wired yet — the data is here so
   that step is a small refactor when we want it.

Scope: only findings Gene Lens actually surfaces today. Specifically the
15 conditions in `src/hereditary_conditions.py`, the 14 panels in
`src/wellness_panels.py`, and the CYP/VKORC1/TPMT pharmacogenomics
clusters that `analyze_drug_response()` reports.

Adding a new entry: write both `pt` and `en` for every field. CI parity
test fails otherwise.

PT-BR notes mention SUS / convênio dynamics where it materially changes
where the user looks (oncogenética, farmacogenética, painéis raros). For
specialties available at any clínico geral, we keep the note generic.
"""
from __future__ import annotations

from typing import Literal

Lang = Literal["pt", "en"]


# Each entry maps a trigger (a genetic finding family) to the specialty
# the user should look for. Fields are bilingual; `notes_*` is the longer
# context (history-of-disease angle, SUS vs. insurance availability,
# common confounders). `genes` is for future programmatic matching.

SPECIALTY_REFERRALS: list[dict] = [
    # ── Hereditary cancers ──────────────────────────────────────────────
    {
        "key": "hboc_brca",
        "genes": ["BRCA1", "BRCA2", "PALB2", "CHEK2"],
        "trigger": {
            "pt": "BRCA1/2, HBOC, câncer hereditário de mama/ovário",
            "en": "BRCA1/2, HBOC, hereditary breast/ovarian cancer",
        },
        "specialty": {
            "pt": "oncogeneticista ou mastologista (conselheiro genético ANTES, se histórico familiar)",
            "en": "cancer geneticist or breast oncologist (genetic counselor FIRST if family history)",
        },
        "notes": {
            "pt": "SUS: ambulatórios de oncogenética em hospitais universitários (HC-FMUSP, INCA, A.C. Camargo via parcerias com ICESP). Convênio: ANS cobre painel BRCA confirmatório quando critérios NCCN/INCA são atendidos (CA mama <50, CA ovário em qualquer idade, múltiplos casos na família).",
            "en": "Available through cancer centers and academic medical centers. Insurance commonly covers confirmatory BRCA panel when NCCN criteria are met (breast cancer <50, ovarian cancer at any age, multiple family cases).",
        },
    },
    {
        "key": "lynch",
        "genes": ["MLH1", "MSH2", "MSH6", "PMS2", "EPCAM"],
        "trigger": {
            "pt": "Síndrome de Lynch (câncer colorretal/endometrial hereditário)",
            "en": "Lynch syndrome (hereditary colorectal/endometrial cancer)",
        },
        "specialty": {
            "pt": "coloproctologista + oncogeneticista; ginecologista oncológico se mulher",
            "en": "colorectal surgeon + cancer geneticist; gynecologic oncologist if female",
        },
        "notes": {
            "pt": "Rastreio colonoscópico anual a partir dos 20-25 anos quando confirmado. SUS: programa de rastreio em centros de referência (INCA, HC). Convênio: cobertura ANS para colonoscopia frequente com critérios Amsterdam/Bethesda.",
            "en": "Annual colonoscopy from age 20-25 when confirmed. Most insurers cover frequent surveillance when Amsterdam/Bethesda criteria are met.",
        },
    },
    {
        "key": "polyposis_fap",
        "genes": ["APC", "MUTYH"],
        "trigger": {
            "pt": "Polipose hereditária (FAP / MAP)",
            "en": "Hereditary polyposis (FAP / MAP)",
        },
        "specialty": {
            "pt": "coloproctologista com experiência em polipose hereditária + oncogeneticista",
            "en": "colorectal surgeon with hereditary polyposis experience + cancer geneticist",
        },
        "notes": {
            "pt": "Rastreio precoce com retossigmoidoscopia/colonoscopia a partir da adolescência. Procurar centro com cirurgia profilática se FAP clássica confirmada.",
            "en": "Early surveillance with sigmoidoscopy/colonoscopy starting in adolescence. Seek a center with experience in prophylactic surgery if classical FAP is confirmed.",
        },
    },
    {
        "key": "li_fraumeni",
        "genes": ["TP53"],
        "trigger": {
            "pt": "Síndrome de Li-Fraumeni (TP53)",
            "en": "Li-Fraumeni syndrome (TP53)",
        },
        "specialty": {
            "pt": "oncogeneticista (programa de rastreio multiorgão Toronto/INCA)",
            "en": "cancer geneticist (Toronto-style multi-organ surveillance program)",
        },
        "notes": {
            "pt": "Rastreio Toronto: RM corpo total anual, mamografia/RM mama, colonoscopia. Disponível em centros oncológicos universitários.",
            "en": "Toronto protocol: annual whole-body MRI, breast MRI/mammography, colonoscopy. Available at academic cancer centers.",
        },
    },
    {
        "key": "cowden_pten",
        "genes": ["PTEN"],
        "trigger": {
            "pt": "Síndrome de Cowden / hamartoma PTEN",
            "en": "Cowden syndrome / PTEN hamartoma",
        },
        "specialty": {
            "pt": "oncogeneticista + dermatologista (lesões mucocutâneas) + endocrinologista (tireoide)",
            "en": "cancer geneticist + dermatologist (mucocutaneous lesions) + endocrinologist (thyroid)",
        },
        "notes": {
            "pt": "Múltiplos sítios de risco — mama, tireoide, endométrio, cólon. Rastreio combinado necessário.",
            "en": "Multiple-site risk — breast, thyroid, endometrium, colon. Combined surveillance is needed.",
        },
    },
    {
        "key": "men2_paraganglioma",
        "genes": ["RET", "SDHB", "SDHC", "SDHD", "VHL", "MAX"],
        "trigger": {
            "pt": "MEN2 / câncer medular de tireoide / paraganglioma / feocromocitoma",
            "en": "MEN2 / medullary thyroid cancer / paraganglioma / pheochromocytoma",
        },
        "specialty": {
            "pt": "endocrinologista com experiência em tumores endócrinos + cirurgião de cabeça e pescoço",
            "en": "endocrinologist experienced in endocrine tumors + head & neck surgeon",
        },
        "notes": {
            "pt": "MEN2A/B com RET pode indicar tireoidectomia profilática na infância — discussão urgente se confirmado.",
            "en": "MEN2A/B with confirmed RET may warrant prophylactic thyroidectomy in childhood — urgent discussion if confirmed.",
        },
    },
    {
        "key": "melanoma_familial",
        "genes": ["CDKN2A", "CDK4", "BAP1"],
        "trigger": {
            "pt": "Melanoma familiar (CDKN2A)",
            "en": "Familial melanoma (CDKN2A)",
        },
        "specialty": {
            "pt": "dermatologista oncológico com dermatoscopia + oftalmologista (melanoma uveal se BAP1)",
            "en": "dermatologic oncologist with dermoscopy + ophthalmologist (uveal melanoma if BAP1)",
        },
        "notes": {
            "pt": "Mapeamento corporal anual com dermatoscopia. Convênio cobre quando há histórico familiar documentado.",
            "en": "Annual full-body mapping with dermoscopy. Most insurers cover when there's documented family history.",
        },
    },
    {
        "key": "gastric_cdh1",
        "genes": ["CDH1"],
        "trigger": {
            "pt": "Câncer gástrico hereditário difuso (CDH1)",
            "en": "Hereditary diffuse gastric cancer (CDH1)",
        },
        "specialty": {
            "pt": "gastroenterologista oncológico + oncogeneticista + mastologista (CA lobular de mama associado em mulheres)",
            "en": "gastrointestinal oncologist + cancer geneticist + breast oncologist (associated lobular breast cancer in women)",
        },
        "notes": {
            "pt": "Endoscopias seriadas com biópsia. Gastrectomia profilática é discutida em centros especializados quando CDH1 patogênico é confirmado.",
            "en": "Serial endoscopies with biopsy. Prophylactic gastrectomy is discussed at specialized centers when pathogenic CDH1 is confirmed.",
        },
    },
    {
        "key": "renal_hereditary",
        "genes": ["VHL", "FLCN", "FH", "MET"],
        "trigger": {
            "pt": "Câncer renal hereditário (VHL, Birt-Hogg-Dubé, HLRCC)",
            "en": "Hereditary renal cancer (VHL, Birt-Hogg-Dubé, HLRCC)",
        },
        "specialty": {
            "pt": "urologista oncológico + oncogeneticista; nefrologista se função renal alterada",
            "en": "urologic oncologist + cancer geneticist; nephrologist if kidney function is affected",
        },
        "notes": {
            "pt": "RM renal anual a partir dos 18-25 anos. VHL também exige rastreio de hemangioblastomas (SNC) e feocromocitoma.",
            "en": "Annual renal MRI from age 18-25. VHL also requires surveillance for hemangioblastomas (CNS) and pheochromocytoma.",
        },
    },
    {
        "key": "prostate_hereditary",
        "genes": ["HOXB13", "BRCA2"],
        "trigger": {
            "pt": "Câncer hereditário de próstata (HOXB13, BRCA2 em homens)",
            "en": "Hereditary prostate cancer (HOXB13, BRCA2 in men)",
        },
        "specialty": {
            "pt": "urologista oncológico; oncogeneticista se BRCA2",
            "en": "urologic oncologist; cancer geneticist if BRCA2",
        },
        "notes": {
            "pt": "PSA anual a partir dos 40 quando confirmado. BRCA2 em homens também aumenta risco de CA mama masculino e pancreático.",
            "en": "Annual PSA from age 40 when confirmed. BRCA2 in men also raises male breast and pancreatic cancer risk.",
        },
    },
    # ── Cardiometabolic ─────────────────────────────────────────────────
    {
        "key": "familial_hypercholesterolemia",
        "genes": ["LDLR", "APOB", "PCSK9"],
        "trigger": {
            "pt": "Hipercolesterolemia familiar (LDLR/APOB/PCSK9)",
            "en": "Familial hypercholesterolemia (LDLR/APOB/PCSK9)",
        },
        "specialty": {
            "pt": "cardiologista ou lipidologista (referência: SBC, SOCESP)",
            "en": "cardiologist or lipidologist",
        },
        "notes": {
            "pt": "Estatina de alta potência precoce, evolução pra inibidor de PCSK9 se necessário. SUS dispensa estatinas pelo programa Farmácia Popular; iPCSK9 só em centros de referência.",
            "en": "Early high-intensity statin, escalating to PCSK9 inhibitors if needed. PCSK9 inhibitors are typically restricted to specialty lipid clinics.",
        },
    },
    {
        "key": "thrombophilia",
        "genes": ["F5", "F2", "MTHFR", "PROC", "PROS1", "SERPINC1"],
        "trigger": {
            "pt": "Trombofilia hereditária (Factor V Leiden, Prothrombin G20210A, MTHFR)",
            "en": "Hereditary thrombophilia (Factor V Leiden, Prothrombin G20210A, MTHFR)",
        },
        "specialty": {
            "pt": "hematologista; ginecologista-obstetra com interesse em trombose se gestação/contracepção",
            "en": "hematologist; OB-GYN with thrombosis interest if pregnancy/contraception is on the table",
        },
        "notes": {
            "pt": "Contracepção hormonal combinada é contraindicação relativa em portadores. SUS atende em ambulatório de hematologia em hospitais públicos; convênio: cobertura padrão.",
            "en": "Combined hormonal contraception is a relative contraindication for carriers. Hematology referrals are standard under most health systems.",
        },
    },
    # ── Hepatic / pulmonary ─────────────────────────────────────────────
    {
        "key": "hemochromatosis",
        "genes": ["HFE", "TFR2", "HJV", "HAMP"],
        "trigger": {
            "pt": "Hemocromatose hereditária (HFE C282Y/H63D)",
            "en": "Hereditary hemochromatosis (HFE C282Y/H63D)",
        },
        "specialty": {
            "pt": "hepatologista ou hematologista (programa de flebotomia terapêutica)",
            "en": "hepatologist or hematologist (therapeutic phlebotomy program)",
        },
        "notes": {
            "pt": "Ferritina e saturação de transferrina anuais. SUS oferece flebotomia terapêutica em hemocentros (Hemorio, Fundação Hemominas, Hemope).",
            "en": "Annual ferritin and transferrin saturation. Therapeutic phlebotomy is available at blood centers in most systems.",
        },
    },
    {
        "key": "alpha1_antitrypsin",
        "genes": ["SERPINA1"],
        "trigger": {
            "pt": "Deficiência de alfa-1 antitripsina (SERPINA1)",
            "en": "Alpha-1 antitrypsin deficiency (SERPINA1)",
        },
        "specialty": {
            "pt": "pneumologista (DPOC precoce) + hepatologista (cirrose) — evitar tabaco é mandatório",
            "en": "pulmonologist (early COPD) + hepatologist (cirrhosis) — smoking cessation is mandatory",
        },
        "notes": {
            "pt": "Terapia de reposição é cara e nem sempre coberta. SUS: centros de referência limitados; convênio: avaliação caso a caso.",
            "en": "Augmentation therapy is expensive and not always covered. Availability varies by health system.",
        },
    },
    # ── Pharmacogenomics ────────────────────────────────────────────────
    {
        "key": "pgx_psychiatry",
        "genes": ["CYP2D6", "CYP2C19", "CYP2B6"],
        "trigger": {
            "pt": "Resposta a antidepressivos/antipsicóticos/opioides (CYP2D6, CYP2C19)",
            "en": "Response to antidepressants/antipsychotics/opioids (CYP2D6, CYP2C19)",
        },
        "specialty": {
            "pt": "psiquiatra com formação em farmacogenética; farmacêutico clínico com PGx",
            "en": "psychiatrist with pharmacogenetics training; clinical pharmacist with PGx expertise",
        },
        "notes": {
            "pt": "Brasil ainda tem poucos centros — universitários (USP, UFRGS, UFMG) e alguns hospitais privados. CPIC publica diretrizes de dose por genótipo.",
            "en": "PGx clinics are still uncommon — academic medical centers and select private hospitals lead. CPIC publishes dosing guidelines by genotype.",
        },
    },
    {
        "key": "pgx_anticoagulation",
        "genes": ["VKORC1", "CYP2C9", "CYP4F2"],
        "trigger": {
            "pt": "Sensibilidade a varfarina (VKORC1/CYP2C9)",
            "en": "Warfarin sensitivity (VKORC1/CYP2C9)",
        },
        "specialty": {
            "pt": "cardiologista ou hematologista responsável pela anticoagulação; INR mais frequente no início",
            "en": "cardiologist or hematologist managing anticoagulation; more frequent INR monitoring initially",
        },
        "notes": {
            "pt": "Dose inicial reduzida em metabolizadores lentos. Alternativas DOAC (rivaroxabana, apixabana) não dependem desses genes.",
            "en": "Lower starting dose for slow metabolizers. DOAC alternatives (rivaroxaban, apixaban) don't depend on these genes.",
        },
    },
    {
        "key": "pgx_immunosuppressants",
        "genes": ["TPMT", "NUDT15"],
        "trigger": {
            "pt": "Toxicidade a tiopurinas (azatioprina, 6-mercaptopurina) — TPMT/NUDT15",
            "en": "Thiopurine toxicity (azathioprine, 6-mercaptopurine) — TPMT/NUDT15",
        },
        "specialty": {
            "pt": "reumatologista, gastroenterologista ou hematologista que prescreva a droga",
            "en": "rheumatologist, gastroenterologist, or hematologist prescribing the drug",
        },
        "notes": {
            "pt": "Genotipagem antes de iniciar azatioprina já é recomendação na maioria dos serviços. Metabolizadores lentos podem ter mielotoxicidade fatal em dose padrão.",
            "en": "Pre-prescription genotyping is increasingly standard. Slow metabolizers can experience fatal myelotoxicity at standard doses.",
        },
    },
    # ── Wellness panels ─────────────────────────────────────────────────
    {
        "key": "wellness_thyroid",
        "genes": ["TPO", "TSHR", "PDE8B"],
        "trigger": {
            "pt": "Predisposição tireoidiana (painel Thyroid)",
            "en": "Thyroid predisposition (Thyroid panel)",
        },
        "specialty": {
            "pt": "endocrinologista; TSH/T4 livre anual se sintomas",
            "en": "endocrinologist; annual TSH/free T4 if symptomatic",
        },
        "notes": {
            "pt": "Achados isolados sem sintoma não exigem tratamento — só rastreio. Anti-TPO sugere autoimunidade tireoidiana.",
            "en": "Isolated findings without symptoms don't need treatment — only surveillance. Anti-TPO antibodies suggest autoimmune thyroiditis.",
        },
    },
    {
        "key": "wellness_mental",
        "genes": ["COMT", "MAOA", "BDNF", "SLC6A4", "DRD2"],
        "trigger": {
            "pt": "Painel Mental (COMT, MAOA, BDNF) — perfil neuroquímico",
            "en": "Mental panel (COMT, MAOA, BDNF) — neurochemical profile",
        },
        "specialty": {
            "pt": "psiquiatra ou psicólogo se sintomas; informativo isoladamente",
            "en": "psychiatrist or psychologist if symptomatic; informational on its own",
        },
        "notes": {
            "pt": "Variantes neuroquímicas NÃO diagnosticam transtorno. Útil pra discutir resposta a medicamento com psiquiatra (ver bucket farmacogenética).",
            "en": "Neurochemical variants do NOT diagnose disorders. Useful when discussing medication response with a psychiatrist (see pharmacogenetics).",
        },
    },
    {
        "key": "wellness_sleep",
        "genes": ["CLOCK", "PER3", "ADA", "HLA-DQB1"],
        "trigger": {
            "pt": "Painel Sleep (cronotipo, narcolepsia em HLA-DQB1*06:02)",
            "en": "Sleep panel (chronotype, narcolepsy with HLA-DQB1*06:02)",
        },
        "specialty": {
            "pt": "médico do sono (otorrinolaringologista ou neurologista com formação em sono); polissonografia se suspeita clínica",
            "en": "sleep medicine physician (ENT or neurologist with sleep training); polysomnography if clinically suspected",
        },
        "notes": {
            "pt": "Brasil: certificação ABMS-AMB Medicina do Sono. SUS: poucos centros, longa fila; convênio: cobertura padrão pra polissonografia.",
            "en": "Polysomnography is widely covered. Specialty sleep centers offer more comprehensive workups.",
        },
    },
    {
        "key": "wellness_eyes",
        "genes": ["CFH", "ARMS2", "HTRA1"],
        "trigger": {
            "pt": "Painel Eyes — predisposição a DMRI (degeneração macular)",
            "en": "Eyes panel — AMD (age-related macular degeneration) risk",
        },
        "specialty": {
            "pt": "oftalmologista com subespecialidade em retina",
            "en": "ophthalmologist subspecialized in retina",
        },
        "notes": {
            "pt": "Fundoscopia/OCT anual a partir dos 50. Antioxidantes AREDS2 só se houver achado clínico — não preventivo cego.",
            "en": "Annual fundoscopy/OCT from age 50. AREDS2 antioxidants only when there's clinical disease — not blind prevention.",
        },
    },
    {
        "key": "wellness_bones",
        "genes": ["VDR", "COL1A1", "LRP5"],
        "trigger": {
            "pt": "Painel Bones — predisposição a baixa densidade óssea",
            "en": "Bones panel — low bone density predisposition",
        },
        "specialty": {
            "pt": "endocrinologista (metabolismo ósseo) ou reumatologista; densitometria conforme idade/sexo",
            "en": "endocrinologist (bone metabolism) or rheumatologist; DEXA scan per age/sex guidelines",
        },
        "notes": {
            "pt": "Vitamina D e cálcio são manejo padrão; bisfosfonatos só com osteoporose confirmada.",
            "en": "Vitamin D and calcium are standard management; bisphosphonates only with confirmed osteoporosis.",
        },
    },
    {
        "key": "wellness_allergy",
        "genes": ["FCER1A", "IL13", "IL4R", "STAT6"],
        "trigger": {
            "pt": "Painel Allergy — predisposição atópica (rinite, asma, dermatite)",
            "en": "Allergy panel — atopic predisposition (rhinitis, asthma, dermatitis)",
        },
        "specialty": {
            "pt": "alergologista/imunologista; pneumologista pediátrico se asma na infância",
            "en": "allergist/immunologist; pediatric pulmonologist for childhood asthma",
        },
        "notes": {
            "pt": "Teste alérgico (prick test) e IgE específica complementam o achado. Genótipo não substitui teste clínico.",
            "en": "Skin prick test and specific IgE complement the genetic finding. Genotype does not replace clinical testing.",
        },
    },
    {
        "key": "wellness_autoimmune",
        "genes": ["HLA-B27", "HLA-DRB1", "HLA-DQ2", "HLA-DQ8", "PTPN22"],
        "trigger": {
            "pt": "Painel Autoimmune — HLA-B27 (espondiloartrite), HLA-DQ2/DQ8 (celíaca), HLA-DRB1 (AR)",
            "en": "Autoimmune panel — HLA-B27 (spondyloarthritis), HLA-DQ2/DQ8 (celiac), HLA-DRB1 (RA)",
        },
        "specialty": {
            "pt": "reumatologista (HLA-B27, DRB1); gastroenterologista + nutricionista (DQ2/DQ8 + sintomas)",
            "en": "rheumatologist (HLA-B27, DRB1); gastroenterologist + dietitian (DQ2/DQ8 + symptoms)",
        },
        "notes": {
            "pt": "HLA isolado NÃO diagnostica — só predispõe. Celíaca exige biópsia duodenal pra confirmar; AR exige clínica + sorologia.",
            "en": "HLA alone does NOT diagnose — it only predisposes. Celiac requires duodenal biopsy to confirm; RA requires clinical + serology workup.",
        },
    },
    {
        "key": "wellness_skin",
        "genes": ["MC1R", "TYR", "OCA2", "IL23R"],
        "trigger": {
            "pt": "Painel Skin — fototipo, melanoma (MC1R), psoríase",
            "en": "Skin panel — phototype, melanoma (MC1R), psoriasis",
        },
        "specialty": {
            "pt": "dermatologista; oncológico se MC1R + histórico familiar de melanoma",
            "en": "dermatologist; dermatologic oncologist if MC1R + family history of melanoma",
        },
        "notes": {
            "pt": "Mapeamento corporal anual em fototipo I/II com MC1R variante. Convênio cobre quando há justificativa clínica.",
            "en": "Annual full-body mapping for phototype I/II with MC1R variants. Typically covered when clinically justified.",
        },
    },
    {
        "key": "wellness_food",
        "genes": ["LCT", "FUT2", "ADH1B", "ALDH2"],
        "trigger": {
            "pt": "Painel Food — intolerância à lactose (LCT), álcool (ADH1B/ALDH2)",
            "en": "Food panel — lactose intolerance (LCT), alcohol (ADH1B/ALDH2)",
        },
        "specialty": {
            "pt": "gastroenterologista (sintomas digestivos); nutricionista pra plano alimentar",
            "en": "gastroenterologist (digestive symptoms); registered dietitian for meal planning",
        },
        "notes": {
            "pt": "Teste respiratório de hidrogênio confirma intolerância à lactose. ALDH2 deficiente (comum em asiáticos) aumenta risco de CA esofágico com álcool.",
            "en": "Hydrogen breath test confirms lactose intolerance. ALDH2 deficiency (common in East Asians) raises esophageal cancer risk with alcohol.",
        },
    },
    {
        "key": "wellness_nutri",
        "genes": ["MTHFR", "FTO", "TCF7L2", "APOA2"],
        "trigger": {
            "pt": "Painel Nutri / Aging / Longevity — metabolismo, peso, longevidade",
            "en": "Nutri / Aging / Longevity panels — metabolism, weight, longevity",
        },
        "specialty": {
            "pt": "endocrinologista (DM2 poligênico, obesidade) ou nutricionista com formação em nutrigenética",
            "en": "endocrinologist (polygenic T2D, obesity) or dietitian with nutrigenomics training",
        },
        "notes": {
            "pt": "Achados poligênicos isolados têm baixo valor preditivo individual. Foco em fatores modificáveis (alimentação, exercício, sono) é mais útil que tratamento direcionado a SNP.",
            "en": "Polygenic findings have low individual predictive value. Modifiable factors (diet, exercise, sleep) matter more than SNP-targeted treatment.",
        },
    },
    {
        "key": "wellness_sensory",
        "genes": ["TAS2R38", "OR6A2", "TAS1R3"],
        "trigger": {
            "pt": "Painel Sensory — percepção de sabor amargo, coentro, doce",
            "en": "Sensory panel — bitter taste, cilantro/coriander, sweet perception",
        },
        "specialty": {
            "pt": "otorrinolaringologista se anosmia/disgeusia clínica; nutricionista pra adaptação alimentar",
            "en": "ENT if clinical anosmia/dysgeusia; dietitian for food adaptation",
        },
        "notes": {
            "pt": "Achado isolado é curiosidade — só vira clínico se houver perda súbita de olfato/paladar (investigar causas neurológicas, sinusais, pós-COVID).",
            "en": "Isolated finding is mostly trivia — becomes clinical only with sudden olfactory/taste loss (investigate neurologic, sinus, post-COVID causes).",
        },
    },
    {
        "key": "wellness_fit",
        "genes": ["ACTN3", "ACE", "PPARGC1A"],
        "trigger": {
            "pt": "Painel Fit — perfil power/endurance, recuperação",
            "en": "Fit panel — power/endurance profile, recovery",
        },
        "specialty": {
            "pt": "médico do esporte; educador físico com formação genômica",
            "en": "sports medicine physician; exercise physiologist with genomics background",
        },
        "notes": {
            "pt": "Genótipo NÃO determina performance — treino e ambiente pesam mais. Útil pra periodização inteligente, não pra decidir esporte.",
            "en": "Genotype does NOT determine performance — training and environment matter more. Useful for smart periodization, not sport selection.",
        },
    },
    {
        "key": "wellness_cardio",
        "genes": ["9p21", "CDKN2B-AS1", "ANRIL"],
        "trigger": {
            "pt": "Painel Cardio — 9p21 (rs10757278) e risco residual independente de lipídios",
            "en": "Cardio panel — 9p21 (rs10757278) and lipid-independent residual risk",
        },
        "specialty": {
            "pt": "cardiologista; escore de cálcio coronariano (CAC) após 40 anos se variante de risco presente",
            "en": "cardiologist; coronary artery calcium (CAC) scoring after age 40 if the risk variant is present",
        },
        "notes": {
            "pt": "9p21 captura risco NÃO explicado por LDL/pressão/glicemia — ou seja, mesmo com perfil lipídico bom, vale acompanhar. Combinado com tabagismo/HAS/dislipidemia, risco se multiplica.",
            "en": "9p21 captures risk NOT explained by LDL/BP/glucose — meaning even with a clean lipid panel, monitoring is worthwhile. Combined with smoking/HTN/dyslipidemia, risk multiplies.",
        },
    },
    {
        "key": "wellness_carrier_screening",
        "genes": ["HBB", "CFTR", "BLM"],
        "trigger": {
            "pt": "Painel Carrier Screening — anemia falciforme (HBB), fibrose cística (CFTR F508del), síndrome de Bloom (BLMAsh) — portador (assintomático) vs afetado (homozigoto)",
            "en": "Carrier Screening panel — sickle cell (HBB), cystic fibrosis (CFTR F508del), Bloom syndrome (BLMAsh) — carrier (asymptomatic) vs affected (homozygous)",
        },
        "specialty": {
            "pt": "geneticista clínico + aconselhador genético se planejamento reprodutivo; hematologista se HbAS/HbSS; pneumologista CF-especialista se CFTR; oncologista + geneticista se BLM homozigoto",
            "en": "clinical geneticist + genetic counselor if planning pregnancy; hematologist if HbAS/HbSS; CF-specialized pulmonologist if CFTR; oncologist + geneticist if BLM homozygous",
        },
        "notes": {
            "pt": "Portador heterozigoto é assintomático mas tem 25% de chance de filho afetado se parceiro também for portador da MESMA doença. Para CFTR, parceiro pode ter outra mutação (não só F508del) e ainda contar como compatível. Aconselhamento genético antes de gestação é o padrão de cuidado.",
            "en": "Heterozygous carriers are asymptomatic but have a 25% chance of an affected child if the partner carries the SAME disease. For CFTR, the partner can carry a different mutation (not just F508del) and still count as compatible. Genetic counseling before pregnancy is standard of care.",
        },
    },
    {
        "key": "wellness_body_chemistry",
        "genes": ["ABCC11"],
        "trigger": {
            "pt": "Painel Body Chemistry — composição de suor apócrino, tipo de cera de ouvido, odor corporal axilar (não prediz volume de transpiração)",
            "en": "Body Chemistry panel — apocrine sweat composition, earwax type, axillary body odor (does not predict sweating volume)",
        },
        "specialty": {
            "pt": "dermatologista para queixas de odor axilar persistente; cirurgião com experiência em hiperidrose se queixa for VOLUME de suor (ABCC11 não cobre isso)",
            "en": "dermatologist for persistent axillary odor concerns; surgeon experienced with hyperhidrosis if the complaint is sweating VOLUME (ABCC11 does not cover this)",
        },
        "notes": {
            "pt": "ABCC11 mede COMPOSIÇÃO química do suor apócrino, não volume. Hiperidrose primária focal é poligênica/multifatorial e NÃO tem marcador SNP comum confiável em chip de consumidor — não tente correlacionar.",
            "en": "ABCC11 measures sweat composition, not volume. Primary focal hyperhidrosis is polygenic/multifactorial and has NO validated common SNP marker on consumer chips — do not try to correlate.",
        },
    },
]


def find_relevant_for_analysis(active: dict, max_results: int = 10) -> list[dict]:
    """Return referral entries whose genes or wellness-panel key match the
    user's active analysis. Ordered by overlap strength so the most
    on-point referrals come first.

    `max_results` defaults to 10 — generous because the model is local,
    but not unbounded. The real cost isn't dollars (loopback to Ollama),
    it's attention-budget on an 8B model: past ~3-4k prompt tokens the
    model starts dropping instruction-following. 10 well-scored referrals
    add ~1-1.5k tokens and stay safely under that ceiling. Bump higher if
    you need; expect quality drop somewhere around 25+.

    Returns the full referral dicts (including `notes`), so the caller
    can choose how much to inline. Returns [] when there's no active
    analysis or no overlap.
    """
    if not active:
        return []

    seen_genes: set[str] = set()
    seen_panels: set[str] = set()

    for src_key in ("health", "disease"):
        section = active.get(src_key) or {}
        for f in section.get("findings", []) or []:
            g = f.get("gene")
            if g:
                seen_genes.add(g)

    # Hereditary results carry per-gene detail and condition-level gene lists.
    hereditary = active.get("hereditary") or {}
    for cond in hereditary.get("matches", []) or []:
        for d in cond.get("gene_details", []) or []:
            if d.get("gene"):
                seen_genes.add(d["gene"])
        for g in cond.get("genes", []) or []:
            seen_genes.add(g)

    # Wellness panels are indexed by short key (skin, sleep, …). Referral
    # keys follow the convention "wellness_<panel>".
    for panel_key, panel in (active.get("wellness") or {}).items():
        if (panel or {}).get("findings"):
            seen_panels.add(panel_key.lower())

    scored: list[tuple[int, dict]] = []
    for r in SPECIALTY_REFERRALS:
        gene_overlap = len(set(r["genes"]) & seen_genes)
        panel_match = 0
        for p in seen_panels:
            if r["key"].lower() == f"wellness_{p}":
                panel_match = 2  # exact panel match beats incidental gene overlap
                break
        score = gene_overlap + panel_match
        if score > 0:
            scored.append((score, r))

    scored.sort(key=lambda x: -x[0])
    return [r for _, r in scored[:max_results]]


def format_for_prompt(lang: Lang) -> str:
    """Render SPECIALTY_REFERRALS as a markdown bullet block for inlining in
    the system prompt. Only the `trigger → specialty` line — notes are
    kept out of the prompt to save tokens, and are available via
    `lookup(key)` for richer context injection later."""
    lines = []
    for r in SPECIALTY_REFERRALS:
        lines.append(f"- {r['trigger'][lang]} → {r['specialty'][lang]}")
    return "\n".join(lines)


def lookup(key: str) -> dict | None:
    """Return the full entry (with notes) for a given key, or None."""
    for r in SPECIALTY_REFERRALS:
        if r["key"] == key:
            return r
    return None
