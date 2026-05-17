"""
Modulo de planejamento familiar — analisa status de portador e
implicacoes reprodutivas para quem deseja ter filhos.

Foca em:
1. Condicoes recessivas onde o usuario e portador
2. Condicoes dominantes que podem ser transmitidas
3. Recomendacoes de testes para o/a parceiro(a)
4. Quando procurar aconselhamento genetico
"""

# Contexto reprodutivo por gene
REPRODUCTIVE_CONTEXT = {
    "CC2D2A": {
        "condition_pt": "Sindrome COACH / Sindrome de Joubert tipo 9",
        "inheritance": "Autossomica recessiva",
        "carrier_risk": "Se o parceiro(a) tambem for portador: 25% de chance de filho afetado. Sindrome de Joubert causa malformacao cerebelar, atraso de desenvolvimento e problemas renais/hepaticos.",
        "partner_test": "Teste de portador para CC2D2A (painel de ciliopatias)",
        "severity": "grave",
        "prevalence": "Rara (~1:80.000-100.000)",
    },
    "KCNQ1": {
        "condition_pt": "Sindrome do QT Longo tipo 1",
        "inheritance": "Autossomica dominante (mas com penetrancia variavel)",
        "carrier_risk": "KCNQ1 pode ser dominante — cada filho tem 50% de chance de herdar a variante. Nem todos que herdam desenvolvem arritmia, mas devem ser monitorados com ECG.",
        "partner_test": "Nao e necessario teste no parceiro (dominante). Filhos devem fazer ECG.",
        "severity": "moderada-grave (tratavel)",
        "prevalence": "~1:2.000-5.000",
    },
    "GATA4": {
        "condition_pt": "Doenca Cardiaca Congenita",
        "inheritance": "Autossomica dominante (penetrancia variavel)",
        "carrier_risk": "50% de chance de transmissao. Nem todos que herdam desenvolvem defeito cardiaco. Ecocardiograma fetal recomendado durante a gravidez.",
        "partner_test": "Nao necessario. Acompanhamento pre-natal com ecocardiograma fetal.",
        "severity": "variavel (leve a grave)",
        "prevalence": "Defeitos cardiacos congenitos: ~1:100",
    },
    "NOD2": {
        "condition_pt": "Suscetibilidade a Doenca de Crohn / Sindrome de Blau",
        "inheritance": "Complexa (fator de risco, nao mendeliana simples)",
        "carrier_risk": "Cada alelo NOD2 variante aumenta o risco de Crohn em 2-4x, mas nao e determinista. Filhos podem herdar o alelo mas isso nao garante doenca.",
        "partner_test": "Nao necessario — nao e condicao mendeliana classica.",
        "severity": "moderada (cronica, tratavel)",
        "prevalence": "Crohn: ~1:1.000",
    },
    "VCL": {
        "condition_pt": "Cardiomiopatia Dilatada",
        "inheritance": "Autossomica dominante",
        "carrier_risk": "50% de chance de transmissao. Cardiomiopatia pode se manifestar na idade adulta. Filhos devem fazer ecocardiograma periodico.",
        "partner_test": "Nao necessario (dominante). Monitoramento cardiaco dos filhos.",
        "severity": "moderada-grave",
        "prevalence": "~1:2.500",
    },
    "PRLR": {
        "condition_pt": "Multiplos Fibroadenomas Mamarios",
        "inheritance": "Autossomica dominante",
        "carrier_risk": "50% de chance de transmissao. Fibroadenomas sao benignos mas requerem acompanhamento. Mais relevante para filhas.",
        "partner_test": "Nao necessario.",
        "severity": "leve (benigno)",
        "prevalence": "Relativamente comum",
    },
    "CCDC170": {
        "condition_pt": "Suscetibilidade a Cancer de Mama",
        "inheritance": "Complexa (fator de risco)",
        "carrier_risk": "Aumenta suscetibilidade a cancer de mama. Nao e determinista. Historico familiar e mais informativo que um unico SNP.",
        "partner_test": "Nao necessario para este gene especificamente.",
        "severity": "variavel",
        "prevalence": "Cancer de mama: ~1:8 mulheres",
    },
    "ACKR1": {
        "condition_pt": "Sistema Sanguineo Duffy / Neutropenia Etnica Benigna",
        "inheritance": "Codominante",
        "carrier_risk": "Relevante para ascendencia africana. Fenotipo Duffy-negativo confere resistencia a malaria vivax. Pode causar neutropenia benigna (contagem baixa de leucocitos sem significado clinico). Informar pediatra.",
        "partner_test": "Nao necessario.",
        "severity": "benigno",
        "prevalence": "Comum em populacoes de ascendencia africana",
    },
    "MSH6": {
        "condition_pt": "Sindrome de Lynch (Cancer Hereditario)",
        "inheritance": "Autossomica dominante",
        "carrier_risk": "50% de chance de transmissao. Filhos que herdam devem iniciar colonoscopia aos 25-30 anos. Cancer colorretal e o principal risco.",
        "partner_test": "Nao necessario (dominante). Filhos devem fazer teste genetico na idade adulta.",
        "severity": "grave (prevenivel com rastreamento)",
        "prevalence": "Lynch: ~1:300",
    },
    "APOE": {
        "condition_pt": "Risco de Alzheimer (APOE e4)",
        "inheritance": "Codominante / Fator de risco",
        "carrier_risk": "Cada filho tem 50% de chance de herdar o alelo e4. Ter um alelo e4 aumenta risco de Alzheimer tardio ~3x, mas NAO e determinista. Nao ha intervencao especifica para criancas — foco em estilo de vida saudavel ao longo da vida.",
        "partner_test": "Opcional. Se parceiro tambem tem e4, filhos podem herdar e4/e4 (risco ~12x).",
        "severity": "variavel (fator de risco, nao determinista)",
        "prevalence": "APOE e4: ~14% da populacao",
    },
    # Generic fallback for HFE
    "HFE": {
        "condition_pt": "Hemocromatose Hereditaria",
        "inheritance": "Autossomica recessiva",
        "carrier_risk": "Se parceiro tambem for portador: 25% de chance de filho com hemocromatose. Hemocromatose e tratavel com flebotomia regular.",
        "partner_test": "Teste de HFE (C282Y e H63D) no parceiro.",
        "severity": "moderada (tratavel)",
        "prevalence": "Portadores: ~1:10 em europeus",
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
        "detail": "Variante MTHFR reduz a conversao de acido folico em sua forma ativa (metilfolato). "
                  "A literatura associa esta variante a risco aumentado de defeitos do tubo neural. "
                  "Protocolos clinicos recomendam suplementacao pre-concepcional de folato, mas a forma e dose "
                  "devem ser definidas pelo obstetra com base no seu genotipo.",
        "action": "Informar obstetra sobre genotipo MTHFR ANTES de planejar gravidez. O medico determinara o protocolo adequado de suplementacao.",
        "min_magnitude": 2,
    },
    "F5": {
        "risk_pt": "Trombofilia gestacional (trombose venosa, pre-eclampsia, aborto recorrente)",
        "detail": "Fator V Leiden aumenta risco de trombose. Na gravidez, o risco e ainda maior pela hipercoagulabilidade fisiologica. "
                  "A literatura descreve protocolos de anticoagulacao profilatica para portadoras, mas a decisao e exclusivamente medica.",
        "action": "Consultar hematologista ANTES da concepcao. Informar obstetra sobre status de Fator V Leiden.",
        "min_magnitude": 2,
    },
    "F2": {
        "risk_pt": "Trombofilia gestacional (variante da protrombina G20210A)",
        "detail": "Variante do gene da protrombina (F2) aumenta producao de trombina e risco de coagulos. "
                  "Combinado com F5 Leiden ou outros fatores, o risco e multiplicado.",
        "action": "Consultar hematologista para avaliacao pre-concepcional. Informar obstetra sobre esta variante.",
        "min_magnitude": 2,
    },
}

