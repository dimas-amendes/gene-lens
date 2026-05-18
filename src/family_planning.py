"""
Modulo de planejamento familiar — analisa status de portador e
implicacoes reprodutivas para quem deseja ter filhos.

Foca em:
1. Condicoes recessivas onde o usuario e portador
2. Condicoes dominantes que podem ser transmitidas
3. Recomendacoes de testes para o/a parceiro(a)
4. Quando procurar aconselhamento genetico

Bilingual (PT/EN): cada campo `*_pt`/`<campo>` (PT) tem um equivalente `*_en`.
"""

from src.i18n import Lang
# Contexto reprodutivo por gene
REPRODUCTIVE_CONTEXT = {
    "CC2D2A": {
        "condition_pt": "Sindrome COACH / Sindrome de Joubert tipo 9",
        "condition_en": "COACH Syndrome / Joubert Syndrome type 9",
        "inheritance": "Autossomica recessiva",
        "inheritance_en": "Autosomal recessive",
        "carrier_risk": "Se o parceiro(a) tambem for portador: 25% de chance de filho afetado. Sindrome de Joubert causa malformacao cerebelar, atraso de desenvolvimento e problemas renais/hepaticos.",
        "carrier_risk_en": "If the partner is also a carrier: 25% chance of an affected child. Joubert syndrome causes cerebellar malformation, developmental delay, and kidney/liver problems.",
        "partner_test": "Teste de portador para CC2D2A (painel de ciliopatias)",
        "partner_test_en": "Carrier testing for CC2D2A (ciliopathy panel)",
        "severity": "grave",
        "severity_en": "severe",
        "prevalence": "Rara (~1:80.000-100.000)",
        "prevalence_en": "Rare (~1:80,000-100,000)",
    },
    "KCNQ1": {
        "condition_pt": "Sindrome do QT Longo tipo 1",
        "condition_en": "Long QT Syndrome type 1",
        "inheritance": "Autossomica dominante (mas com penetrancia variavel)",
        "inheritance_en": "Autosomal dominant (with variable penetrance)",
        "carrier_risk": "KCNQ1 pode ser dominante — cada filho tem 50% de chance de herdar a variante. Nem todos que herdam desenvolvem arritmia, mas devem ser monitorados com ECG.",
        "carrier_risk_en": "KCNQ1 can be dominant — each child has a 50% chance of inheriting the variant. Not all carriers develop arrhythmia, but they should be monitored with ECG.",
        "partner_test": "Nao e necessario teste no parceiro (dominante). Filhos devem fazer ECG.",
        "partner_test_en": "Partner testing not required (dominant). Children should undergo ECG screening.",
        "severity": "moderada-grave (tratavel)",
        "severity_en": "moderate-severe (treatable)",
        "prevalence": "~1:2.000-5.000",
        "prevalence_en": "~1:2,000-5,000",
    },
    "GATA4": {
        "condition_pt": "Doenca Cardiaca Congenita",
        "condition_en": "Congenital Heart Disease",
        "inheritance": "Autossomica dominante (penetrancia variavel)",
        "inheritance_en": "Autosomal dominant (variable penetrance)",
        "carrier_risk": "50% de chance de transmissao. Nem todos que herdam desenvolvem defeito cardiaco. Ecocardiograma fetal recomendado durante a gravidez.",
        "carrier_risk_en": "50% transmission chance. Not all carriers develop a cardiac defect. Fetal echocardiogram is recommended during pregnancy.",
        "partner_test": "Nao necessario. Acompanhamento pre-natal com ecocardiograma fetal.",
        "partner_test_en": "Not required. Prenatal follow-up with fetal echocardiogram.",
        "severity": "variavel (leve a grave)",
        "severity_en": "variable (mild to severe)",
        "prevalence": "Defeitos cardiacos congenitos: ~1:100",
        "prevalence_en": "Congenital heart defects: ~1:100",
    },
    "NOD2": {
        "condition_pt": "Suscetibilidade a Doenca de Crohn / Sindrome de Blau",
        "condition_en": "Crohn's Disease Susceptibility / Blau Syndrome",
        "inheritance": "Complexa (fator de risco, nao mendeliana simples)",
        "inheritance_en": "Complex (risk factor, not simple Mendelian)",
        "carrier_risk": "Cada alelo NOD2 variante aumenta o risco de Crohn em 2-4x, mas nao e determinista. Filhos podem herdar o alelo mas isso nao garante doenca.",
        "carrier_risk_en": "Each NOD2 variant allele raises Crohn's risk 2-4x, but it is not deterministic. Children may inherit the allele without necessarily developing the disease.",
        "partner_test": "Nao necessario — nao e condicao mendeliana classica.",
        "partner_test_en": "Not required — this is not a classical Mendelian condition.",
        "severity": "moderada (cronica, tratavel)",
        "severity_en": "moderate (chronic, treatable)",
        "prevalence": "Crohn: ~1:1.000",
        "prevalence_en": "Crohn's: ~1:1,000",
    },
    "VCL": {
        "condition_pt": "Cardiomiopatia Dilatada",
        "condition_en": "Dilated Cardiomyopathy",
        "inheritance": "Autossomica dominante",
        "inheritance_en": "Autosomal dominant",
        "carrier_risk": "50% de chance de transmissao. Cardiomiopatia pode se manifestar na idade adulta. Filhos devem fazer ecocardiograma periodico.",
        "carrier_risk_en": "50% transmission chance. Cardiomyopathy may manifest in adulthood. Children should undergo periodic echocardiograms.",
        "partner_test": "Nao necessario (dominante). Monitoramento cardiaco dos filhos.",
        "partner_test_en": "Not required (dominant). Cardiac monitoring of children.",
        "severity": "moderada-grave",
        "severity_en": "moderate-severe",
        "prevalence": "~1:2.500",
        "prevalence_en": "~1:2,500",
    },
    "PRLR": {
        "condition_pt": "Multiplos Fibroadenomas Mamarios",
        "condition_en": "Multiple Breast Fibroadenomas",
        "inheritance": "Autossomica dominante",
        "inheritance_en": "Autosomal dominant",
        "carrier_risk": "50% de chance de transmissao. Fibroadenomas sao benignos mas requerem acompanhamento. Mais relevante para filhas.",
        "carrier_risk_en": "50% transmission chance. Fibroadenomas are benign but require follow-up. More relevant for daughters.",
        "partner_test": "Nao necessario.",
        "partner_test_en": "Not required.",
        "severity": "leve (benigno)",
        "severity_en": "mild (benign)",
        "prevalence": "Relativamente comum",
        "prevalence_en": "Relatively common",
    },
    "CCDC170": {
        "condition_pt": "Suscetibilidade a Cancer de Mama",
        "condition_en": "Breast Cancer Susceptibility",
        "inheritance": "Complexa (fator de risco)",
        "inheritance_en": "Complex (risk factor)",
        "carrier_risk": "Aumenta suscetibilidade a cancer de mama. Nao e determinista. Historico familiar e mais informativo que um unico SNP.",
        "carrier_risk_en": "Increases susceptibility to breast cancer. Not deterministic. Family history is more informative than a single SNP.",
        "partner_test": "Nao necessario para este gene especificamente.",
        "partner_test_en": "Not required for this specific gene.",
        "severity": "variavel",
        "severity_en": "variable",
        "prevalence": "Cancer de mama: ~1:8 mulheres",
        "prevalence_en": "Breast cancer: ~1:8 women",
    },
    "ACKR1": {
        "condition_pt": "Sistema Sanguineo Duffy / Neutropenia Etnica Benigna",
        "condition_en": "Duffy Blood Group / Benign Ethnic Neutropenia",
        "inheritance": "Codominante",
        "inheritance_en": "Codominant",
        "carrier_risk": "Relevante para ascendencia africana. Fenotipo Duffy-negativo confere resistencia a malaria vivax. Pode causar neutropenia benigna (contagem baixa de leucocitos sem significado clinico). Informar pediatra.",
        "carrier_risk_en": "Relevant for African ancestry. The Duffy-negative phenotype confers resistance to vivax malaria. May cause benign neutropenia (low white-cell count without clinical significance). Inform the pediatrician.",
        "partner_test": "Nao necessario.",
        "partner_test_en": "Not required.",
        "severity": "benigno",
        "severity_en": "benign",
        "prevalence": "Comum em populacoes de ascendencia africana",
        "prevalence_en": "Common in populations of African ancestry",
    },
    "MSH6": {
        "condition_pt": "Sindrome de Lynch (Cancer Hereditario)",
        "condition_en": "Lynch Syndrome (Hereditary Cancer)",
        "inheritance": "Autossomica dominante",
        "inheritance_en": "Autosomal dominant",
        "carrier_risk": "50% de chance de transmissao. Filhos que herdam devem iniciar colonoscopia aos 25-30 anos. Cancer colorretal e o principal risco.",
        "carrier_risk_en": "50% transmission chance. Children who inherit should begin colonoscopy at age 25-30. Colorectal cancer is the main risk.",
        "partner_test": "Nao necessario (dominante). Filhos devem fazer teste genetico na idade adulta.",
        "partner_test_en": "Not required (dominant). Children should undergo genetic testing in adulthood.",
        "severity": "grave (prevenivel com rastreamento)",
        "severity_en": "severe (preventable with screening)",
        "prevalence": "Lynch: ~1:300",
        "prevalence_en": "Lynch: ~1:300",
    },
    "APOE": {
        "condition_pt": "Risco de Alzheimer (APOE e4)",
        "condition_en": "Alzheimer's Risk (APOE e4)",
        "inheritance": "Codominante / Fator de risco",
        "inheritance_en": "Codominant / Risk factor",
        "carrier_risk": "Cada filho tem 50% de chance de herdar o alelo e4. Ter um alelo e4 aumenta risco de Alzheimer tardio ~3x, mas NAO e determinista. Nao ha intervencao especifica para criancas — foco em estilo de vida saudavel ao longo da vida.",
        "carrier_risk_en": "Each child has a 50% chance of inheriting the e4 allele. Carrying one e4 allele raises late-onset Alzheimer's risk ~3x, but is NOT deterministic. There is no child-specific intervention — focus on healthy lifestyle across the lifespan.",
        "partner_test": "Opcional. Se parceiro tambem tem e4, filhos podem herdar e4/e4 (risco ~12x).",
        "partner_test_en": "Optional. If the partner also carries e4, children may inherit e4/e4 (~12x risk).",
        "severity": "variavel (fator de risco, nao determinista)",
        "severity_en": "variable (risk factor, not deterministic)",
        "prevalence": "APOE e4: ~14% da populacao",
        "prevalence_en": "APOE e4: ~14% of the population",
    },
    # Generic fallback for HFE
    "HFE": {
        "condition_pt": "Hemocromatose Hereditaria",
        "condition_en": "Hereditary Hemochromatosis",
        "inheritance": "Autossomica recessiva",
        "inheritance_en": "Autosomal recessive",
        "carrier_risk": "Se parceiro tambem for portador: 25% de chance de filho com hemocromatose. Hemocromatose e tratavel com flebotomia regular.",
        "carrier_risk_en": "If the partner is also a carrier: 25% chance of a child with hemochromatosis. Hemochromatosis is treatable with regular phlebotomy.",
        "partner_test": "Teste de HFE (C282Y e H63D) no parceiro.",
        "partner_test_en": "HFE testing (C282Y and H63D) in the partner.",
        "severity": "moderada (tratavel)",
        "severity_en": "moderate (treatable)",
        "prevalence": "Portadores: ~1:10 em europeus",
        "prevalence_en": "Carriers: ~1:10 in Europeans",
    },
}

