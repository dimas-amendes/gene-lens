"""
Modulo de condicoes hereditarias com routing por sexo biologico.

Organizado por condicao clinica com contexto sex-aware:
- Texto do relatorio muda conforme sexo
- Prioridade de exibicao muda conforme sexo
- Evidencia baseada em ClinVar (gold stars)

Formato: condicao -> genes -> prioridade -> texto -> evidencia -> confirmacao

IMPORTANTE: Nenhuma destas conclusoes constitui diagnostico.
Variantes de chips de consumo tem ~40% de falso positivo.

Bilingue PT/EN: campos textuais user-facing tem variante `_en`.
Use `_pick(item, key, lang)` para resolver no idioma correto.
"""

from src.i18n import Lang
# ══════════════════════════════════════════════════════════════════════════════
# CONDITION MATRIX
# ══════════════════════════════════════════════════════════════════════════════

HEREDITARY_CONDITIONS = {

    # ── Cancer hereditario de mama/ovario (HBOC) ─────────────────────────────
    "hboc": {
        "name_pt": "Cancer Hereditario de Mama e Ovario (HBOC)",
        "name_en": "Hereditary Breast & Ovarian Cancer (HBOC)",
        "genes": ["BRCA1", "BRCA2", "PALB2", "ATM", "CHEK2", "BRIP1"],
        "priority_F": 1,
        "priority_M": 3,
        "text_F": (
            "Variantes nestes genes estao associadas a risco significativamente aumentado de "
            "cancer de mama (ate 70% ao longo da vida para BRCA1) e cancer de ovario (ate 44% para BRCA1). "
            "A confirmacao clinica e OBRIGATORIA — chips de consumo nao sao teste diagnostico para BRCA. "
            "Se confirmado, protocolos de rastreamento intensificado (ressonancia mamaria anual, "
            "considerar mastectomia/ooforectomia profilatica) devem ser discutidos com oncogeneticista."
        ),
        "text_F_en": (
            "Variants in these genes are associated with significantly increased risk of "
            "breast cancer (up to 70% lifetime for BRCA1) and ovarian cancer (up to 44% for BRCA1). "
            "Clinical confirmation is REQUIRED — consumer chips are not diagnostic tests for BRCA. "
            "If confirmed, intensified screening protocols (annual breast MRI, "
            "consider prophylactic mastectomy/oophorectomy) should be discussed with a cancer geneticist."
        ),
        "text_M": (
            "Embora associados principalmente a cancer feminino, BRCA1/2 tambem aumentam risco em homens: "
            "cancer de mama masculino (BRCA2: risco ~7%), cancer de prostata (BRCA2: risco ~20% ao longo da vida), "
            "e cancer de pancreas. Confirmacao clinica OBRIGATORIA. "
            "Se confirmado, rastreamento de prostata precoce (PSA a partir dos 40) e vigilancia pancreatica."
        ),
        "text_M_en": (
            "Although mainly associated with female cancers, BRCA1/2 also increase risk in men: "
            "male breast cancer (BRCA2: ~7% risk), prostate cancer (BRCA2: ~20% lifetime risk), "
            "and pancreatic cancer. Clinical confirmation REQUIRED. "
            "If confirmed, early prostate screening (PSA from age 40) and pancreatic surveillance."
        ),
        "text_neutral": (
            "Genes do espectro HBOC detectados. Risco varia conforme sexo biologico e gene especifico. "
            "Confirmacao por sequenciamento clinico e OBRIGATORIA — chips de consumo tem alta taxa de erro para estes genes."
        ),
        "text_neutral_en": (
            "HBOC spectrum genes detected. Risk varies by biological sex and specific gene. "
            "Confirmation by clinical sequencing is REQUIRED — consumer chips have a high error rate for these genes."
        ),
        "evidence": "ClinVar 2-3 estrelas. BRCA1/2 tem diretriz NCCN de manejo clinico.",
        "evidence_en": "ClinVar 2-3 stars. BRCA1/2 has NCCN clinical management guidelines.",
        "confirm": "Sequenciamento clinico de painel de cancer hereditario (Invitae, Myriad, laboratorio local). Consultar oncogeneticista.",
        "confirm_en": "Clinical sequencing of hereditary cancer panel (Invitae, Myriad, local lab). Consult a cancer geneticist.",
        "min_stars": 1,
    },

    # ── Cancer hereditario de prostata ────────────────────────────────────────
    "prostate": {
        "name_pt": "Cancer Hereditario de Prostata",
        "name_en": "Hereditary Prostate Cancer",
        "genes": ["HOXB13"],
        "priority_F": 5,
        "priority_M": 1,
        "text_F": (
            "HOXB13 G84E e uma variante de predisposicao a cancer de prostata. "
            "Para voce, nao ha risco direto, mas voce pode transmitir para filhos homens. "
            "Filhos devem ser informados para rastreamento precoce de prostata."
        ),
        "text_F_en": (
            "HOXB13 G84E is a prostate cancer predisposition variant. "
            "There is no direct risk for you, but you may transmit it to male children. "
            "Sons should be informed for early prostate screening."
        ),
        "text_M": (
            "HOXB13 G84E esta associado a risco ~3-5x de cancer de prostata, especialmente inicio precoce (<55 anos). "
            "Discuta com urologista: PSA anual a partir dos 40 anos (em vez dos 50 padrao). "
            "Confirmacao clinica recomendada."
        ),
        "text_M_en": (
            "HOXB13 G84E is associated with a ~3-5x risk of prostate cancer, especially early onset (<55 years). "
            "Discuss with a urologist: annual PSA from age 40 (instead of the standard age 50). "
            "Clinical confirmation recommended."
        ),
        "text_neutral": (
            "Variante HOXB13 detectada. Associada a predisposicao a cancer de prostata hereditario."
        ),
        "text_neutral_en": (
            "HOXB13 variant detected. Associated with predisposition to hereditary prostate cancer."
        ),
        "evidence": "ClinVar 2 estrelas. HOXB13 G84E e a variante classica de cancer de prostata hereditario (NCI).",
        "evidence_en": "ClinVar 2 stars. HOXB13 G84E is the classic hereditary prostate cancer variant (NCI).",
        "confirm": "PSA e toque retal anual a partir dos 40 (homens). Painel genetico de cancer de prostata.",
        "confirm_en": "Annual PSA and digital rectal exam from age 40 (men). Hereditary prostate cancer gene panel.",
        "min_stars": 1,
    },

    # ── Sindrome de Lynch ─────────────────────────────────────────────────────
    "lynch": {
        "name_pt": "Sindrome de Lynch (Cancer Colorretal/Endometrial Hereditario)",
        "name_en": "Lynch Syndrome (Hereditary Colorectal/Endometrial Cancer)",
        "genes": ["MLH1", "MSH2", "MSH6", "PMS2", "EPCAM"],
        "priority_F": 1,
        "priority_M": 1,
        "text_F": (
            "Sindrome de Lynch aumenta risco de cancer colorretal (ate 80%), endometrio (ate 60%), "
            "ovario (ate 24%) e outros. Colonoscopia a cada 1-2 anos a partir dos 25 e diretriz padrao. "
            "Para mulheres: discutir tambem rastreamento endometrial e opcoes de reducao de risco ovariano. "
            "Confirmacao clinica OBRIGATORIA."
        ),
        "text_F_en": (
            "Lynch syndrome increases risk of colorectal (up to 80%), endometrial (up to 60%), "
            "ovarian (up to 24%) and other cancers. Colonoscopy every 1-2 years from age 25 is standard guidance. "
            "For women: also discuss endometrial screening and ovarian risk-reduction options. "
            "Clinical confirmation REQUIRED."
        ),
        "text_M": (
            "Sindrome de Lynch aumenta risco de cancer colorretal (ate 80%), prostata, "
            "estomago e trato urinario. Colonoscopia a cada 1-2 anos a partir dos 25 e diretriz padrao. "
            "Confirmacao clinica OBRIGATORIA."
        ),
        "text_M_en": (
            "Lynch syndrome increases risk of colorectal (up to 80%), prostate, "
            "stomach and urinary tract cancers. Colonoscopy every 1-2 years from age 25 is standard guidance. "
            "Clinical confirmation REQUIRED."
        ),
        "text_neutral": (
            "Variante em gene de reparo de DNA (mismatch repair) detectada. "
            "Sindrome de Lynch aumenta risco de multiplos canceres. Confirmacao clinica essencial."
        ),
        "text_neutral_en": (
            "Variant detected in a DNA mismatch repair gene. "
            "Lynch syndrome increases the risk of multiple cancers. Clinical confirmation essential."
        ),
        "evidence": "ClinVar 3 estrelas. Diretriz NCCN de rastreamento disponivel.",
        "evidence_en": "ClinVar 3 stars. NCCN screening guidelines available.",
        "confirm": "Painel de cancer hereditario + imunohistoquimica MMR em tumores previos. Colonoscopia + consulta oncogeneticista.",
        "confirm_en": "Hereditary cancer panel + MMR immunohistochemistry on prior tumors. Colonoscopy + cancer geneticist consultation.",
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
        "text_F_en": (
            "APC (familial adenomatous polyposis) and MUTYH (MAP) strongly increase the risk of colorectal cancer. "
            "FAP (APC): hundreds to thousands of polyps, ~100% colorectal cancer risk without intervention. "
            "MAP (MUTYH): recessive inheritance — both alleles must be altered. "
            "Screening colonoscopy essential. Clinical confirmation REQUIRED."
        ),
        "text_M": None,
        "text_M_en": None,
        "text_neutral": (
            "Variante em gene de polipose hereditaria detectada. "
            "Risco significativamente aumentado de cancer colorretal. Confirmacao clinica OBRIGATORIA."
        ),
        "text_neutral_en": (
            "Variant in a hereditary polyposis gene detected. "
            "Significantly increased risk of colorectal cancer. Clinical confirmation REQUIRED."
        ),
        "evidence": "ClinVar 2 estrelas. APC I1307K confirmado como patogenico.",
        "evidence_en": "ClinVar 2 stars. APC I1307K confirmed as pathogenic.",
        "confirm": "Colonoscopia + sequenciamento de APC/MUTYH. Consulta com gastroenterologista e oncogeneticista.",
        "confirm_en": "Colonoscopy + APC/MUTYH sequencing. Consultation with gastroenterologist and cancer geneticist.",
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
        "text_F_en": (
            "Familial hypercholesterolemia causes very high LDL cholesterol levels from childhood, "
            "leading to early cardiovascular disease. Prevalence ~1:250. "
            "Women are partially protected by estrogen until menopause, but risk persists. "
            "Lipid panel is REQUIRED. Statins are the mainstay of treatment if confirmed."
        ),
        "text_M": (
            "Hipercolesterolemia familiar causa LDL muito elevado desde a infancia, "
            "com risco de infarto precoce (homens: evento cardiovascular ~50% ate os 50 anos sem tratamento). "
            "Perfil lipidico OBRIGATORIO. Estatinas sao a base do tratamento se confirmado."
        ),
        "text_M_en": (
            "Familial hypercholesterolemia causes very high LDL from childhood, "
            "with risk of early heart attack (men: ~50% cardiovascular event rate by age 50 without treatment). "
            "Lipid panel REQUIRED. Statins are the mainstay of treatment if confirmed."
        ),
        "text_neutral": (
            "Variante em gene de metabolismo do colesterol detectada. "
            "Hipercolesterolemia familiar afeta ~1:250 pessoas. Perfil lipidico e essencial."
        ),
        "text_neutral_en": (
            "Variant in a cholesterol metabolism gene detected. "
            "Familial hypercholesterolemia affects ~1:250 people. A lipid panel is essential."
        ),
        "evidence": "ClinVar 2 estrelas para LDLR. PCSK9 com evidencia limitada mas crescente.",
        "evidence_en": "ClinVar 2 stars for LDLR. PCSK9 has limited but growing evidence.",
        "confirm": "Perfil lipidico completo (LDL, HDL, TG, CT). Se LDL > 190mg/dL: Dutch Lipid Score + sequenciamento de LDLR/PCSK9.",
        "confirm_en": "Complete lipid panel (LDL, HDL, TG, total cholesterol). If LDL > 190 mg/dL: Dutch Lipid Score + LDLR/PCSK9 sequencing.",
        "min_stars": 1,
    },

    # ── Trombofilia hereditaria ───────────────────────────────────────────────
    "thrombophilia": {
        "name_pt": "Trombofilia Hereditaria",
        "name_en": "Hereditary Thrombophilia",
        "genes": ["F5", "F2"],
        "priority_F": 1,
        "priority_M": 3,
        "text_F": (
            "Factor V Leiden (F5) e/ou Protrombina G20210A (F2) aumentam risco de trombose venosa. "
            "Em mulheres, o risco e amplificado por: anticoncepcionais orais com estrogeno, "
            "gravidez, e terapia de reposicao hormonal (TRH). "
            "DISCUTA COM SEU MEDICO ANTES de iniciar anticoncepcional oral, planejar gravidez ou iniciar TRH. "
            "Alternativas sem estrogeno podem ser mais seguras."
        ),
        "text_F_en": (
            "Factor V Leiden (F5) and/or Prothrombin G20210A (F2) increase the risk of venous thrombosis. "
            "In women, risk is amplified by: estrogen-containing oral contraceptives, "
            "pregnancy, and hormone replacement therapy (HRT). "
            "DISCUSS WITH YOUR PHYSICIAN BEFORE starting oral contraceptives, planning pregnancy, or starting HRT. "
            "Estrogen-free alternatives may be safer."
        ),
        "text_M": (
            "Factor V Leiden (F5) e/ou Protrombina G20210A (F2) aumentam risco de trombose venosa profunda (TVP) "
            "e embolia pulmonar. Risco aumenta com imobilizacao prolongada (viagens longas, pos-cirurgia). "
            "Informe qualquer medico/cirurgiao sobre este resultado antes de procedimentos."
        ),
        "text_M_en": (
            "Factor V Leiden (F5) and/or Prothrombin G20210A (F2) increase the risk of deep vein thrombosis (DVT) "
            "and pulmonary embolism. Risk increases with prolonged immobilization (long travel, post-surgery). "
            "Inform any physician/surgeon about this result before procedures."
        ),
        "text_neutral": (
            "Variante de trombofilia detectada. Risco aumentado de trombose venosa. "
            "Informe todos os seus medicos sobre este resultado."
        ),
        "text_neutral_en": (
            "Thrombophilia variant detected. Increased risk of venous thrombosis. "
            "Inform all of your physicians about this result."
        ),
        "evidence": "ClinVar 2-3 estrelas. F5 Leiden: OR ~5x heterozigoto, ~50x homozigoto. F2 G20210A: OR ~3x.",
        "evidence_en": "ClinVar 2-3 stars. F5 Leiden: OR ~5x heterozygous, ~50x homozygous. F2 G20210A: OR ~3x.",
        "confirm": "Teste especifico de resistencia a proteina C ativada (F5) ou PCR para G20210A (F2). Consultar hematologista.",
        "confirm_en": "Specific activated protein C resistance assay (F5) or PCR for G20210A (F2). Consult a hematologist.",
        "min_stars": 0,
    },

    # ── Hemocromatose hereditaria ─────────────────────────────────────────────
    "hemochromatosis": {
        "name_pt": "Hemocromatose Hereditaria",
        "name_en": "Hereditary Hemochromatosis",
        "genes": ["HFE"],
        "priority_F": 3,
        "priority_M": 1,
        "text_F": (
            "HFE C282Y e/ou H63D alteram a absorcao de ferro. Penetrancia incompleta — nem todos desenvolvem doenca. "
            "Mulheres pre-menopausa sao parcialmente protegidas pela perda menstrual de ferro. "
            "Apos a menopausa: monitorar ferritina anualmente. Se ferritina > 200ng/mL: avaliacao hepatica."
        ),
        "text_F_en": (
            "HFE C282Y and/or H63D alter iron absorption. Incomplete penetrance — not everyone develops disease. "
            "Pre-menopausal women are partially protected by menstrual iron loss. "
            "After menopause: monitor ferritin annually. If ferritin > 200 ng/mL: hepatic evaluation."
        ),
        "text_M": (
            "HFE C282Y e/ou H63D alteram a absorcao de ferro. Homens tendem a manifestar sintomas mais cedo "
            "(40-60 anos): fadiga, dor articular, bronze da pele, diabetes. "
            "Monitorar ferritina anualmente. Se ferritina > 300ng/mL: avaliacao hepatica. "
            "Doacao de sangue regular e terapeutica se ferritina elevada."
        ),
        "text_M_en": (
            "HFE C282Y and/or H63D alter iron absorption. Men tend to develop symptoms earlier "
            "(ages 40-60): fatigue, joint pain, bronze skin, diabetes. "
            "Monitor ferritin annually. If ferritin > 300 ng/mL: hepatic evaluation. "
            "Regular blood donation is therapeutic if ferritin is elevated."
        ),
        "text_neutral": (
            "Variante HFE detectada. Risco de acumulo de ferro. Monitorar ferritina periodicamente."
        ),
        "text_neutral_en": (
            "HFE variant detected. Risk of iron overload. Monitor ferritin periodically."
        ),
        "evidence": "ClinVar 1-2 estrelas. Penetrancia variavel (~28% C282Y homozigotos desenvolvem doenca clinica).",
        "evidence_en": "ClinVar 1-2 stars. Variable penetrance (~28% of C282Y homozygotes develop clinical disease).",
        "confirm": "Ferritina serico + saturacao de transferrina. Se elevados: genotipagem HFE confirmatoria + avaliacao hepatica.",
        "confirm_en": "Serum ferritin + transferrin saturation. If elevated: confirmatory HFE genotyping + hepatic evaluation.",
        "min_stars": 0,
    },

    # ── Deficiencia de Alfa-1 Antitripsina ────────────────────────────────────
    "a1at": {
        "name_pt": "Deficiencia de Alfa-1 Antitripsina",
        "name_en": "Alpha-1 Antitrypsin Deficiency",
        "genes": ["SERPINA1"],
        "priority_F": 2,
        "priority_M": 2,
        "text_F": None,
        "text_F_en": None,
        "text_M": None,
        "text_M_en": None,
        "text_neutral": (
            "Variante SERPINA1 (alelo Z e/ou S) detectada. Deficiencia de alfa-1 antitripsina "
            "pode causar doenca pulmonar (enfisema/DPOC, especialmente em fumantes) e hepatica (cirrose). "
            "Prevalencia de portadores: ~1:25 em europeus. "
            "NAO FUME — tabagismo acelera drasticamente a destruicao pulmonar em portadores. "
            "Dosagem de alfa-1 antitripsina no sangue confirma ou exclui deficiencia clinica."
        ),
        "text_neutral_en": (
            "SERPINA1 variant (Z and/or S allele) detected. Alpha-1 antitrypsin deficiency "
            "may cause pulmonary disease (emphysema/COPD, especially in smokers) and hepatic disease (cirrhosis). "
            "Carrier prevalence: ~1:25 in Europeans. "
            "DO NOT SMOKE — smoking dramatically accelerates lung destruction in carriers. "
            "Serum alpha-1 antitrypsin level confirms or rules out clinical deficiency."
        ),
        "evidence": "ClinVar 2 estrelas para alelo Z (rs28929474). Alelo S nao confirmado em nossa base.",
        "evidence_en": "ClinVar 2 stars for Z allele (rs28929474). S allele not confirmed in our database.",
        "confirm": "Dosagem serica de alfa-1 antitripsina. Se baixa: fenotipagem/genotipagem confirmatoria + espirometria.",
        "confirm_en": "Serum alpha-1 antitrypsin level. If low: confirmatory phenotyping/genotyping + spirometry.",
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
        "text_F_en": None,
        "text_M": None,
        "text_M_en": None,
        "text_neutral": (
            "Variante em gene associado a melanoma hereditario detectada. "
            "CDKN2A (p16) e o principal gene de melanoma familiar — portadores tem risco de 60-90% ao longo da vida. "
            "MC1R (variantes de cabelo ruivo/pele clara) aumenta o risco 2-4x independentemente. "
            "Autoexame de pele mensal, dermatoscopia anual e protecao solar rigorosa sao essenciais. "
            "Evite bronzeamento artificial."
        ),
        "text_neutral_en": (
            "Variant in a hereditary melanoma gene detected. "
            "CDKN2A (p16) is the main familial melanoma gene — carriers have a 60-90% lifetime risk. "
            "MC1R (red hair/fair skin variants) increases risk 2-4x independently. "
            "Monthly skin self-exam, annual dermoscopy and strict sun protection are essential. "
            "Avoid tanning beds."
        ),
        "evidence": "ClinVar 2 estrelas para CDKN2A. MC1R bem documentado em GWAS de melanoma.",
        "evidence_en": "ClinVar 2 stars for CDKN2A. MC1R well documented in melanoma GWAS.",
        "confirm": "Dermatoscopia digital anual. Painel genetico de melanoma familiar se CDKN2A detectado. Encaminhamento a dermatologista.",
        "confirm_en": "Annual digital dermoscopy. Familial melanoma gene panel if CDKN2A detected. Referral to a dermatologist.",
        "min_stars": 0,
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
        "text_F_en": (
            "Variant in the CDH1 gene (E-cadherin) detected. Associated with hereditary diffuse gastric cancer "
            "(~70% lifetime risk) and lobular breast cancer in women (~40% risk). "
            "Screening endoscopy from ages 18-20. Prophylactic gastrectomy is discussed with a specialist. "
            "For women: intensified breast screening (MRI + mammography)."
        ),
        "text_M": (
            "Variante no gene CDH1 (E-caderina) detectada. Associado a cancer gastrico difuso hereditario "
            "(risco ~70% ao longo da vida). Endoscopia de rastreamento a partir dos 18-20 anos. "
            "Gastrectomia profilatica e discutida com especialista."
        ),
        "text_M_en": (
            "Variant in the CDH1 gene (E-cadherin) detected. Associated with hereditary diffuse gastric cancer "
            "(~70% lifetime risk). Screening endoscopy from ages 18-20. "
            "Prophylactic gastrectomy is discussed with a specialist."
        ),
        "text_neutral": (
            "Variante CDH1 detectada. Gene associado a cancer gastrico difuso hereditario (risco ate ~70%). "
            "Confirmacao clinica essencial."
        ),
        "text_neutral_en": (
            "CDH1 variant detected. Gene associated with hereditary diffuse gastric cancer (up to ~70% risk). "
            "Clinical confirmation essential."
        ),
        "evidence": "ClinVar 2 estrelas. CDH1 tem diretriz IGCLC (International Gastric Cancer Linkage Consortium).",
        "evidence_en": "ClinVar 2 stars. CDH1 has IGCLC (International Gastric Cancer Linkage Consortium) guidelines.",
        "confirm": "Sequenciamento clinico de CDH1. Endoscopia com biopsias aleatorias. Consulta com oncogeneticista e gastroenterologista.",
        "confirm_en": "Clinical CDH1 sequencing. Endoscopy with random biopsies. Consultation with cancer geneticist and gastroenterologist.",
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
        "text_F_en": (
            "Variant in a renal cancer predisposition gene detected. "
            "VHL (Von Hippel-Lindau): risk of clear cell renal carcinoma, hemangioblastomas and pheochromocytomas. "
            "FH (Fumarate hydratase / HLRCC): aggressive type 2 papillary renal cancer + uterine leiomyomas in women. "
            "For women with FH: watch for early-onset uterine leiomyomas (fibroids)."
        ),
        "text_M": (
            "Variante em gene de predisposicao a cancer renal detectada. "
            "VHL (Von Hippel-Lindau): risco de carcinoma renal, hemangioblastomas e feocromocitomas. "
            "FH (HLRCC): cancer renal papilar tipo 2, agressivo e de tratamento urgente se detectado."
        ),
        "text_M_en": (
            "Variant in a renal cancer predisposition gene detected. "
            "VHL (Von Hippel-Lindau): risk of renal carcinoma, hemangioblastomas and pheochromocytomas. "
            "FH (HLRCC): type 2 papillary renal cancer, aggressive and requiring urgent treatment if detected."
        ),
        "text_neutral": (
            "Variante em gene de cancer renal hereditario detectada (VHL ou FH). "
            "Confirmacao clinica e imagem abdominal recomendadas."
        ),
        "text_neutral_en": (
            "Variant in a hereditary renal cancer gene detected (VHL or FH). "
            "Clinical confirmation and abdominal imaging recommended."
        ),
        "evidence": "ClinVar 2 estrelas para ambos. VHL e FH tem diretrizes de rastreamento por imagem.",
        "evidence_en": "ClinVar 2 stars for both. VHL and FH have imaging-based screening guidelines.",
        "confirm": "Ressonancia abdominal anual. Sequenciamento clinico de VHL/FH. Consulta com urologista e oncogeneticista.",
        "confirm_en": "Annual abdominal MRI. Clinical VHL/FH sequencing. Consultation with urologist and cancer geneticist.",
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
        "text_F_en": None,
        "text_M": None,
        "text_M_en": None,
        "text_neutral": (
            "Variante no proto-oncogene RET detectada. Associado a Neoplasia Endocrina Multipla tipo 2 (MEN2): "
            "cancer medular de tireoide (penetrancia quase 100%), feocromocitoma (50%) e hiperparatireoidismo (20-30%). "
            "MEN2 e uma das sindromes hereditarias de cancer mais acionaveis — tireoidectomia profilatica "
            "pode ser indicada dependendo da variante especifica. "
            "Calcitonina serica e ultrassom de tireoide sao os exames de rastreamento."
        ),
        "text_neutral_en": (
            "Variant in the RET proto-oncogene detected. Associated with Multiple Endocrine Neoplasia type 2 (MEN2): "
            "medullary thyroid cancer (near 100% penetrance), pheochromocytoma (50%) and hyperparathyroidism (20-30%). "
            "MEN2 is one of the most actionable hereditary cancer syndromes — prophylactic thyroidectomy "
            "may be indicated depending on the specific variant. "
            "Serum calcitonin and thyroid ultrasound are the screening exams."
        ),
        "evidence": "ClinVar 2 estrelas. RET tem diretriz ATA (American Thyroid Association) com codon-especifica.",
        "evidence_en": "ClinVar 2 stars. RET has codon-specific ATA (American Thyroid Association) guidelines.",
        "confirm": "Calcitonina serica + ultrassom tireoide. Sequenciamento clinico de RET com identificacao do codon. Consulta endocrinologista/oncogeneticista.",
        "confirm_en": "Serum calcitonin + thyroid ultrasound. Clinical RET sequencing with codon identification. Consultation with endocrinologist/cancer geneticist.",
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
        "text_F_en": (
            "Variant in the TP53 gene (guardian of the genome) detected. Li-Fraumeni syndrome confers an "
            "extremely elevated lifetime risk of multiple cancers (~70% in women by age 60): "
            "breast (most frequent in women), sarcomas, leukemias, brain tumors, adrenal tumors. "
            "Intensive screening protocol (Toronto/NCCN) includes annual whole-body MRI. "
            "URGENT CLINICAL CONFIRMATION."
        ),
        "text_M": (
            "Variante no gene TP53 detectada. Sindrome de Li-Fraumeni confere risco extremamente elevado "
            "de multiplos canceres (~40% em homens ate 60 anos): sarcomas, leucemias, tumores cerebrais, "
            "adrenais, cancer de prostata precoce. "
            "Protocolo de rastreamento intensivo (Toronto/NCCN) inclui ressonancia de corpo inteiro anual. "
            "CONFIRMACAO CLINICA URGENTE."
        ),
        "text_M_en": (
            "Variant in the TP53 gene detected. Li-Fraumeni syndrome confers an extremely elevated "
            "risk of multiple cancers (~40% in men by age 60): sarcomas, leukemias, brain tumors, "
            "adrenal tumors, early prostate cancer. "
            "Intensive screening protocol (Toronto/NCCN) includes annual whole-body MRI. "
            "URGENT CLINICAL CONFIRMATION."
        ),
        "text_neutral": (
            "Variante TP53 detectada. Sindrome de Li-Fraumeni: risco muito elevado de multiplos canceres. "
            "Confirmacao clinica URGENTE."
        ),
        "text_neutral_en": (
            "TP53 variant detected. Li-Fraumeni syndrome: very high risk of multiple cancers. "
            "URGENT clinical confirmation."
        ),
        "evidence": "ClinVar 2-3 estrelas. TP53 tem protocolo de rastreamento Toronto/NCCN.",
        "evidence_en": "ClinVar 2-3 stars. TP53 has Toronto/NCCN screening protocol.",
        "confirm": "Sequenciamento clinico de TP53 URGENTE. Se confirmado: ressonancia de corpo inteiro anual + protocolo Toronto. Consulta oncogeneticista imediata.",
        "confirm_en": "URGENT clinical TP53 sequencing. If confirmed: annual whole-body MRI + Toronto protocol. Immediate cancer geneticist consultation.",
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
        "text_F_en": (
            "Variant in the PTEN gene detected. Cowden syndrome increases risk of: "
            "breast cancer (up to 85%), thyroid cancer (35%), endometrial cancer (28%), renal and colorectal cancer. "
            "For women: intensified breast screening (annual MRI from age 30), "
            "annual thyroid ultrasound, endometrial screening from age 35. "
            "CLINICAL CONFIRMATION RECOMMENDED."
        ),
        "text_M": (
            "Variante no gene PTEN detectada. Sindrome de Cowden aumenta risco de: "
            "cancer de tireoide (35%), cancer renal, cancer colorretal e cancer de prostata. "
            "Rastreamento: ultrassom de tireoide anual, colonoscopia a partir dos 35, PSA anual a partir dos 40. "
            "CONFIRMACAO CLINICA RECOMENDADA."
        ),
        "text_M_en": (
            "Variant in the PTEN gene detected. Cowden syndrome increases risk of: "
            "thyroid cancer (35%), renal cancer, colorectal cancer and prostate cancer. "
            "Screening: annual thyroid ultrasound, colonoscopy from age 35, annual PSA from age 40. "
            "CLINICAL CONFIRMATION RECOMMENDED."
        ),
        "text_neutral": (
            "Variante PTEN detectada. Sindrome de Cowden: risco aumentado de multiplos canceres "
            "(mama, tireoide, endometrio, renal, colorretal). Confirmacao clinica recomendada."
        ),
        "text_neutral_en": (
            "PTEN variant detected. Cowden syndrome: increased risk of multiple cancers "
            "(breast, thyroid, endometrial, renal, colorectal). Clinical confirmation recommended."
        ),
        "evidence": "ClinVar 2 estrelas. PTEN tem diretriz NCCN de manejo.",
        "evidence_en": "ClinVar 2 stars. PTEN has NCCN management guidelines.",
        "confirm": "Sequenciamento clinico de PTEN. Se confirmado: protocolo de rastreamento NCCN multi-orgao. Consulta oncogeneticista.",
        "confirm_en": "Clinical PTEN sequencing. If confirmed: NCCN multi-organ screening protocol. Cancer geneticist consultation.",
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
        "text_F_en": None,
        "text_M": None,
        "text_M_en": None,
        "text_neutral": (
            "Variante em gene SDH (succinato desidrogenase) detectada. Associado a paragangliomas "
            "(tumores neuroendocrinos, frequentemente cabeca/pescoco) e feocromocitomas (adrenal). "
            "SDHB: maior risco de malignidade (~30%) e cancer renal. "
            "SDHD: heranca paterna (so manifesta se herdado do pai). "
            "Rastreamento por imagem (ressonancia) e metanefrinas urinarias/plasmaticas recomendados."
        ),
        "text_neutral_en": (
            "Variant in an SDH (succinate dehydrogenase) gene detected. Associated with paragangliomas "
            "(neuroendocrine tumors, frequently head/neck) and pheochromocytomas (adrenal). "
            "SDHB: higher risk of malignancy (~30%) and renal cancer. "
            "SDHD: paternal inheritance (only manifests if inherited from the father). "
            "Imaging screening (MRI) and urinary/plasma metanephrines recommended."
        ),
        "evidence": "ClinVar 2 estrelas. SDHx tem diretriz de rastreamento por imagem.",
        "evidence_en": "ClinVar 2 stars. SDHx has imaging-based screening guidelines.",
        "confirm": "Metanefrinas fracionadas (urina 24h ou plasma). Ressonancia de abdome e cabeca/pescoco. Sequenciamento clinico SDHx.",
        "confirm_en": "Fractionated metanephrines (24h urine or plasma). MRI of abdomen and head/neck. Clinical SDHx sequencing.",
        "min_stars": 1,
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# i18n helpers
# ══════════════════════════════════════════════════════════════════════════════

def _pick(item: dict, key: str, lang: Lang):
    """Return item[key_en] when lang == 'en' (and present), else item[key]."""
    if lang == "en":
        en_val = item.get(f"{key}_en")
        if en_val is not None:
            return en_val
    return item.get(key)


def analyze_hereditary_conditions(disease_findings: dict, profile: dict, lang: Lang = "en") -> dict:
    """Cross-reference disease findings with hereditary condition matrix.

    Args:
        disease_findings: dict from disease analyzer.
        profile: user profile (may contain "sex", "sex_inferred").
        lang: output language for user-facing strings ("en" or "pt").

    Returns {
        "conditions": [{
            "key": str,
            "name": str,           # localized
            "name_en": str,        # kept for compatibility
            "name_pt": str,        # kept for compatibility
            "genes_found": [str],
            "gene_details": [{gene, rsid, genotype, stars, traits}],
            "priority": int,
            "text": str,           # localized
            "evidence": str,       # localized
            "confirm": str,        # localized
        }],
        "sex": str or None,
        "sex_inferred": bool,
        "lang": str,
    }
    """
    sex = profile.get("sex")
    sex_inferred = profile.get("sex_inferred", False)
    conditions_found = []

    if not disease_findings:
        return {"conditions": [], "sex": sex, "sex_inferred": sex_inferred, "lang": lang}

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

        # Select sex-appropriate text in the requested language
        if sex == "F" and _pick(cond, "text_F", lang):
            text = _pick(cond, "text_F", lang)
            priority = cond["priority_F"]
        elif sex == "M" and _pick(cond, "text_M", lang):
            text = _pick(cond, "text_M", lang)
            priority = cond["priority_M"]
        else:
            text = _pick(cond, "text_neutral", lang)
            priority = min(cond["priority_F"], cond["priority_M"])

        # Localized name: prefer EN when lang == 'en'
        name = cond.get("name_en") if lang == "en" else cond.get("name_pt")

        conditions_found.append({
            "key": key,
            "name": name,
            "name_en": cond.get("name_en"),
            "name_pt": cond.get("name_pt"),
            "genes_found": genes_found,
            "gene_details": gene_details,
            "priority": priority,
            "text": text,
            "evidence": _pick(cond, "evidence", lang),
            "confirm": _pick(cond, "confirm", lang),
            "max_stars": max_stars,
        })

    # Sort by priority (lower = more important)
    conditions_found.sort(key=lambda c: c["priority"])

    return {
        "conditions": conditions_found,
        "sex": sex,
        "sex_inferred": sex_inferred,
        "lang": lang,
    }
