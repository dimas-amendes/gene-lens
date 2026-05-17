"""
Modulo de condicoes hereditarias com routing por sexo biologico.

Organizado por condicao clinica com contexto sex-aware:
- Texto do relatorio muda conforme sexo
- Prioridade de exibicao muda conforme sexo
- Evidencia baseada em ClinVar (gold stars)

Formato: condicao -> genes -> prioridade -> texto -> evidencia -> confirmacao

IMPORTANTE: Nenhuma destas conclusoes constitui diagnostico.
Variantes de chips de consumo tem ~40% de falso positivo.
"""

# ══════════════════════════════════════════════════════════════════════════════
# CONDITION MATRIX
# ══════════════════════════════════════════════════════════════════════════════

HEREDITARY_CONDITIONS = {

    # ── Cancer hereditario de mama/ovario (HBOC) ─────────────────────────────
    "hboc": {
        "name_pt": "Cancer Hereditario de Mama e Ovario (HBOC)",
        "name_en": "Hereditary Breast & Ovarian Cancer (HBOC)",
        "genes": ["BRCA1", "BRCA2", "PALB2", "ATM", "CHEK2", "BRIP1"],
        "priority_F": 1,   # alta prioridade para mulheres
        "priority_M": 3,   # relevante mas menor para homens
        "text_F": (
            "Variantes nestes genes estao associadas a risco significativamente aumentado de "
            "cancer de mama (ate 70% ao longo da vida para BRCA1) e cancer de ovario (ate 44% para BRCA1). "
            "A confirmacao clinica e OBRIGATORIA — chips de consumo nao sao teste diagnostico para BRCA. "
            "Se confirmado, protocolos de rastreamento intensificado (ressonancia mamaria anual, "
            "considerar mastectomia/ooforectomia profilatica) devem ser discutidos com oncogeneticista."
        ),
        "text_M": (
            "Embora associados principalmente a cancer feminino, BRCA1/2 tambem aumentam risco em homens: "
            "cancer de mama masculino (BRCA2: risco ~7%), cancer de prostata (BRCA2: risco ~20% ao longo da vida), "
            "e cancer de pancreas. Confirmacao clinica OBRIGATORIA. "
            "Se confirmado, rastreamento de prostata precoce (PSA a partir dos 40) e vigilancia pancreatica."
        ),
        "text_neutral": (
            "Genes do espectro HBOC detectados. Risco varia conforme sexo biologico e gene especifico. "
            "Confirmacao por sequenciamento clinico e OBRIGATORIA — chips de consumo tem alta taxa de erro para estes genes."
        ),
        "evidence": "ClinVar 2-3 estrelas. BRCA1/2 tem diretriz NCCN de manejo clinico.",
        "confirm": "Sequenciamento clinico de painel de cancer hereditario (Invitae, Myriad, laboratorio local). Consultar oncogeneticista.",
        "min_stars": 1,
    },

    # ── Cancer hereditario de prostata ────────────────────────────────────────
    "prostate": {
        "name_pt": "Cancer Hereditario de Prostata",
        "name_en": "Hereditary Prostate Cancer",
        "genes": ["HOXB13"],
        "priority_F": 5,   # informativo para mulheres (pode transmitir)
        "priority_M": 1,   # alta prioridade para homens
        "text_F": (
            "HOXB13 G84E e uma variante de predisposicao a cancer de prostata. "
            "Para voce, nao ha risco direto, mas voce pode transmitir para filhos homens. "
            "Filhos devem ser informados para rastreamento precoce de prostata."
        ),
        "text_M": (
            "HOXB13 G84E esta associado a risco ~3-5x de cancer de prostata, especialmente inicio precoce (<55 anos). "
            "Discuta com urologista: PSA anual a partir dos 40 anos (em vez dos 50 padrao). "
            "Confirmacao clinica recomendada."
        ),
        "text_neutral": (
            "Variante HOXB13 detectada. Associada a predisposicao a cancer de prostata hereditario."
        ),
        "evidence": "ClinVar 2 estrelas. HOXB13 G84E e a variante classica de cancer de prostata hereditario (NCI).",
        "confirm": "PSA e toque retal anual a partir dos 40 (homens). Painel genetico de cancer de prostata.",
        "min_stars": 1,
    },

    # ── Sindrome de Lynch ─────────────────────────────────────────────────────
    "lynch": {
        "name_pt": "Sindrome de Lynch (Cancer Colorretal/Endometrial Hereditario)",
        "name_en": "Lynch Syndrome (Hereditary Colorectal/Endometrial Cancer)",
        "genes": ["MLH1", "MSH2", "MSH6", "PMS2", "EPCAM"],
        "priority_F": 1,   # colorretal + endometrio + ovario
        "priority_M": 1,   # colorretal + prostata
        "text_F": (
            "Sindrome de Lynch aumenta risco de cancer colorretal (ate 80%), endometrio (ate 60%), "
            "ovario (ate 24%) e outros. Colonoscopia a cada 1-2 anos a partir dos 25 e diretriz padrao. "
            "Para mulheres: discutir tambem rastreamento endometrial e opcoes de reducao de risco ovariano. "
            "Confirmacao clinica OBRIGATORIA."
        ),
        "text_M": (
            "Sindrome de Lynch aumenta risco de cancer colorretal (ate 80%), prostata, "
            "estomago e trato urinario. Colonoscopia a cada 1-2 anos a partir dos 25 e diretriz padrao. "
            "Confirmacao clinica OBRIGATORIA."
        ),
        "text_neutral": (
            "Variante em gene de reparo de DNA (mismatch repair) detectada. "
            "Sindrome de Lynch aumenta risco de multiplos canceres. Confirmacao clinica essencial."
        ),
        "evidence": "ClinVar 3 estrelas. Diretriz NCCN de rastreamento disponivel.",
        "confirm": "Painel de cancer hereditario + imunohistoquimica MMR em tumores previos. Colonoscopia + consulta oncogeneticista.",
        "min_stars": 1,
    },

    # ── Poliposes hereditarias ────────────────────────────────────────────────
    "polyposis": {
        "name_pt": "Poliposes Hereditarias (FAP / MAP)",
        "name_en": "Hereditary Polyposis (FAP / MAP)",
        "genes": ["APC", "MUTYH"],
        "priority_F": 2,
        "priority_M": 2,
        "text_F": (
            "APC (polipose adenomatosa familiar) e MUTYH (MAP) aumentam fortemente o risco de cancer colorretal. "
            "FAP (APC): centenas a milhares de polipos, risco ~100% de cancer colorretal sem intervencao. "
            "MAP (MUTYH): heranca recessiva — ambos alelos precisam estar alterados. "
            "Colonoscopia de rastreamento essencial. Confirmacao clinica OBRIGATORIA."
        ),
        "text_M": None,  # same as F
        "text_neutral": (
            "Variante em gene de polipose hereditaria detectada. "
            "Risco significativamente aumentado de cancer colorretal. Confirmacao clinica OBRIGATORIA."
        ),
        "evidence": "ClinVar 2 estrelas. APC I1307K confirmado como patogenico.",
        "confirm": "Colonoscopia + sequenciamento de APC/MUTYH. Consulta com gastroenterologista e oncogeneticista.",
        "min_stars": 1,
    },

    # ── Hipercolesterolemia familiar ──────────────────────────────────────────
    "fh": {
        "name_pt": "Hipercolesterolemia Familiar (HF)",
        "name_en": "Familial Hypercholesterolemia (FH)",
        "genes": ["LDLR", "PCSK9"],
        "priority_F": 2,
        "priority_M": 2,
        "text_F": (
            "Hipercolesterolemia familiar causa niveis muito elevados de LDL-colesterol desde a infancia, "
            "levando a doenca cardiovascular precoce. Prevalencia ~1:250. "
            "Mulheres sao parcialmente protegidas pelo estrogeno ate a menopausa, mas o risco persiste. "
            "Perfil lipidico e OBRIGATORIO. Estatinas sao a base do tratamento se confirmado."
        ),
        "text_M": (
            "Hipercolesterolemia familiar causa LDL muito elevado desde a infancia, "
            "com risco de infarto precoce (homens: evento cardiovascular ~50% ate os 50 anos sem tratamento). "
            "Perfil lipidico OBRIGATORIO. Estatinas sao a base do tratamento se confirmado."
        ),
        "text_neutral": (
            "Variante em gene de metabolismo do colesterol detectada. "
            "Hipercolesterolemia familiar afeta ~1:250 pessoas. Perfil lipidico e essencial."
        ),
        "evidence": "ClinVar 2 estrelas para LDLR. PCSK9 com evidencia limitada mas crescente.",
        "confirm": "Perfil lipidico completo (LDL, HDL, TG, CT). Se LDL > 190mg/dL: Dutch Lipid Score + sequenciamento de LDLR/PCSK9.",
        "min_stars": 1,
    },

    # ── Trombofilia hereditaria ───────────────────────────────────────────────
    "thrombophilia": {
        "name_pt": "Trombofilia Hereditaria",
        "name_en": "Hereditary Thrombophilia",
        "genes": ["F5", "F2"],
        "priority_F": 1,   # anticoncepcional + gestacao + TRH
        "priority_M": 3,
        "text_F": (
            "Factor V Leiden (F5) e/ou Protrombina G20210A (F2) aumentam risco de trombose venosa. "
            "Em mulheres, o risco e amplificado por: anticoncepcionais orais com estrogeno, "
            "gravidez, e terapia de reposicao hormonal (TRH). "
            "DISCUTA COM SEU MEDICO ANTES de iniciar anticoncepcional oral, planejar gravidez ou iniciar TRH. "
            "Alternativas sem estrogeno podem ser mais seguras."
        ),
        "text_M": (
            "Factor V Leiden (F5) e/ou Protrombina G20210A (F2) aumentam risco de trombose venosa profunda (TVP) "
            "e embolia pulmonar. Risco aumenta com imobilizacao prolongada (viagens longas, pos-cirurgia). "
            "Informe qualquer medico/cirurgiao sobre este resultado antes de procedimentos."
        ),
        "text_neutral": (
            "Variante de trombofilia detectada. Risco aumentado de trombose venosa. "
            "Informe todos os seus medicos sobre este resultado."
        ),
        "evidence": "ClinVar 2-3 estrelas. F5 Leiden: OR ~5x heterozigoto, ~50x homozigoto. F2 G20210A: OR ~3x.",
        "confirm": "Teste especifico de resistencia a proteina C ativada (F5) ou PCR para G20210A (F2). Consultar hematologista.",
        "min_stars": 0,  # F5 is classified as drug_response in ClinVar, not pathogenic
    },

    # ── Hemocromatose hereditaria ─────────────────────────────────────────────
    "hemochromatosis": {
        "name_pt": "Hemocromatose Hereditaria",
        "name_en": "Hereditary Hemochromatosis",
        "genes": ["HFE"],
        "priority_F": 3,   # protegida ate menopausa
        "priority_M": 1,   # manifesta mais cedo
        "text_F": (
            "HFE C282Y e/ou H63D alteram a absorcao de ferro. Penetrancia incompleta — nem todos desenvolvem doenca. "
            "Mulheres pre-menopausa sao parcialmente protegidas pela perda menstrual de ferro. "
            "Apos a menopausa: monitorar ferritina anualmente. Se ferritina > 200ng/mL: avaliacao hepatica."
        ),
        "text_M": (
            "HFE C282Y e/ou H63D alteram a absorcao de ferro. Homens tendem a manifestar sintomas mais cedo "
            "(40-60 anos): fadiga, dor articular, bronze da pele, diabetes. "
            "Monitorar ferritina anualmente. Se ferritina > 300ng/mL: avaliacao hepatica. "
            "Doacao de sangue regular e terapeutica se ferritina elevada."
        ),
        "text_neutral": (
            "Variante HFE detectada. Risco de acumulo de ferro. Monitorar ferritina periodicamente."
        ),
        "evidence": "ClinVar 1-2 estrelas. Penetrancia variavel (~28% C282Y homozigotos desenvolvem doenca clinica).",
        "confirm": "Ferritina serico + saturacao de transferrina. Se elevados: genotipagem HFE confirmatoria + avaliacao hepatica.",
        "min_stars": 0,
    },

    # ── Deficiencia de Alfa-1 Antitripsina ────────────────────────────────────
    "a1at": {
        "name_pt": "Deficiencia de Alfa-1 Antitripsina",
        "name_en": "Alpha-1 Antitrypsin Deficiency",
        "genes": ["SERPINA1"],
        "priority_F": 2,
        "priority_M": 2,
        "text_F": None,  # same for both
        "text_M": None,
        "text_neutral": (
            "Variante SERPINA1 (alelo Z e/ou S) detectada. Deficiencia de alfa-1 antitripsina "
            "pode causar doenca pulmonar (enfisema/DPOC, especialmente em fumantes) e hepatica (cirrose). "
            "Prevalencia de portadores: ~1:25 em europeus. "
            "NAO FUME — tabagismo acelera drasticamente a destruicao pulmonar em portadores. "
            "Dosagem de alfa-1 antitripsina no sangue confirma ou exclui deficiencia clinica."
        ),
        "evidence": "ClinVar 2 estrelas para alelo Z (rs28929474). Alelo S nao confirmado em nossa base.",
        "confirm": "Dosagem serica de alfa-1 antitripsina. Se baixa: fenotipagem/genotipagem confirmatoria + espirometria.",
        "min_stars": 1,
    },

    # ── Melanoma familiar / Sindrome do nevo displasico ───────────────────────
    "melanoma": {
        "name_pt": "Melanoma Familiar",
        "name_en": "Familial Melanoma",
        "genes": ["CDKN2A", "MC1R"],
        "priority_F": 2,
        "priority_M": 2,
        "text_F": None,
        "text_M": None,
        "text_neutral": (
            "Variante em gene associado a melanoma hereditario detectada. "
            "CDKN2A (p16) e o principal gene de melanoma familiar — portadores tem risco de 60-90% ao longo da vida. "
            "MC1R (variantes de cabelo ruivo/pele clara) aumenta o risco 2-4x independentemente. "
            "Autoexame de pele mensal, dermatoscopia anual e protecao solar rigorosa sao essenciais. "
            "Evite bronzeamento artificial."
        ),
        "evidence": "ClinVar 2 estrelas para CDKN2A. MC1R bem documentado em GWAS de melanoma.",
        "confirm": "Dermatoscopia digital anual. Painel genetico de melanoma familiar se CDKN2A detectado. Encaminhamento a dermatologista.",
        "min_stars": 0,  # MC1R may have low stars but well-established
    },

    # ── Cancer gastrico hereditario difuso ────────────────────────────────────
    "gastric": {
        "name_pt": "Cancer Gastrico Hereditario Difuso",
        "name_en": "Hereditary Diffuse Gastric Cancer",
        "genes": ["CDH1"],
        "priority_F": 2,
        "priority_M": 2,
        "text_F": (
            "Variante no gene CDH1 (E-caderina) detectada. Associado a cancer gastrico difuso hereditario "
            "(risco ~70% ao longo da vida) e cancer lobular de mama em mulheres (risco ~40%). "
            "Endoscopia de rastreamento a partir dos 18-20 anos. Gastrectomia profilatica e discutida com especialista. "
            "Para mulheres: rastreamento mamario intensificado (ressonancia + mamografia)."
        ),
        "text_M": (
            "Variante no gene CDH1 (E-caderina) detectada. Associado a cancer gastrico difuso hereditario "
            "(risco ~70% ao longo da vida). Endoscopia de rastreamento a partir dos 18-20 anos. "
            "Gastrectomia profilatica e discutida com especialista."
        ),
        "text_neutral": (
            "Variante CDH1 detectada. Gene associado a cancer gastrico difuso hereditario (risco ate ~70%). "
            "Confirmacao clinica essencial."
        ),
        "evidence": "ClinVar 2 estrelas. CDH1 tem diretriz IGCLC (International Gastric Cancer Linkage Consortium).",
        "confirm": "Sequenciamento clinico de CDH1. Endoscopia com biopsias aleatorias. Consulta com oncogeneticista e gastroenterologista.",
        "min_stars": 1,
    },

    # ── Cancer renal hereditario ──────────────────────────────────────────────
    "renal": {
        "name_pt": "Cancer Renal Hereditario",
        "name_en": "Hereditary Renal Cancer",
        "genes": ["VHL", "FH"],
        "priority_F": 2,
        "priority_M": 2,
        "text_F": (
            "Variante em gene de predisposicao a cancer renal detectada. "
            "VHL (Von Hippel-Lindau): risco de carcinoma renal de celulas claras, hemangioblastomas e feocromocitomas. "
            "FH (Fumarato hidratase / HLRCC): cancer renal papilar tipo 2 agressivo + leiomiomas uterinos em mulheres. "
            "Para mulheres com FH: atencao a leiomiomas (miomas) uterinos de aparecimento precoce."
        ),
        "text_M": (
            "Variante em gene de predisposicao a cancer renal detectada. "
            "VHL (Von Hippel-Lindau): risco de carcinoma renal, hemangioblastomas e feocromocitomas. "
            "FH (HLRCC): cancer renal papilar tipo 2, agressivo e de tratamento urgente se detectado."
        ),
        "text_neutral": (
            "Variante em gene de cancer renal hereditario detectada (VHL ou FH). "
            "Confirmacao clinica e imagem abdominal recomendadas."
        ),
        "evidence": "ClinVar 2 estrelas para ambos. VHL e FH tem diretrizes de rastreamento por imagem.",
        "confirm": "Ressonancia abdominal anual. Sequenciamento clinico de VHL/FH. Consulta com urologista e oncogeneticista.",
        "min_stars": 1,
    },

    # ── Neoplasia Endocrina Multipla / Cancer medular de tireoide ─────────────
    "men2_thyroid": {
        "name_pt": "Neoplasia Endocrina Multipla tipo 2 / Cancer Medular de Tireoide",
        "name_en": "Multiple Endocrine Neoplasia type 2 / Medullary Thyroid Cancer",
        "genes": ["RET"],
        "priority_F": 2,
        "priority_M": 2,
        "text_F": None,
        "text_M": None,
        "text_neutral": (
            "Variante no proto-oncogene RET detectada. Associado a Neoplasia Endocrina Multipla tipo 2 (MEN2): "
            "cancer medular de tireoide (penetrancia quase 100%), feocromocitoma (50%) e hiperparatireoidismo (20-30%). "
            "MEN2 e uma das sindromes hereditarias de cancer mais acionaveis — tireoidectomia profilatica "
            "pode ser indicada dependendo da variante especifica. "
            "Calcitonina serica e ultrassom de tireoide sao os exames de rastreamento."
        ),
        "evidence": "ClinVar 2 estrelas. RET tem diretriz ATA (American Thyroid Association) com codon-especifica.",
        "confirm": "Calcitonina serica + ultrassom tireoide. Sequenciamento clinico de RET com identificacao do codon. Consulta endocrinologista/oncogeneticista.",
        "min_stars": 1,
    },

    # ── Sindrome de Li-Fraumeni ───────────────────────────────────────────────
    "li_fraumeni": {
        "name_pt": "Sindrome de Li-Fraumeni",
        "name_en": "Li-Fraumeni Syndrome",
        "genes": ["TP53"],
        "priority_F": 1,
        "priority_M": 1,
        "text_F": (
            "Variante no gene TP53 (guardiao do genoma) detectada. Sindrome de Li-Fraumeni confere risco "
            "extremamente elevado de multiplos canceres ao longo da vida (~70% em mulheres ate 60 anos): "
            "mama (mais frequente em mulheres), sarcomas, leucemias, tumores cerebrais, adrenais. "
            "Protocolo de rastreamento intensivo (Toronto/NCCN) inclui ressonancia de corpo inteiro anual. "
            "CONFIRMACAO CLINICA URGENTE."
        ),
        "text_M": (
            "Variante no gene TP53 detectada. Sindrome de Li-Fraumeni confere risco extremamente elevado "
            "de multiplos canceres (~40% em homens ate 60 anos): sarcomas, leucemias, tumores cerebrais, "
            "adrenais, cancer de prostata precoce. "
            "Protocolo de rastreamento intensivo (Toronto/NCCN) inclui ressonancia de corpo inteiro anual. "
            "CONFIRMACAO CLINICA URGENTE."
        ),
        "text_neutral": (
            "Variante TP53 detectada. Sindrome de Li-Fraumeni: risco muito elevado de multiplos canceres. "
            "Confirmacao clinica URGENTE."
        ),
        "evidence": "ClinVar 2-3 estrelas. TP53 tem protocolo de rastreamento Toronto/NCCN.",
        "confirm": "Sequenciamento clinico de TP53 URGENTE. Se confirmado: ressonancia de corpo inteiro anual + protocolo Toronto. Consulta oncogeneticista imediata.",
        "min_stars": 1,
    },

    # ── Sindrome de Cowden (PTEN) ─────────────────────────────────────────────
    "cowden": {
        "name_pt": "Sindrome de Cowden / PTEN Hamartoma",
        "name_en": "Cowden Syndrome / PTEN Hamartoma",
        "genes": ["PTEN"],
        "priority_F": 1,
        "priority_M": 2,
        "text_F": (
            "Variante no gene PTEN detectada. Sindrome de Cowden aumenta risco de: "
            "cancer de mama (ate 85%), cancer de tireoide (35%), cancer de endometrio (28%), cancer renal e colorretal. "
            "Para mulheres: rastreamento mamario intensificado (ressonancia anual a partir dos 30), "
            "ultrassom de tireoide anual, rastreamento endometrial a partir dos 35. "
            "CONFIRMACAO CLINICA RECOMENDADA."
        ),
        "text_M": (
            "Variante no gene PTEN detectada. Sindrome de Cowden aumenta risco de: "
            "cancer de tireoide (35%), cancer renal, cancer colorretal e cancer de prostata. "
            "Rastreamento: ultrassom de tireoide anual, colonoscopia a partir dos 35, PSA anual a partir dos 40. "
            "CONFIRMACAO CLINICA RECOMENDADA."
        ),
        "text_neutral": (
            "Variante PTEN detectada. Sindrome de Cowden: risco aumentado de multiplos canceres "
            "(mama, tireoide, endometrio, renal, colorretal). Confirmacao clinica recomendada."
        ),
        "evidence": "ClinVar 2 estrelas. PTEN tem diretriz NCCN de manejo.",
        "confirm": "Sequenciamento clinico de PTEN. Se confirmado: protocolo de rastreamento NCCN multi-orgao. Consulta oncogeneticista.",
        "min_stars": 1,
    },

    # ── Paraganglioma/Feocromocitoma hereditario ──────────────────────────────
    "paraganglioma": {
        "name_pt": "Paraganglioma / Feocromocitoma Hereditario",
        "name_en": "Hereditary Paraganglioma / Pheochromocytoma",
        "genes": ["SDHB", "SDHD"],
        "priority_F": 2,
        "priority_M": 2,
        "text_F": None,
        "text_M": None,
        "text_neutral": (
            "Variante em gene SDH (succinato desidrogenase) detectada. Associado a paragangliomas "
            "(tumores neuroendocrinos, frequentemente cabeca/pescoco) e feocromocitomas (adrenal). "
            "SDHB: maior risco de malignidade (~30%) e cancer renal. "
            "SDHD: heranca paterna (so manifesta se herdado do pai). "
            "Rastreamento por imagem (ressonancia) e metanefrinas urinarias/plasmaticas recomendados."
        ),
        "evidence": "ClinVar 2 estrelas. SDHx tem diretriz de rastreamento por imagem.",
        "confirm": "Metanefrinas fracionadas (urina 24h ou plasma). Ressonancia de abdome e cabeca/pescoco. Sequenciamento clinico SDHx.",
        "min_stars": 1,
    },
}