# Conditions that are autosomal recessive (both parents need to be carriers)
RECESSIVE_CONDITIONS = {"CC2D2A", "HFE"}

# Conditions that are autosomal dominant (one copy is enough)
DOMINANT_CONDITIONS = {"KCNQ1", "GATA4", "VCL", "PRLR", "MSH6"}


# ── Gestational risk SNPs (from health/lifestyle findings) ────────────────────

GESTATIONAL_RISKS = {
    "MTHFR": {
        "risk_pt": "Defeitos do tubo neural (espinha bifida, anencefalia)",
        "risk_en": "Neural tube defects (spina bifida, anencephaly)",
        "detail": "Variante MTHFR reduz a conversao de acido folico em sua forma ativa (metilfolato). "
                  "A literatura associa esta variante a risco aumentado de defeitos do tubo neural. "
                  "Protocolos clinicos recomendam suplementacao pre-concepcional de folato, mas a forma e dose "
                  "devem ser definidas pelo obstetra com base no seu genotipo.",
        "detail_en": "The MTHFR variant reduces conversion of folic acid to its active form (methylfolate). "
                     "The literature associates this variant with increased risk of neural tube defects. "
                     "Clinical protocols recommend preconception folate supplementation, but the form and dose "
                     "must be defined by the obstetrician based on your genotype.",
        "action": "Informar obstetra sobre genotipo MTHFR ANTES de planejar gravidez. O medico determinara o protocolo adequado de suplementacao.",
        "action_en": "Inform your obstetrician about your MTHFR genotype BEFORE planning pregnancy. The physician will determine the appropriate supplementation protocol.",
        "min_magnitude": 2,
    },
    "F5": {
        "risk_pt": "Trombofilia gestacional (trombose venosa, pre-eclampsia, aborto recorrente)",
        "risk_en": "Gestational thrombophilia (venous thrombosis, preeclampsia, recurrent miscarriage)",
        "detail": "Fator V Leiden aumenta risco de trombose. Na gravidez, o risco e ainda maior pela hipercoagulabilidade fisiologica. "
                  "A literatura descreve protocolos de anticoagulacao profilatica para portadoras, mas a decisao e exclusivamente medica.",
        "detail_en": "Factor V Leiden increases thrombosis risk. During pregnancy, the risk is even higher due to physiological hypercoagulability. "
                     "The literature describes prophylactic anticoagulation protocols for carriers, but the decision is strictly medical.",
        "action": "Consultar hematologista ANTES da concepcao. Informar obstetra sobre status de Fator V Leiden.",
        "action_en": "Consult a hematologist BEFORE conception. Inform your obstetrician about your Factor V Leiden status.",
        "min_magnitude": 2,
    },
    "F2": {
        "risk_pt": "Trombofilia gestacional (variante da protrombina G20210A)",
        "risk_en": "Gestational thrombophilia (prothrombin G20210A variant)",
        "detail": "Variante do gene da protrombina (F2) aumenta producao de trombina e risco de coagulos. "
                  "Combinado com F5 Leiden ou outros fatores, o risco e multiplicado.",
        "detail_en": "The prothrombin gene (F2) variant increases thrombin production and clotting risk. "
                     "Combined with F5 Leiden or other factors, the risk is multiplied.",
        "action": "Consultar hematologista para avaliacao pre-concepcional. Informar obstetra sobre esta variante.",
        "action_en": "Consult a hematologist for preconception evaluation. Inform your obstetrician about this variant.",
        "min_magnitude": 2,
    },
}

