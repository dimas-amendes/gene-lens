"""
Traducao de condicoes clinicas e contexto por gene.
Mapeia termos ClinVar em ingles para portugues e adiciona
contexto clinico para conclusoes mais informativas.
"""
from src.i18n import Lang

# Traducao de condicoes comuns do ClinVar
CONDITIONS_PT = {
    # Cancer
    "Hereditary cancer-predisposing syndrome": "Sindrome hereditaria de predisposicao ao cancer",
    "Breast Cancer": "Cancer de Mama",
    "Breast cancer": "Cancer de Mama",
    "Multiple fibroadenomas of the breast": "Multiplos fibroadenomas mamarios",
    "Colorectal cancer": "Cancer Colorretal",
    "Prostate cancer": "Cancer de Prostata",
    "Ovarian cancer": "Cancer de Ovario",
    "Pancreatic cancer": "Cancer de Pancreas",
    "Lynch syndrome": "Sindrome de Lynch",
    "Li-Fraumeni syndrome": "Sindrome de Li-Fraumeni",
    "Estrogen resistance": "Resistencia a estrogeno",
    "Poor prognosis": "Prognostico desfavoravel",

    # Cardiovascular
    "Long QT syndrome": "Sindrome do QT Longo",
    "Congenital long QT syndrome": "Sindrome do QT Longo Congenita",
    "Congenital heart disease": "Doenca Cardiaca Congenita",
    "Primary dilated cardiomyopathy": "Cardiomiopatia Dilatada Primaria",
    "Coronary artery disease, modifier of": "Doenca arterial coronaria (modificador)",
    "Hypertrophic cardiomyopathy": "Cardiomiopatia Hipertrofica",
    "Atrial fibrillation": "Fibrilacao Atrial",

    # Neurological
    "Alzheimer disease 2": "Doenca de Alzheimer tipo 2",
    "Angelman syndrome": "Sindrome de Angelman",
    "Parkinson disease": "Doenca de Parkinson",
    "Epilepsy": "Epilepsia",

    # Autoimmune / Inflammatory
    "Inflammatory bowel disease": "Doenca Inflamatoria Intestinal",
    "Blau syndrome": "Sindrome de Blau",
    "Crohn disease": "Doenca de Crohn",
    "Celiac disease": "Doenca Celiaca",
    "Rheumatoid arthritis": "Artrite Reumatoide",
    "Multiple sclerosis": "Esclerose Multipla",
    "Type 1 diabetes": "Diabetes Tipo 1",
    "Lupus": "Lupus",

    # Blood / Immune
    "Plasmodium vivax, resistance to": "Resistencia ao Plasmodium vivax (malaria)",
    "White blood cell count quantitative trait locus 1": "Locus de contagem de leucocitos",
    "Hemochromatosis type 1": "Hemocromatose tipo 1",
    "Factor V Leiden thrombophilia": "Trombofilia por Fator V Leiden",
    "Sickle cell disease": "Doenca Falciforme",

    # Metabolic
    "Phenylketonuria": "Fenilcetonuria",
    "Gaucher disease": "Doenca de Gaucher",
    "Cystic fibrosis": "Fibrose Cistica",
    "Galactosemia": "Galactosemia",

    # Other
    "Spina bifida, susceptibility to": "Espinha bifida (suscetibilidade)",
    "COACH syndrome": "Sindrome COACH",
    "Joubert syndrome 9": "Sindrome de Joubert tipo 9",
    "not provided": "nao especificada",
    "Not provided": "nao especificada",
    "not specified": "nao especificada",
    "Not specified": "nao especificada",

    # Macular / Eye
    "Age-related macular degeneration": "Degeneracao macular relacionada a idade",

    # Obesity / Diabetes
    "Type 2 diabetes": "Diabetes Tipo 2",
    "Obesity": "Obesidade",
}