# ── X-linked conditions detectable on consumer chips ──────────────────────────

X_LINKED_CONDITIONS = {
    "G6PD": {
        "condition_pt": "Deficiencia de G6PD (favismo)",
        "detail": "Condicao X-linked recessiva. Se a mae e portadora, cada filho homem tem 50% de chance de ser afetado. "
                  "Afetados devem evitar certos medicamentos (antimaláricos, sulfonamidas) e favas.",
        "severity": "moderada (controlavel com dieta/medicacao)",
        "prevalence": "~400 milhoes de pessoas no mundo. Mais comum em descendentes africanos, mediterraneos e asiaticos.",
    },
    "OPN1LW": {
        "condition_pt": "Daltonismo (deficiencia vermelho-verde)",
        "detail": "Condicao X-linked recessiva. Se a mae e portadora, cada filho homem tem 50% de chance. "
                  "Nao causa problemas de saude — impacto apenas visual. ~8% dos homens sao afetados.",
        "severity": "leve (apenas visual)",
        "prevalence": "~8% dos homens de ascendencia europeia",
    },
    "DMD": {
        "condition_pt": "Distrofia Muscular de Duchenne/Becker",
        "detail": "Condicao X-linked recessiva grave. Se a mae e portadora, cada filho homem tem 50% de chance. "
                  "Duchenne causa fraqueza muscular progressiva. Raramente detectada por chips de consumo (mutacoes grandes), "
                  "mas alguns SNPs proximos podem indicar risco.",
        "severity": "grave",
        "prevalence": "~1:3.500 meninos nascidos",
    },
}