# ── X-linked conditions detectable on consumer chips ──────────────────────────

X_LINKED_CONDITIONS = {
    "G6PD": {
        "condition_pt": "Deficiencia de G6PD (favismo)",
        "condition_en": "G6PD Deficiency (favism)",
        "detail": "Condicao X-linked recessiva. Se a mae e portadora, cada filho homem tem 50% de chance de ser afetado. "
                  "Afetados devem evitar certos medicamentos (antimaláricos, sulfonamidas) e favas.",
        "detail_en": "X-linked recessive condition. If the mother is a carrier, each male child has a 50% chance of being affected. "
                     "Affected individuals must avoid certain medications (antimalarials, sulfonamides) and fava beans.",
        "severity": "moderada (controlavel com dieta/medicacao)",
        "severity_en": "moderate (manageable with diet/medication)",
        "prevalence": "~400 milhoes de pessoas no mundo. Mais comum em descendentes africanos, mediterraneos e asiaticos.",
        "prevalence_en": "~400 million people worldwide. More common in African, Mediterranean, and Asian descent.",
    },
    "OPN1LW": {
        "condition_pt": "Daltonismo (deficiencia vermelho-verde)",
        "condition_en": "Color Blindness (red-green deficiency)",
        "detail": "Condicao X-linked recessiva. Se a mae e portadora, cada filho homem tem 50% de chance. "
                  "Nao causa problemas de saude — impacto apenas visual. ~8% dos homens sao afetados.",
        "detail_en": "X-linked recessive condition. If the mother is a carrier, each male child has a 50% chance. "
                     "It does not cause health problems — visual impact only. ~8% of men are affected.",
        "severity": "leve (apenas visual)",
        "severity_en": "mild (visual only)",
        "prevalence": "~8% dos homens de ascendencia europeia",
        "prevalence_en": "~8% of men of European descent",
    },
    "DMD": {
        "condition_pt": "Distrofia Muscular de Duchenne/Becker",
        "condition_en": "Duchenne/Becker Muscular Dystrophy",
        "detail": "Condicao X-linked recessiva grave. Se a mae e portadora, cada filho homem tem 50% de chance. "
                  "Duchenne causa fraqueza muscular progressiva. Raramente detectada por chips de consumo (mutacoes grandes), "
                  "mas alguns SNPs proximos podem indicar risco.",
        "detail_en": "Severe X-linked recessive condition. If the mother is a carrier, each male child has a 50% chance. "
                     "Duchenne causes progressive muscle weakness. Rarely detected by consumer chips (large mutations), "
                     "but some nearby SNPs may indicate risk.",
        "severity": "grave",
        "severity_en": "severe",
        "prevalence": "~1:3.500 meninos nascidos",
        "prevalence_en": "~1:3,500 male births",
    },
}