# Clinical context per gene, used to enrich disease-section conclusions.
# Bilingual: bare keys are EN (source of truth); `*_pt` keys are translations.
# Access via get_gene_context(gene, lang) to receive lang-resolved fields.
GENE_CONTEXT = {
    "MSH6": {
        "syndrome": "Lynch syndrome",
        "syndrome_pt": "Sindrome de Lynch",
        "cancers": ["colorectal", "endometrial", "ovarian", "stomach", "urinary tract"],
        "cancers_pt": ["colorretal", "endometrio", "ovario", "estomago", "trato urinario"],
        "note": "MSH6 is a DNA mismatch-repair gene. Pathogenic variants are linked to Lynch syndrome, which raises lifetime colorectal cancer risk (up to ~80%), as well as endometrial, ovarian and other cancers. Regular colonoscopic surveillance is recommended from age 25-30 in confirmed carriers.",
        "note_pt": "MSH6 e um gene de reparo de DNA (mismatch repair). Variantes patogenicas estao associadas a Sindrome de Lynch, que aumenta o risco de cancer colorretal (ate 80% ao longo da vida), endometrio, ovario e outros. Rastreamento colonoscopico regular e recomendado a partir dos 25-30 anos para portadores confirmados.",
        "action": "Confirm via a clinical hereditary-cancer panel. If confirmed, colonoscopy every 1-2 years starting at age 25. Discuss with a cancer geneticist.",
        "action_pt": "Confirmar com teste clinico de painel de cancer hereditario. Se confirmado, colonoscopia a cada 1-2 anos a partir dos 25 anos. Discutir com oncogeneticista.",
    },
    "BRCA1": {
        "syndrome": "BRCA1",
        "syndrome_pt": "BRCA1",
        "cancers": ["breast", "ovarian", "prostate", "pancreatic"],
        "cancers_pt": ["mama", "ovario", "prostata", "pancreas"],
        "note": "BRCA1 is a tumor-suppressor gene essential for DNA repair. Pathogenic variants substantially raise the risk of breast (up to ~70%) and ovarian (up to ~40%) cancer. In men, prostate and breast cancer risk is also elevated.",
        "note_pt": "BRCA1 e um gene supressor tumoral essencial para reparo de DNA. Variantes patogenicas aumentam significativamente o risco de cancer de mama (ate 70%) e ovario (ate 40%). Em homens, aumento do risco de prostata e mama.",
        "action": "Confirm with clinical BRCA1/2 sequencing. If confirmed, pursue intensive surveillance (annual breast MRI, CA-125) and discuss preventive options with an oncologist.",
        "action_pt": "Confirmar com sequenciamento clinico de BRCA1/2. Se confirmado, rastreamento intensivo (RMN mamaria anual, CA-125) e avaliar opcoes preventivas com oncologista.",
    },
    "BRCA2": {
        "syndrome": "BRCA2",
        "syndrome_pt": "BRCA2",
        "cancers": ["breast", "ovarian", "prostate", "pancreatic", "melanoma"],
        "cancers_pt": ["mama", "ovario", "prostata", "pancreas", "melanoma"],
        "note": "BRCA2 functions similarly to BRCA1 in DNA repair. Increased risk of breast, ovarian, prostate, pancreatic and melanoma cancers.",
        "note_pt": "BRCA2 funciona de forma similar ao BRCA1 no reparo de DNA. Risco aumentado de cancer de mama, ovario, prostata, pancreas e melanoma.",
        "action": "Confirm with clinical sequencing. Intensive surveillance if confirmed.",
        "action_pt": "Confirmar com sequenciamento clinico. Rastreamento intensivo se confirmado.",
    },
    "MLH1": {
        "syndrome": "Lynch syndrome",
        "syndrome_pt": "Sindrome de Lynch",
        "cancers": ["colorectal", "endometrial", "ovarian", "stomach"],
        "cancers_pt": ["colorretal", "endometrio", "ovario", "estomago"],
        "note": "MLH1 is part of the DNA mismatch-repair system. Pathogenic variants cause Lynch syndrome with high risk of colorectal cancer.",
        "note_pt": "MLH1 faz parte do sistema de reparo de mismatch do DNA. Variantes patogenicas causam Sindrome de Lynch com alto risco de cancer colorretal.",
        "action": "Regular colonoscopy. Consult a cancer geneticist.",
        "action_pt": "Colonoscopia regular. Consultar oncogeneticista.",
    },
    "MSH2": {
        "syndrome": "Lynch syndrome",
        "syndrome_pt": "Sindrome de Lynch",
        "cancers": ["colorectal", "endometrial", "ovarian", "urinary tract"],
        "cancers_pt": ["colorretal", "endometrio", "ovario", "trato urinario"],
        "note": "MSH2 is another mismatch-repair gene. Together with MLH1 and MSH6, it forms the main trio in Lynch syndrome.",
        "note_pt": "MSH2 e outro gene de reparo de mismatch. Junto com MLH1 e MSH6, forma o trio principal da Sindrome de Lynch.",
        "action": "Regular colonoscopy from age 25 if confirmed.",
        "action_pt": "Colonoscopia regular a partir dos 25 anos se confirmado.",
    },
    "APOE": {
        "syndrome": "APOE e4",
        "syndrome_pt": "APOE e4",
        "cancers": [],
        "cancers_pt": [],
        "note": "APOE e4 is the main genetic risk factor for late-onset Alzheimer's disease. One copy (heterozygous) raises risk ~3x; two copies ~12x. It is NOT deterministic — many carriers never develop Alzheimer's. Regular exercise, a Mediterranean diet, quality sleep, cognitive engagement and cardiovascular control are the best evidence-based preventive strategies.",
        "note_pt": "APOE e4 e o principal fator de risco genetico para Doenca de Alzheimer de inicio tardio. Uma copia (heterozigoto) aumenta o risco ~3x; duas copias ~12x. NAO e determinista — muitos portadores nunca desenvolvem Alzheimer. Exercicio regular, dieta mediterranea, sono, engajamento cognitivo e controle cardiovascular sao as melhores estrategias preventivas baseadas em evidencia.",
        "action": "Focus on cardiovascular prevention and lifestyle. No additional clinical test is needed for APOE — genotype alone is sufficient. Discuss with a neurologist if there is concern.",
        "action_pt": "Foco em prevencao cardiovascular e estilo de vida. Nao ha teste clinico adicional necessario para APOE — o genotipo ja e suficiente. Discutir com neurologista se houver preocupacao.",
    },
    "KCNQ1": {
        "syndrome": "Long QT Syndrome",
        "syndrome_pt": "Sindrome do QT Longo",
        "cancers": [],
        "cancers_pt": [],
        "note": "KCNQ1 encodes a cardiac potassium channel. Variants can cause Long QT Syndrome type 1, which predisposes to arrhythmia and sudden death. Heterozygous carriers may show mild QT-interval prolongation.",
        "note_pt": "KCNQ1 codifica um canal de potassio cardiaco. Variantes podem causar Sindrome do QT Longo tipo 1, que predispoe a arritmias e morte subita. Heterozigoto pode ter prolongamento leve do intervalo QT.",
        "action": "ECG with QT measurement. Avoid QT-prolonging medications (list at crediblemeds.org). Consult a cardiologist.",
        "action_pt": "ECG com medida de intervalo QT. Evitar medicamentos que prolongam QT (lista em crediblemeds.org). Consultar cardiologista.",
    },
    "NOD2": {
        "syndrome": "Inflammatory Bowel Disease",
        "syndrome_pt": "Doenca Inflamatoria Intestinal",
        "cancers": [],
        "cancers_pt": [],
        "note": "NOD2 is an innate-immunity receptor. Variants raise Crohn's disease susceptibility 3-4x per allele. Heterozygous carriers have moderate risk.",
        "note_pt": "NOD2 e um receptor de imunidade inata. Variantes aumentam suscetibilidade a Doenca de Crohn (3-4x por alelo). Heterozigoto tem risco moderado.",
        "action": "Watch for persistent gastrointestinal symptoms (chronic diarrhea, abdominal pain, blood in stool). Consult a gastroenterologist if symptomatic.",
        "action_pt": "Estar atento a sintomas gastrointestinais persistentes (diarreia cronica, dor abdominal, sangue nas fezes). Consultar gastroenterologista se sintomatico.",
    },
    "VCL": {
        "syndrome": "Cardiomyopathy",
        "syndrome_pt": "Cardiomiopatia",
        "cancers": [],
        "cancers_pt": [],
        "note": "VCL (vinculin) is a structural protein of cardiac muscle. Variants can cause dilated cardiomyopathy.",
        "note_pt": "VCL (vinculina) e uma proteina estrutural do musculo cardiaco. Variantes podem causar cardiomiopatia dilatada.",
        "action": "Baseline echocardiogram. Consult a cardiologist.",
        "action_pt": "Ecocardiograma basal. Consultar cardiologista.",
    },
    "GATA4": {
        "syndrome": "Congenital Heart Disease",
        "syndrome_pt": "Doenca Cardiaca Congenita",
        "cancers": [],
        "cancers_pt": [],
        "note": "GATA4 is a transcription factor essential for heart development. Variants can cause congenital heart defects.",
        "note_pt": "GATA4 e um fator de transcricao essencial para desenvolvimento cardiaco. Variantes podem causar defeitos cardiacos congenitos.",
        "action": "If asymptomatic in adulthood, likely not clinically relevant. Echocardiogram if concerned.",
        "action_pt": "Se assintomatico na vida adulta, provavelmente nao e clinicamente relevante. Ecocardiograma se houver preocupacao.",
    },
    "CCDC170": {
        "syndrome": "Breast Cancer",
        "syndrome_pt": "Cancer de Mama",
        "cancers": ["breast"],
        "cancers_pt": ["mama"],
        "note": "CCDC170 lies near the ESR1 (estrogen receptor) gene. Variants in this region are associated with breast-cancer risk and with hormonal-therapy response.",
        "note_pt": "CCDC170 fica proximo ao gene ESR1 (receptor de estrogeno). Variantes nesta regiao estao associadas a risco de cancer de mama e resposta a terapia hormonal.",
        "action": "Mammographic screening per guidelines. Discuss family history with your doctor.",
        "action_pt": "Rastreamento mamografico conforme diretrizes. Discutir historico familiar com medico.",
    },
    "PRLR": {
        "syndrome": "Breast Fibroadenomas",
        "syndrome_pt": "Fibroadenomas Mamarios",
        "cancers": [],
        "cancers_pt": [],
        "note": "PRLR (prolactin receptor) is associated with multiple breast fibroadenomas. Fibroadenomas are benign but require follow-up.",
        "note_pt": "PRLR (receptor de prolactina) esta associado a multiplos fibroadenomas mamarios. Fibroadenomas sao benignos mas requerem acompanhamento.",
        "action": "Regular clinical breast exam. Ultrasound if palpable.",
        "action_pt": "Exame clinico mamario regular. Ultrassom se palpavel.",
    },
    "UBE3A": {
        "syndrome": "Angelman Syndrome",
        "syndrome_pt": "Sindrome de Angelman",
        "cancers": [],
        "cancers_pt": [],
        "note": "UBE3A is associated with Angelman syndrome (developmental delay, epilepsy). In asymptomatic adults, a heterozygous variant is likely not clinically significant — Angelman requires loss of the maternal copy.",
        "note_pt": "UBE3A esta associado a Sindrome de Angelman (atraso de desenvolvimento, epilepsia). Em adultos assintomaticos, uma variante heterozigota provavelmente nao e clinicamente significativa — Angelman requer perda da copia materna.",
        "action": "Likely not relevant if asymptomatic adult. Genetic counseling if planning pregnancy.",
        "action_pt": "Provavelmente nao relevante se adulto assintomatico. Aconselhamento genetico se planejar gravidez.",
    },
    "ACKR1": {
        "syndrome": "Duffy Blood Group System",
        "syndrome_pt": "Sistema Sanguineo Duffy",
        "cancers": [],
        "cancers_pt": [],
        "note": "ACKR1 (Duffy) affects susceptibility to Plasmodium vivax malaria. The Duffy-negative phenotype confers resistance to vivax malaria. Also associated with lower white-blood-cell counts (benign ethnic neutropenia), common in populations of African ancestry.",
        "note_pt": "ACKR1 (Duffy) afeta suscetibilidade a malaria por Plasmodium vivax. O fenotipo Duffy-negativo confere resistencia a malaria vivax. Tambem associado a contagem de leucocitos mais baixa (neutropenia etnica benigna), comum em populacoes de ascendencia africana.",
        "action": "Inform physicians about possible benign ethnic neutropenia (to avoid unnecessary work-up).",
        "action_pt": "Informar medicos sobre possivel neutropenia etnica benigna (evitar investigacoes desnecessarias).",
    },
    "HFE": {
        "syndrome": "Hemochromatosis",
        "syndrome_pt": "Hemocromatose",
        "cancers": [],
        "cancers_pt": [],
        "note": "HFE is associated with hereditary hemochromatosis (iron overload). Heterozygous carriers are usually unaffected.",
        "note_pt": "HFE esta associado a hemocromatose hereditaria (acumulo de ferro). Portadores heterozigotos geralmente nao sao afetados.",
        "action": "Monitor ferritin periodically. Avoid unnecessary iron supplements.",
        "action_pt": "Monitorar ferritina periodicamente. Evitar suplementos de ferro desnecessarios.",
    },
}