def analyze_family_planning(disease_findings: dict, health_results: dict) -> dict:
    """Analyze genetic data for family planning implications.

    Returns {
        "carrier_findings": [{gene, condition, inheritance, risk, partner_test, severity}, ...],
        "dominant_findings": [{...}, ...],
        "risk_factor_findings": [{...}, ...],
        "summary": {total_relevant, carriers, dominant, risk_factors},
        "conclusions": [str, ...],
        "recommendations": [str, ...],
    }
    """
    carrier_findings = []
    dominant_findings = []
    risk_factor_findings = []
    seen_genes = set()

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

            entry = {
                "gene": gene,
                "condition_pt": ctx["condition_pt"],
                "inheritance": ctx["inheritance"],
                "carrier_risk": ctx["carrier_risk"],
                "partner_test": ctx["partner_test"],
                "severity": ctx["severity"],
                "prevalence": ctx.get("prevalence", ""),
                "gold_stars": stars,
                "genotype": f.get("user_genotype", "?"),
                "rsid": f.get("rsid", ""),
            }

            if gene in RECESSIVE_CONDITIONS:
                carrier_findings.append(entry)
            elif gene in DOMINANT_CONDITIONS:
                dominant_findings.append(entry)
            else:
                risk_factor_findings.append(entry)

    # ── Gestational risks from lifestyle findings ──
    gestational_risks = []
    # Build dict keeping highest magnitude per gene
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
                "detail": info["detail"],
                "action": info["action"],
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
            chrom = str(f.get("chrom", ""))
            if gene in X_LINKED_CONDITIONS and gene not in seen_genes:
                xinfo = X_LINKED_CONDITIONS[gene]
                x_linked_findings.append({
                    "gene": gene,
                    "condition_pt": xinfo["condition_pt"],
                    "detail": xinfo["detail"],
                    "severity": xinfo["severity"],
                    "prevalence": xinfo["prevalence"],
                    "rsid": f.get("rsid", ""),
                    "genotype": f.get("user_genotype", "?"),
                })
                seen_genes.add(gene)

    # Check APOE from health results
    apoe = health_results.get("apoe")
    if apoe and apoe["magnitude"] >= 3 and "APOE" not in seen_genes:
        ctx = REPRODUCTIVE_CONTEXT["APOE"]
        risk_factor_findings.append({
            "gene": "APOE",
            "condition_pt": ctx["condition_pt"],
            "inheritance": ctx["inheritance"],
            "carrier_risk": ctx["carrier_risk"],
            "partner_test": ctx["partner_test"],
            "severity": ctx["severity"],
            "prevalence": ctx.get("prevalence", ""),
            "gold_stars": 0,
            "genotype": f"rs429358={apoe['rs429358']}",
            "rsid": "rs429358+rs7412",
            "apoe_isoform": apoe["isoform"],
        })

    # Summary
    summary = {
        "total_relevant": len(carrier_findings) + len(dominant_findings) + len(risk_factor_findings) + len(gestational_risks) + len(x_linked_findings),
        "carriers": len(carrier_findings),
        "dominant": len(dominant_findings),
        "risk_factors": len(risk_factor_findings),
        "gestational": len(gestational_risks),
        "x_linked": len(x_linked_findings),
    }

    # Conclusions (bilingual)
    conclusions = []
    if carrier_findings:
        details = ", ".join(f"{f['gene']} ({f['condition_pt']})" for f in carrier_findings)
        conclusions.append(
            f"Voce e portador(a) de {len(carrier_findings)} condicao(oes) recessiva(s): {details}. "
            f"Se seu parceiro(a) tambem for portador da mesma condicao, ha 25% de chance de um filho ser afetado. "
            f"Recomenda-se teste de portador no parceiro(a) antes da concepcao."
        )
    if dominant_findings:
        details = ", ".join(f"{f['gene']} ({f['condition_pt']})" for f in dominant_findings)
        conclusions.append(
            f"{len(dominant_findings)} variante(s) dominante(s) detectada(s): {details}. "
            f"Cada filho tem 50% de chance de herdar. Acompanhamento medico dos filhos e recomendado."
        )
    if risk_factor_findings:
        conclusions.append(
            f"{len(risk_factor_findings)} fator(es) de risco com implicacoes reprodutivas. "
            f"Estes nao seguem heranca mendeliana classica mas podem influenciar a saude dos filhos."
        )
    if gestational_risks:
        details = ", ".join(f"{f['gene']} ({f['risk_pt']})" for f in gestational_risks)
        conclusions.append(
            f"**Riscos gestacionais identificados:** {details}. "
            f"Acompanhamento pre-natal especializado e essencial."
        )
    if x_linked_findings:
        details = ", ".join(f"{f['gene']} ({f['condition_pt']})" for f in x_linked_findings)
        conclusions.append(
            f"**Condicoes ligadas ao X:** {details}. "
            f"Estas condicoes afetam predominantemente filhos HOMENS (50% de chance se a mae e portadora). "
            f"Filhas geralmente sao portadoras sem sintomas."
        )
    if not conclusions:
        conclusions.append(
            "Nenhuma variante com implicacao reprodutiva significativa detectada nos dados disponiveis. "
            "Lembre-se que este painel cobre apenas SNPs selecionados — um teste de portador expandido "
            "cobre centenas de condicoes adicionais."
        )

    # Recommendations
    recommendations = []
    recommendations.append("Consulte um conselheiro genetico antes de planejar gravidez para avaliacao completa.")
    if gestational_risks:
        for gr in gestational_risks:
            recommendations.append(f"**{gr['gene']}**: {gr['action']}")
    if carrier_findings:
        tests = [f["partner_test"] for f in carrier_findings if "Nao" not in f["partner_test"]]
        if tests:
            recommendations.append(f"Testes recomendados para parceiro(a): {'; '.join(tests)}.")
    if dominant_findings:
        recommendations.append("Filhos devem ser acompanhados por geneticista/especialista desde o nascimento.")
    if x_linked_findings:
        recommendations.append(
            "Condicoes X-linked: se voce e mulher e portadora, filhos homens tem 50% de chance de ser afetados. "
            "Discuta opcoes reprodutivas (PGD, diagnostico pre-natal) com conselheiro genetico."
        )
    recommendations.append(
        "Considere teste de portador expandido (carrier screening) que cobre 200+ condicoes recessivas. "
        "Disponivel em laboratorios como Invitae, Myriad, ou laboratorios locais."
    )
    recommendations.append("Diretorio NSGC (conselheiros geneticos): https://findageneticcounselor.nsgc.org")

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