# ── Localized message templates (summary/recommendations) ────────────────────

_MESSAGES = {
    "pt": {
        "carriers": (
            "Voce e portador(a) de {n} condicao(oes) recessiva(s): {details}. "
            "Se seu parceiro(a) tambem for portador da mesma condicao, ha 25% de chance de um filho ser afetado. "
            "Recomenda-se teste de portador no parceiro(a) antes da concepcao."
        ),
        "dominant": (
            "{n} variante(s) dominante(s) detectada(s): {details}. "
            "Cada filho tem 50% de chance de herdar. Acompanhamento medico dos filhos e recomendado."
        ),
        "risk_factors": (
            "{n} fator(es) de risco com implicacoes reprodutivas. "
            "Estes nao seguem heranca mendeliana classica mas podem influenciar a saude dos filhos."
        ),
        "gestational": (
            "**Riscos gestacionais identificados:** {details}. "
            "Acompanhamento pre-natal especializado e essencial."
        ),
        "x_linked": (
            "**Condicoes ligadas ao X:** {details}. "
            "Estas condicoes afetam predominantemente filhos HOMENS (50% de chance se a mae e portadora). "
            "Filhas geralmente sao portadoras sem sintomas."
        ),
        "none": (
            "Nenhuma variante com implicacao reprodutiva significativa detectada nos dados disponiveis. "
            "Lembre-se que este painel cobre apenas SNPs selecionados — um teste de portador expandido "
            "cobre centenas de condicoes adicionais."
        ),
        "rec_counselor": "Consulte um conselheiro genetico antes de planejar gravidez para avaliacao completa.",
        "rec_partner_tests": "Testes recomendados para parceiro(a): {tests}.",
        "rec_dominant": "Filhos devem ser acompanhados por geneticista/especialista desde o nascimento.",
        "rec_x_linked": (
            "Condicoes X-linked: se voce e mulher e portadora, filhos homens tem 50% de chance de ser afetados. "
            "Discuta opcoes reprodutivas (PGD, diagnostico pre-natal) com conselheiro genetico."
        ),
        "rec_expanded": (
            "Considere teste de portador expandido (carrier screening) que cobre 200+ condicoes recessivas. "
            "Disponivel em laboratorios como Invitae, Myriad, ou laboratorios locais."
        ),
        "rec_directory": "Diretorio NSGC (conselheiros geneticos): https://findageneticcounselor.nsgc.org",
        "skip_partner_marker": "Nao",
    },
    "en": {
        "carriers": (
            "You are a carrier of {n} recessive condition(s): {details}. "
            "If your partner is also a carrier of the same condition, there is a 25% chance of an affected child. "
            "Carrier testing in the partner is recommended before conception."
        ),
        "dominant": (
            "{n} dominant variant(s) detected: {details}. "
            "Each child has a 50% chance of inheriting. Medical follow-up of children is recommended."
        ),
        "risk_factors": (
            "{n} risk factor(s) with reproductive implications. "
            "These do not follow classical Mendelian inheritance but may influence children's health."
        ),
        "gestational": (
            "**Gestational risks identified:** {details}. "
            "Specialized prenatal follow-up is essential."
        ),
        "x_linked": (
            "**X-linked conditions:** {details}. "
            "These conditions predominantly affect MALE children (50% chance if the mother is a carrier). "
            "Daughters are usually asymptomatic carriers."
        ),
        "none": (
            "No variant with significant reproductive implications was detected in the available data. "
            "Keep in mind this panel covers only selected SNPs — an expanded carrier screen "
            "covers hundreds of additional conditions."
        ),
        "rec_counselor": "Consult a genetic counselor before planning pregnancy for a full evaluation.",
        "rec_partner_tests": "Recommended tests for the partner: {tests}.",
        "rec_dominant": "Children should be followed by a geneticist/specialist from birth.",
        "rec_x_linked": (
            "X-linked conditions: if you are a female carrier, male children have a 50% chance of being affected. "
            "Discuss reproductive options (PGD, prenatal diagnosis) with a genetic counselor."
        ),
        "rec_expanded": (
            "Consider expanded carrier screening covering 200+ recessive conditions. "
            "Available from labs such as Invitae, Myriad, or local laboratories."
        ),
        "rec_directory": "NSGC directory (genetic counselors): https://findageneticcounselor.nsgc.org",
        "skip_partner_marker": "Not required",
    },
}