def translate_condition(condition_en: str) -> str:
    """Translate a ClinVar condition string to PT-BR."""
    if not condition_en:
        return "nao especificada"

    # Try exact match first
    if condition_en in CONDITIONS_PT:
        return CONDITIONS_PT[condition_en]

    # Try case-insensitive partial match
    lower = condition_en.lower()
    for en, pt in CONDITIONS_PT.items():
        if en.lower() in lower:
            return pt

    # Return original if no translation
    return condition_en


def translate_traits(traits_str: str) -> str:
    """Translate a semicolon-separated ClinVar traits string."""
    if not traits_str:
        return "nao especificada"

    parts = traits_str.split(";")
    translated = []
    seen = set()
    for part in parts:
        part = part.strip()
        if not part:
            continue
        t = translate_condition(part)
        t_lower = t.lower()
        if t_lower not in seen:
            seen.add(t_lower)
            translated.append(t)

    return "; ".join(translated[:3]) if translated else traits_str


def get_gene_context(gene: str, lang: Lang = "en") -> dict:
    """Get clinical context for a gene, resolved to the requested language.

    GENE_CONTEXT stores EN as the bare keys (`syndrome`, `cancers`, `note`,
    `action`) and PT under `*_pt` suffixes. For lang='pt' this returns a copy
    where the bare keys hold the PT translation (falling back to EN if the
    PT variant is missing). For lang='en' it returns the entry as-is.
    """
    entry = GENE_CONTEXT.get(gene)
    if not entry:
        return {}
    if lang != "pt":
        return entry
    out = dict(entry)
    for k in ("syndrome", "cancers", "note", "action"):
        pt = entry.get(f"{k}_pt")
        if pt:
            out[k] = pt
    return out
