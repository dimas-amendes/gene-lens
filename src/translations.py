"""
Traducao de condicoes clinicas e contexto por gene.
Mapeia termos ClinVar em ingles para portugues e adiciona
contexto clinico para conclusoes mais informativas.
"""

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


# Contexto clinico por gene para conclusoes
GENE_CONTEXT = {
    "MSH6": {
        "syndrome": "Sindrome de Lynch",
        "cancers": ["colorretal", "endometrio", "ovario", "estomago", "trato urinario"],
        "note": "MSH6 e um gene de reparo de DNA (mismatch repair). Variantes patogenicas estao associadas a Sindrome de Lynch, que aumenta o risco de cancer colorretal (ate 80% ao longo da vida), endometrio, ovario e outros. Rastreamento colonoscopico regular e recomendado a partir dos 25-30 anos para portadores confirmados.",
        "action": "Confirmar com teste clinico de painel de cancer hereditario. Se confirmado, colonoscopia a cada 1-2 anos a partir dos 25 anos. Discutir com oncogeneticista.",
    },
    "BRCA1": {
        "syndrome": "BRCA1",
        "cancers": ["mama", "ovario", "prostata", "pancreas"],
        "note": "BRCA1 e um gene supressor tumoral essencial para reparo de DNA. Variantes patogenicas aumentam significativamente o risco de cancer de mama (ate 70%) e ovario (ate 40%). Em homens, aumento do risco de prostata e mama.",
        "action": "Confirmar com sequenciamento clinico de BRCA1/2. Se confirmado, rastreamento intensivo (RMN mamaria anual, CA-125) e avaliar opcoes preventivas com oncologista.",
    },
    "BRCA2": {
        "syndrome": "BRCA2",
        "cancers": ["mama", "ovario", "prostata", "pancreas", "melanoma"],
        "note": "BRCA2 funciona de forma similar ao BRCA1 no reparo de DNA. Risco aumentado de cancer de mama, ovario, prostata, pancreas e melanoma.",
        "action": "Confirmar com sequenciamento clinico. Rastreamento intensivo se confirmado.",
    },
    "MLH1": {
        "syndrome": "Sindrome de Lynch",
        "cancers": ["colorretal", "endometrio", "ovario", "estomago"],
        "note": "MLH1 faz parte do sistema de reparo de mismatch do DNA. Variantes patogenicas causam Sindrome de Lynch com alto risco de cancer colorretal.",
        "action": "Colonoscopia regular. Consultar oncogeneticista.",
    },
    "MSH2": {
        "syndrome": "Sindrome de Lynch",
        "cancers": ["colorretal", "endometrio", "ovario", "trato urinario"],
        "note": "MSH2 e outro gene de reparo de mismatch. Junto com MLH1 e MSH6, forma o trio principal da Sindrome de Lynch.",
        "action": "Colonoscopia regular a partir dos 25 anos se confirmado.",
    },
    "APOE": {
        "syndrome": "APOE e4",
        "cancers": [],
        "note": "APOE e4 e o principal fator de risco genetico para Doenca de Alzheimer de inicio tardio. Uma copia (heterozigoto) aumenta o risco ~3x; duas copias ~12x. NAO e determinista — muitos portadores nunca desenvolvem Alzheimer. Exercicio regular, dieta mediterranea, sono, engajamento cognitivo e controle cardiovascular sao as melhores estrategias preventivas baseadas em evidencia.",
        "action": "Foco em prevencao cardiovascular e estilo de vida. Nao ha teste clinico adicional necessario para APOE — o genotipo ja e suficiente. Discutir com neurologista se houver preocupacao.",
    },
    "KCNQ1": {
        "syndrome": "Sindrome do QT Longo",
        "cancers": [],
        "note": "KCNQ1 codifica um canal de potassio cardiaco. Variantes podem causar Sindrome do QT Longo tipo 1, que predispoe a arritmias e morte subita. Heterozigoto pode ter prolongamento leve do intervalo QT.",
        "action": "ECG com medida de intervalo QT. Evitar medicamentos que prolongam QT (lista em crediblemeds.org). Consultar cardiologista.",
    },
    "NOD2": {
        "syndrome": "Doenca Inflamatoria Intestinal",
        "cancers": [],
        "note": "NOD2 e um receptor de imunidade inata. Variantes aumentam suscetibilidade a Doenca de Crohn (3-4x por alelo). Heterozigoto tem risco moderado.",
        "action": "Estar atento a sintomas gastrointestinais persistentes (diarreia cronica, dor abdominal, sangue nas fezes). Consultar gastroenterologista se sintomatico.",
    },
    "VCL": {
        "syndrome": "Cardiomiopatia",
        "cancers": [],
        "note": "VCL (vinculina) e uma proteina estrutural do musculo cardiaco. Variantes podem causar cardiomiopatia dilatada.",
        "action": "Ecocardiograma basal. Consultar cardiologista.",
    },
    "GATA4": {
        "syndrome": "Doenca Cardiaca Congenita",
        "cancers": [],
        "note": "GATA4 e um fator de transcricao essencial para desenvolvimento cardiaco. Variantes podem causar defeitos cardiacos congenitos.",
        "action": "Se assintomatico na vida adulta, provavelmente nao e clinicamente relevante. Ecocardiograma se houver preocupacao.",
    },
    "CCDC170": {
        "syndrome": "Cancer de Mama",
        "cancers": ["mama"],
        "note": "CCDC170 fica proximo ao gene ESR1 (receptor de estrogeno). Variantes nesta regiao estao associadas a risco de cancer de mama e resposta a terapia hormonal.",
        "action": "Rastreamento mamografico conforme diretrizes. Discutir historico familiar com medico.",
    },
    "PRLR": {
        "syndrome": "Fibroadenomas Mamarios",
        "cancers": [],
        "note": "PRLR (receptor de prolactina) esta associado a multiplos fibroadenomas mamarios. Fibroadenomas sao benignos mas requerem acompanhamento.",
        "action": "Exame clinico mamario regular. Ultrassom se palpavel.",
    },
    "UBE3A": {
        "syndrome": "Sindrome de Angelman",
        "cancers": [],
        "note": "UBE3A esta associado a Sindrome de Angelman (atraso de desenvolvimento, epilepsia). Em adultos assintomaticos, uma variante heterozigota provavelmente nao e clinicamente significativa — Angelman requer perda da copia materna.",
        "action": "Provavelmente nao relevante se adulto assintomatico. Aconselhamento genetico se planejar gravidez.",
    },
    "ACKR1": {
        "syndrome": "Sistema Sanguineo Duffy",
        "cancers": [],
        "note": "ACKR1 (Duffy) afeta suscetibilidade a malaria por Plasmodium vivax. O fenotipo Duffy-negativo confere resistencia a malaria vivax. Tambem associado a contagem de leucocitos mais baixa (neutropenia etnica benigna), comum em populacoes de ascendencia africana.",
        "action": "Informar medicos sobre possivel neutropenia etnica benigna (evitar investigacoes desnecessarias).",
    },
    "HFE": {
        "syndrome": "Hemocromatose",
        "cancers": [],
        "note": "HFE esta associado a hemocromatose hereditaria (acumulo de ferro). Portadores heterozigotos geralmente nao sao afetados.",
        "action": "Monitorar ferritina periodicamente. Evitar suplementos de ferro desnecessarios.",
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


def get_gene_context(gene: str) -> dict:
    """Get clinical context for a gene."""
    return GENE_CONTEXT.get(gene, {})