def analyze_hereditary_conditions(disease_findings: dict, profile: dict) -> dict:
    """Cross-reference disease findings with hereditary condition matrix.

    Returns {
        "conditions": [{
            "key": str,
            "name": str,
            "genes_found": [str],
            "gene_details": [{gene, rsid, genotype, stars, traits}],
            "priority": int,
            "text": str,
            "evidence": str,
            "confirm": str,
        }],
        "sex": str or None,
        "sex_inferred": bool,
    }
    """
    sex = profile.get("sex")
    sex_inferred = profile.get("sex_inferred", False)
    conditions_found = []

    if not disease_findings:
        return {"conditions": [], "sex": sex, "sex_inferred": sex_inferred}

    # Collect all pathogenic/likely_pathogenic findings by gene
    all_patho = (
        disease_findings.get("pathogenic", [])
        + disease_findings.get("likely_pathogenic", [])
    )
    # Also check risk_factor and drug_response for F5/HFE
    all_risk = disease_findings.get("risk_factor", [])
    all_drug = disease_findings.get("drug_response", [])
    all_variants = all_patho + all_risk + all_drug

    gene_variants = {}
    for v in all_variants:
        gene = v.get("gene", "")
        if gene:
            if gene not in gene_variants:
                gene_variants[gene] = []
            gene_variants[gene].append(v)

    # Match against condition matrix
    for key, cond in HEREDITARY_CONDITIONS.items():
        genes_found = [g for g in cond["genes"] if g in gene_variants]
        if not genes_found:
            continue

        # Check minimum star threshold
        max_stars = 0
        gene_details = []
        for gene in genes_found:
            for v in gene_variants[gene]:
                stars = v.get("gold_stars", 0)
                max_stars = max(max_stars, stars)
                gene_details.append({
                    "gene": gene,
                    "rsid": v.get("rsid", ""),
                    "genotype": v.get("user_genotype", "?"),
                    "stars": stars,
                    "traits": v.get("traits", "")[:80],
                    "zygosity": v.get("zygosity_status", ""),
                    "significance": v.get("clinical_significance", ""),
                })

        if max_stars < cond["min_stars"]:
            continue

        # Select sex-appropriate text
        if sex == "F" and cond.get("text_F"):
            text = cond["text_F"]
            priority = cond["priority_F"]
        elif sex == "M" and cond.get("text_M"):
            text = cond["text_M"]
            priority = cond["priority_M"]
        else:
            text = cond["text_neutral"]
            priority = min(cond["priority_F"], cond["priority_M"])

        conditions_found.append({
            "key": key,
            "name": cond["name_pt"],
            "name_en": cond["name_en"],
            "genes_found": genes_found,
            "gene_details": gene_details,
            "priority": priority,
            "text": text,
            "evidence": cond["evidence"],
            "confirm": cond["confirm"],
            "max_stars": max_stars,
        })

    # Sort by priority (lower = more important)
    conditions_found.sort(key=lambda c: c["priority"])

    return {
        "conditions": conditions_found,
        "sex": sex,
        "sex_inferred": sex_inferred,
    }