def _t(item: dict, key: str, lang: Lang) -> str:
    """Return EN field if lang=='en' and present, else PT field.

    For keys ending in `_pt` (e.g. `condition_pt`), the EN counterpart is the
    base name + `_en` (e.g. `condition_en`). For other keys (e.g. `action`,
    `detail`), the EN counterpart is `<key>_en`.
    """
    if lang == "en":
        if key.endswith("_pt"):
            en_key = key[:-3] + "_en"
        else:
            en_key = f"{key}_en"
        en_val = item.get(en_key)
        if en_val:
            return en_val
    return item.get(key, "")


def analyze_family_planning(disease_findings: dict, health_results: dict, lang: Lang = "en") -> dict:
    """Analyze genetic data for family planning implications.

    Args:
        disease_findings: pathogenic/likely_pathogenic/risk_factor variant dicts.
        health_results: findings + apoe dicts from health analysis.
        lang: "en" (default) or "pt" — selects output language for summary
              strings. All raw entries keep both PT and EN fields.

    Returns dict with carrier_findings, dominant_findings, risk_factor_findings,
    gestational_risks, x_linked_findings, summary, conclusions, recommendations.
    """
    msgs = _MESSAGES.get(lang, _MESSAGES["en"])

    carrier_findings = []
    dominant_findings = []
    risk_factor_findings = []
    seen_genes = set()

    def _build_ctx_entry(gene: str, ctx: dict, extra: dict) -> dict:
        return {
            "gene": gene,
            "condition_pt": ctx["condition_pt"],
            "condition_en": ctx.get("condition_en", ctx["condition_pt"]),
            "inheritance": ctx["inheritance"],
            "inheritance_en": ctx.get("inheritance_en", ctx["inheritance"]),
            "carrier_risk": ctx["carrier_risk"],
            "carrier_risk_en": ctx.get("carrier_risk_en", ctx["carrier_risk"]),
            "partner_test": ctx["partner_test"],
            "partner_test_en": ctx.get("partner_test_en", ctx["partner_test"]),
            "severity": ctx["severity"],
            "severity_en": ctx.get("severity_en", ctx["severity"]),
            "prevalence": ctx.get("prevalence", ""),
            "prevalence_en": ctx.get("prevalence_en", ctx.get("prevalence", "")),
            **extra,
        }

    if disease_findings:
        all_patho = disease_findings.get("pathogenic", []) + disease_findings.get("likely_pathogenic", [])

        for f in all_patho:
            gene = f.get("gene", "")
            if not gene or gene in seen_genes:
                continue

            ctx = REPRODUCTIVE_CONTEXT.get(gene)
            if not ctx:
                continue

            seen_genes.add(gene)
            stars = f.get("gold_stars", 0)

            entry = _build_ctx_entry(gene, ctx, {
                "gold_stars": stars,
                "genotype": f.get("user_genotype", "?"),
                "rsid": f.get("rsid", ""),
            })

            if gene in RECESSIVE_CONDITIONS:
                carrier_findings.append(entry)
            elif gene in DOMINANT_CONDITIONS:
                dominant_findings.append(entry)
            else:
                risk_factor_findings.append(entry)

    # ── Gestational risks from lifestyle findings ──
    gestational_risks = []
    findings_dict = {}
    for f in health_results.get("findings", []):
        gene = f["gene"]
        if gene not in findings_dict or f["magnitude"] > findings_dict[gene]["magnitude"]:
            findings_dict[gene] = f
    for gene, info in GESTATIONAL_RISKS.items():
        if gene in findings_dict and findings_dict[gene]["magnitude"] >= info["min_magnitude"]:
            gestational_risks.append({
                "gene": gene,
                "risk_pt": info["risk_pt"],
                "risk_en": info.get("risk_en", info["risk_pt"]),
                "detail": info["detail"],
                "detail_en": info.get("detail_en", info["detail"]),
                "action": info["action"],
                "action_en": info.get("action_en", info["action"]),
                "genotype": findings_dict[gene].get("genotype", "?"),
                "rsid": findings_dict[gene].get("rsid", ""),
            })

    # ── X-linked carrier check ──
    x_linked_findings = []
    if disease_findings:
        all_variants = (
            disease_findings.get("pathogenic", [])
            + disease_findings.get("likely_pathogenic", [])
            + disease_findings.get("risk_factor", [])
        )
        for f in all_variants:
            gene = f.get("gene", "")
            if gene in X_LINKED_CONDITIONS and gene not in seen_genes:
                xinfo = X_LINKED_CONDITIONS[gene]
                x_linked_findings.append({
                    "gene": gene,
                    "condition_pt": xinfo["condition_pt"],
                    "condition_en": xinfo.get("condition_en", xinfo["condition_pt"]),
                    "detail": xinfo["detail"],
                    "detail_en": xinfo.get("detail_en", xinfo["detail"]),
                    "severity": xinfo["severity"],
                    "severity_en": xinfo.get("severity_en", xinfo["severity"]),
                    "prevalence": xinfo["prevalence"],
                    "prevalence_en": xinfo.get("prevalence_en", xinfo["prevalence"]),
                    "rsid": f.get("rsid", ""),
                    "genotype": f.get("user_genotype", "?"),
                })
                seen_genes.add(gene)

    # Check APOE from health results
    apoe = health_results.get("apoe")
    if apoe and apoe["magnitude"] >= 3 and "APOE" not in seen_genes:
        ctx = REPRODUCTIVE_CONTEXT["APOE"]
        risk_factor_findings.append(_build_ctx_entry("APOE", ctx, {
            "gold_stars": 0,
            "genotype": f"rs429358={apoe['rs429358']}",
            "rsid": "rs429358+rs7412",
            "apoe_isoform": apoe["isoform"],
        }))

    # Summary
    summary = {
        "total_relevant": len(carrier_findings) + len(dominant_findings) + len(risk_factor_findings) + len(gestational_risks) + len(x_linked_findings),
        "carriers": len(carrier_findings),
        "dominant": len(dominant_findings),
        "risk_factors": len(risk_factor_findings),
        "gestational": len(gestational_risks),
        "x_linked": len(x_linked_findings),
    }

    # Conclusions
    conclusions = []
    if carrier_findings:
        details = ", ".join(f"{f['gene']} ({_t(f, 'condition_pt', lang)})" for f in carrier_findings)
        conclusions.append(msgs["carriers"].format(n=len(carrier_findings), details=details))
    if dominant_findings:
        details = ", ".join(f"{f['gene']} ({_t(f, 'condition_pt', lang)})" for f in dominant_findings)
        conclusions.append(msgs["dominant"].format(n=len(dominant_findings), details=details))
    if risk_factor_findings:
        conclusions.append(msgs["risk_factors"].format(n=len(risk_factor_findings)))
    if gestational_risks:
        details = ", ".join(f"{f['gene']} ({_t(f, 'risk_pt', lang)})" for f in gestational_risks)
        conclusions.append(msgs["gestational"].format(details=details))
    if x_linked_findings:
        details = ", ".join(f"{f['gene']} ({_t(f, 'condition_pt', lang)})" for f in x_linked_findings)
        conclusions.append(msgs["x_linked"].format(details=details))
    if not conclusions:
        conclusions.append(msgs["none"])

    # Recommendations
    recommendations = []
    recommendations.append(msgs["rec_counselor"])
    if gestational_risks:
        for gr in gestational_risks:
            recommendations.append(f"**{gr['gene']}**: {_t(gr, 'action', lang)}")
    if carrier_findings:
        # Filter out "not required" partner tests (language-aware)
        tests = []
        for f in carrier_findings:
            pt_test = _t(f, "partner_test", lang)
            # Skip entries that explicitly say "not required" in either language
            if pt_test and "Nao" not in pt_test and "Not required" not in pt_test:
                tests.append(pt_test)
        if tests:
            recommendations.append(msgs["rec_partner_tests"].format(tests="; ".join(tests)))
    if dominant_findings:
        recommendations.append(msgs["rec_dominant"])
    if x_linked_findings:
        recommendations.append(msgs["rec_x_linked"])
    recommendations.append(msgs["rec_expanded"])
    recommendations.append(msgs["rec_directory"])

    return {
        "carrier_findings": carrier_findings,
        "dominant_findings": dominant_findings,
        "risk_factor_findings": risk_factor_findings,
        "gestational_risks": gestational_risks,
        "x_linked_findings": x_linked_findings,
        "summary": summary,
        "conclusions": conclusions,
        "recommendations": recommendations,
    }
