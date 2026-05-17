"""
Paineis de bem-estar — Nutri, Fit, Skin, Aging.

Cada painel mapeia SNPs especificos para interpretacoes e recomendacoes
organizadas por categoria, com scores e conclusoes.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# NUTRI — Nutricao e Metabolismo
# ═══════════════════════════════════════════════════════════════════════════════

NUTRI_SNPS = {
    "rs1801133": {
        "gene": "MTHFR", "trait": "Metabolismo do Folato",
        "variants": {
            "GG": {"score": "normal", "text": "Conversao normal de acido folico em metilfolato. Suplementacao padrao de acido folico e eficaz."},
            "AG": {"score": "atencao", "text": "Reducao de ~35% na conversao de acido folico. Prefira metilfolato (L-5-MTHF) a acido folico sintetico."},
            "GA": {"score": "atencao", "text": "Reducao de ~35% na conversao de acido folico. Prefira metilfolato (L-5-MTHF)."},
            "AA": {"score": "alerta", "text": "Reducao de ~70% na atividade MTHFR. Use metilfolato em vez de acido folico. Monitore homocisteina."},
        },
    },
    "rs4988235": {
        "gene": "MCM6/LCT", "trait": "Tolerancia a Lactose",
        "variants": {
            "TT": {"score": "normal", "text": "Persistencia da lactase — voce tolera lactose normalmente ao longo da vida."},
            "TC": {"score": "normal", "text": "Uma copia de persistencia — provavelmente tolerante a lactose."},
            "CT": {"score": "normal", "text": "Uma copia de persistencia — provavelmente tolerante a lactose."},
            "CC": {"score": "alerta", "text": "Intolerancia a lactose genetica. Laticinios fermentados (iogurte, queijos curados) geralmente sao tolerados. Considere enzima lactase."},
        },
    },
    "rs174547": {
        "gene": "FADS1", "trait": "Conversao de Omega-3",
        "variants": {
            "TT": {"score": "normal", "text": "Boa conversao de ALA (linhaça, chia) em EPA/DHA. Fontes vegetais de omega-3 sao eficazes."},
            "TC": {"score": "atencao", "text": "Conversao moderada. Inclua peixes gordurosos ou suplemento de oleo de peixe/algas."},
            "CT": {"score": "atencao", "text": "Conversao moderada. Inclua peixes gordurosos ou suplemento de oleo de peixe/algas."},
            "CC": {"score": "alerta", "text": "Conversao pobre de ALA em EPA/DHA. Fontes vegetais insuficientes — use oleo de peixe ou algas (1-2g EPA+DHA/dia)."},
        },
    },
    "rs2282679": {
        "gene": "GC", "trait": "Vitamina D",
        "variants": {
            "GG": {"score": "normal", "text": "Niveis normais de proteina de ligacao de vitamina D. Exposicao solar e dieta geralmente suficientes."},
            "GT": {"score": "atencao", "text": "Tendencia a niveis mais baixos de vitamina D. Suplemente 2000-4000 UI/dia de D3."},
            "TG": {"score": "atencao", "text": "Tendencia a niveis mais baixos de vitamina D. Suplemente 2000-4000 UI/dia de D3."},
            "TT": {"score": "alerta", "text": "Predisposicao forte a deficiencia de vitamina D. Suplemente 4000-5000 UI/dia de D3. Teste 25-OH-D."},
        },
    },
    "rs5082": {
        "gene": "APOA2", "trait": "Sensibilidade a Gordura Saturada",
        "variants": {
            "GG": {"score": "normal", "text": "Resposta normal a gordura saturada. Dieta equilibrada e suficiente."},
            "GA": {"score": "normal", "text": "Sensibilidade moderada a gordura saturada."},
            "AG": {"score": "normal", "text": "Sensibilidade moderada a gordura saturada."},
            "AA": {"score": "alerta", "text": "Alta sensibilidade — gordura saturada se correlaciona mais fortemente com ganho de peso. Limite manteiga, carne gorda, coco. Prefira azeite, abacate, nozes."},
        },
    },
    "rs7903146": {
        "gene": "TCF7L2", "trait": "Risco de Diabetes Tipo 2",
        "variants": {
            "CC": {"score": "normal", "text": "Risco normal de diabetes tipo 2."},
            "CT": {"score": "atencao", "text": "Risco 1.4x aumentado. Monitore glicemia e HbA1c anualmente. Dieta baixa em acucar refinado."},
            "TC": {"score": "atencao", "text": "Risco 1.4x aumentado. Monitore glicemia e HbA1c anualmente."},
            "TT": {"score": "alerta", "text": "Risco 2x aumentado. HbA1c anual obrigatorio. Dieta low-glycemic, exercicio regular, controle de peso."},
        },
    },
    "rs11568820": {
        "gene": "BCMO1", "trait": "Conversao de Beta-caroteno em Vitamina A",
        "variants": {
            "GG": {"score": "normal", "text": "Boa conversao de beta-caroteno (cenoura, batata-doce) em vitamina A ativa."},
            "GA": {"score": "atencao", "text": "Conversao reduzida. Inclua fontes pre-formadas: ovos, figado, peixes."},
            "AG": {"score": "atencao", "text": "Conversao reduzida. Inclua fontes pre-formadas de vitamina A."},
            "AA": {"score": "alerta", "text": "Conversao pobre. Nao dependa apenas de vegetais para vitamina A — consuma ovos, figado, laticinios."},
        },
    },
    "rs762551": {
        "gene": "CYP1A2", "trait": "Metabolismo da Cafeina",
        "variants": {
            "AA": {"score": "normal", "text": "Metabolizador rapido de cafeina. Pode tolerar cafe sem aumento de risco cardiovascular."},
            "AC": {"score": "atencao", "text": "Metabolizador intermediario. Cafeina permanece ~5-6h. Limite ao periodo da manha."},
            "CA": {"score": "atencao", "text": "Metabolizador intermediario. Limite cafeina ao periodo da manha."},
            "CC": {"score": "alerta", "text": "Metabolizador lento. Cafeina permanece 8-12h. Risco cardiovascular aumentado com alto consumo. Maximo 1 xicara/dia, so de manha."},
        },
    },
    "rs1229984": {
        "gene": "ADH1B", "trait": "Metabolismo do Alcool",
        "variants": {
            "CC": {"score": "normal", "text": "Metabolismo lento de alcool — efeitos duram mais. Moderacao recomendada."},
            "CT": {"score": "normal", "text": "Metabolismo intermediario de alcool."},
            "TC": {"score": "normal", "text": "Metabolismo intermediario de alcool."},
            "TT": {"score": "atencao", "text": "Metabolismo rapido — converte alcool em acetaldeido rapidamente. Se combinado com ALDH2 lento, causa flush."},
        },
    },
    "rs671": {
        "gene": "ALDH2", "trait": "Tolerancia ao Alcool",
        "variants": {
            "GG": {"score": "normal", "text": "Depuracao normal de acetaldeido. Tolerancia padrao ao alcool."},
            "GA": {"score": "alerta", "text": "ALDH2 deficiente — acetaldeido acumula (flush, nausea). Risco aumentado de cancer esofagico com consumo regular de alcool."},
            "AG": {"score": "alerta", "text": "ALDH2 deficiente — risco aumentado de cancer esofagico com alcool. Minimize consumo."},
            "AA": {"score": "alerta", "text": "ALDH2 severamente deficiente. Alcool fortemente desaconselhado — risco significativo de cancer."},
        },
    },
    "rs1799945": {
        "gene": "HFE", "trait": "Absorcao de Ferro",
        "variants": {
            "CC": {"score": "normal", "text": "Absorcao normal de ferro."},
            "CG": {"score": "atencao", "text": "Portador HFE H63D — absorcao levemente aumentada. Monitore ferritina. Evite suplementos de ferro desnecessarios."},
            "GC": {"score": "atencao", "text": "Portador HFE H63D — monitore ferritina periodicamente."},
            "GG": {"score": "alerta", "text": "HFE H63D homozigoto — risco de acumulo de ferro. Monitore ferritina anualmente. Doe sangue se ferritina elevada."},
        },
    },
    "rs1800562": {
        "gene": "HFE", "trait": "Hemocromatose Hereditaria",
        "variants": {
            "GG": {"score": "normal", "text": "Sem variante C282Y. Absorcao de ferro normal."},
            "GA": {"score": "atencao", "text": "Portador HFE C282Y — risco de hemocromatose se combinado com H63D. Monitore ferritina."},
            "AG": {"score": "atencao", "text": "Portador HFE C282Y — monitore ferritina."},
            "AA": {"score": "alerta", "text": "HFE C282Y homozigoto — alto risco de hemocromatose. Flebotomia pode ser necessaria. Consulte hematologista."},
        },
    },
    "rs7946": {
        "gene": "PEMT", "trait": "Necessidade de Colina",
        "variants": {
            "CC": {"score": "normal", "text": "Producao endogena adequada de fosfatidilcolina."},
            "CT": {"score": "atencao", "text": "Producao reduzida. Aumente colina na dieta: ovos (2/dia = ~300mg), figado, peixe."},
            "TC": {"score": "atencao", "text": "Producao reduzida de colina. Aumente consumo de ovos e figado."},
            "TT": {"score": "alerta", "text": "Producao significativamente reduzida. Considere suplemento de colina (250-500mg CDP-colina ou fosfatidilcolina)."},
        },
    },
    "rs1802059": {
        "gene": "MTRR", "trait": "Reciclagem de Vitamina B12",
        "variants": {
            "GG": {"score": "normal", "text": "Reciclagem eficiente de B12 (metilcobalamina)."},
            "GA": {"score": "atencao", "text": "Reciclagem reduzida. Use metilcobalamina em vez de cianocobalamina."},
            "AG": {"score": "atencao", "text": "Reciclagem reduzida de B12."},
            "AA": {"score": "alerta", "text": "Reciclagem significativamente reduzida. Use metilcobalamina sublingual 1000-5000mcg. Teste B12 e acido metilmalonico."},
        },
    },
    "rs4880": {
        "gene": "SOD2", "trait": "Defesa Antioxidante",
        "variants": {
            "TT": {"score": "normal", "text": "Alta atividade SOD2 — defesa antioxidante mitocondrial eficiente."},
            "TC": {"score": "normal", "text": "Atividade intermediaria SOD2 — defesa adequada."},
            "CT": {"score": "normal", "text": "Atividade intermediaria SOD2."},
            "CC": {"score": "atencao", "text": "Atividade reduzida SOD2. Dieta rica em antioxidantes (frutas vermelhas, vegetais coloridos). Considere CoQ10."},
        },
    },
    "rs1800795": {
        "gene": "IL6", "trait": "Inflamacao Basal",
        "variants": {
            "CC": {"score": "normal", "text": "Niveis normais de IL-6."},
            "CG": {"score": "normal", "text": "Niveis intermediarios de IL-6."},
            "GC": {"score": "normal", "text": "Niveis intermediarios de IL-6."},
            "GG": {"score": "alerta", "text": "IL-6 basal elevada. Dieta anti-inflamatoria: omega-3, vegetais, curcuma. Sono adequado e essencial (privacao de sono eleva IL-6)."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# FIT — Aptidao Fisica
# ═══════════════════════════════════════════════════════════════════════════════

FIT_SNPS = {
    "rs1815739": {
        "gene": "ACTN3", "trait": "Tipo de Fibra Muscular",
        "variants": {
            "CC": {"score": "power", "text": "Alpha-actinina-3 presente — fibras rapidas. Vantagem em atividades explosivas: sprint, salto, musculacao pesada."},
            "CT": {"score": "misto", "text": "Perfil misto — versatil para potencia e resistencia. Responde bem a treinos variados."},
            "TC": {"score": "misto", "text": "Perfil misto — versatil para potencia e resistencia."},
            "TT": {"score": "endurance", "text": "Sem alpha-actinina-3 — favorece resistencia. Vantagem em corrida de longa distancia, ciclismo, natacao."},
        },
    },
    "rs8192678": {
        "gene": "PPARGC1A", "trait": "Biogenese Mitocondrial",
        "variants": {
            "CC": {"score": "normal", "text": "PGC-1alpha normal — boa capacidade de gerar novas mitocondrias com exercicio."},
            "CT": {"score": "atencao", "text": "PGC-1alpha reduzido. Exercicio aerobico e ainda mais importante para voce — estimula a biogenese mitocondrial."},
            "TC": {"score": "atencao", "text": "PGC-1alpha reduzido. Priorize treino aerobico."},
            "TT": {"score": "alerta", "text": "PGC-1alpha significativamente reduzido. Treino aerobico regular e essencial para manter saude mitocondrial. HIIT pode ser particularmente benefico."},
        },
    },
    "rs1042713": {
        "gene": "ADRB2", "trait": "Queima de Gordura no Exercicio",
        "variants": {
            "GG": {"score": "otimo", "text": "ADRB2 Gly16 — excelente mobilizacao de gordura durante exercicio. Cardio e HIIT sao particularmente eficazes para composicao corporal."},
            "GA": {"score": "normal", "text": "Mobilizacao moderada de gordura durante exercicio."},
            "AG": {"score": "normal", "text": "Mobilizacao moderada de gordura."},
            "AA": {"score": "normal", "text": "Mobilizacao padrao de gordura. Treino de resistencia pode complementar cardio para composicao corporal."},
        },
    },
    "rs6265": {
        "gene": "BDNF", "trait": "Neuroplasticidade e Exercicio",
        "variants": {
            "CC": {"score": "normal", "text": "BDNF Val66Val — producao normal de fator neurotrofico. Exercicio potencializa cognicao normalmente."},
            "CT": {"score": "atencao", "text": "BDNF Val66Met — producao reduzida. Exercicio e ESSENCIAL para compensar — e o melhor estimulador natural de BDNF."},
            "TC": {"score": "atencao", "text": "BDNF reduzido. Exercicio regular e crucial para neuroplasticidade."},
            "TT": {"score": "alerta", "text": "BDNF Met66Met — producao significativamente reduzida. Priorize exercicio diario, aprendizado continuo e interacao social. Exercicio aerobico 5x/semana."},
        },
    },
    "rs4680": {
        "gene": "COMT", "trait": "Recuperacao e Estresse",
        "variants": {
            "GG": {"score": "warrior", "text": "COMT rapido (Val/Val) — 'guerreiro'. Dopamina limpa rapido. Resiliencia ao estresse mas pode precisar de mais estimulo para foco. Suporta treinos de alta intensidade."},
            "GA": {"score": "misto", "text": "COMT intermediario — equilibrio entre foco e resiliencia. Bom perfil para treino variado."},
            "AG": {"score": "misto", "text": "COMT intermediario."},
            "AA": {"score": "worrier", "text": "COMT lento (Met/Met) — 'estrategista'. Alto foco basal mas sensivel a estresse. Overtraining mais provavel. Inclua yoga, meditacao, e periodize descanso."},
        },
    },
    "rs1799971": {
        "gene": "OPRM1", "trait": "Resposta a Dor e Endorfinas",
        "variants": {
            "AA": {"score": "normal", "text": "Receptor opioide normal. Resposta padrao a endorfinas do exercicio."},
            "AG": {"score": "atencao", "text": "Receptor opioide alterado. Pode precisar de mais exercicio para sentir o 'runner's high'. Informe anestesista antes de cirurgias."},
            "GA": {"score": "atencao", "text": "Receptor alterado. Dosagem de analgesicos pode precisar de ajuste."},
            "GG": {"score": "alerta", "text": "Receptor significativamente alterado. Informe todos os medicos sobre este genotipo antes de prescricao de analgesicos."},
        },
    },
    "rs5443": {
        "gene": "GNB3", "trait": "Tendencia a Ganho de Peso",
        "variants": {
            "CC": {"score": "normal", "text": "Sinalizacao G-protein normal. Peso responde de forma padrao a dieta e exercicio."},
            "CT": {"score": "atencao", "text": "GNB3 C825T — tendencia levemente aumentada a ganho de peso. Exercicio regular e particularmente importante."},
            "TC": {"score": "atencao", "text": "Tendencia levemente aumentada a ganho de peso."},
            "TT": {"score": "alerta", "text": "GNB3 C825T homozigoto — tendencia maior a ganho de peso e hipertensao. Exercicio aerobico regular e controle alimentar sao essenciais."},
        },
    },
    "rs699": {
        "gene": "AGT", "trait": "Pressao Arterial e Exercicio",
        "variants": {
            "CC": {"score": "normal", "text": "Niveis normais de angiotensinogeno."},
            "CT": {"score": "atencao", "text": "AGT M235T — leve tendencia a pressao elevada. Exercicio aerobico ajuda a regular."},
            "TC": {"score": "atencao", "text": "Leve tendencia a pressao elevada."},
            "TT": {"score": "alerta", "text": "AGT M235T homozigoto — risco aumentado de hipertensao. 150+ min/semana de exercicio aerobico. Monitore pressao."},
        },
    },
    "rs5186": {
        "gene": "AGTR1", "trait": "Receptor de Angiotensina e Exercicio",
        "variants": {
            "AA": {"score": "normal", "text": "Receptor AGTR1 normal."},
            "AC": {"score": "atencao", "text": "AGTR1 aumentado — maior risco de hipertensao. Exercicio aerobico e restricao de sodio beneficos."},
            "CA": {"score": "atencao", "text": "AGTR1 aumentado. Monitore pressao arterial."},
            "CC": {"score": "alerta", "text": "AGTR1 alto — monitoramento de pressao essencial. Exercicio aerobico regular como primeira linha de prevencao."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# SKIN — Pele e Dermatologia
# ═══════════════════════════════════════════════════════════════════════════════

SKIN_SNPS = {
    "rs2228479": {
        "gene": "MC1R", "trait": "Fotoenvelhecimento",
        "variants": {
            "GG": {"score": "normal", "text": "Producao normal de melanina. Envelhecimento cutaneo padrao com protecao solar adequada."},
            "GA": {"score": "atencao", "text": "MC1R V92M — envelhecimento cutaneo acelerado. Use protetor solar SPF 30+ diariamente. Considere retinoides topicos e serum de vitamina C."},
            "AG": {"score": "atencao", "text": "Envelhecimento cutaneo acelerado. SPF 30+ diario."},
            "AA": {"score": "alerta", "text": "MC1R homozigoto — fotoenvelhecimento significativo. SPF 50+ obrigatorio. Evite exposicao solar prolongada. Retinoides + antioxidantes topicos recomendados."},
        },
    },
    "rs1800795": {
        "gene": "IL6", "trait": "Inflamacao Cutanea",
        "variants": {
            "CC": {"score": "normal", "text": "Inflamacao cutanea basal normal."},
            "CG": {"score": "normal", "text": "Inflamacao moderada."},
            "GC": {"score": "normal", "text": "Inflamacao moderada."},
            "GG": {"score": "alerta", "text": "Tendencia a inflamacao cutanea elevada. Dieta anti-inflamatoria beneficia a pele. Omega-3 e acidos graxos essenciais ajudam. Evite alimentos ultraprocessados."},
        },
    },
    "rs4880": {
        "gene": "SOD2", "trait": "Protecao Antioxidante da Pele",
        "variants": {
            "TT": {"score": "normal", "text": "Alta protecao antioxidante — estresse oxidativo cutaneo bem gerenciado."},
            "TC": {"score": "normal", "text": "Protecao antioxidante adequada."},
            "CT": {"score": "normal", "text": "Protecao antioxidante adequada."},
            "CC": {"score": "atencao", "text": "Protecao antioxidante reduzida. Serum de vitamina C (L-ascorbico 10-20%) e vitamina E topicos compensam. Dieta rica em antioxidantes."},
        },
    },
    "rs2282679": {
        "gene": "GC", "trait": "Vitamina D e Saude da Pele",
        "variants": {
            "GG": {"score": "normal", "text": "Niveis adequados de vitamina D para saude da pele."},
            "GT": {"score": "atencao", "text": "Tendencia a vitamina D mais baixa — afeta renovacao celular da pele. Suplemente D3."},
            "TG": {"score": "atencao", "text": "Vitamina D mais baixa. Suplemente D3."},
            "TT": {"score": "alerta", "text": "Deficiencia provavel de vitamina D — impacta barreira cutanea e renovacao. Suplemente 4000-5000 UI D3/dia."},
        },
    },
    "rs1801133": {
        "gene": "MTHFR", "trait": "Colageno e Metilacao",
        "variants": {
            "GG": {"score": "normal", "text": "Metilacao normal — producao de colageno e renovacao celular adequadas."},
            "AG": {"score": "atencao", "text": "Metilacao reduzida pode afetar sintese de colageno a longo prazo. Metilfolato e B12 ajudam."},
            "GA": {"score": "atencao", "text": "Metilacao reduzida. Suporte com metilfolato."},
            "AA": {"score": "alerta", "text": "Metilacao significativamente reduzida — impacto potencial na producao de colageno e reparo de DNA cutaneo. Metilfolato + B12 + colina."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# AGING — Envelhecimento e Longevidade
# ═══════════════════════════════════════════════════════════════════════════════

AGING_SNPS = {
    # APOE: rs429358 alone only tells part of the story
    # Full isoform requires rs429358 + rs7412 (see analyzer.py determine_apoe)
    # Here we show rs429358 as a flag; the combined result appears in conclusions
    "rs429358": {
        "gene": "APOE (rs429358)", "trait": "Risco de Alzheimer (parcial — ver conclusoes para isoforma completa)",
        "variants": {
            "TT": {"score": "favoravel", "text": "Sem alelo APOE e4 (rs429358=TT). Risco basal. Ver rs7412 para isoforma completa (E2 ou E3)."},
            "TC": {"score": "alerta", "text": "APOE e4 heterozigoto (rs429358=TC). Se rs7412=CC -> E3/E4 (risco ~3x Alzheimer). Se rs7412=CT -> E2/E4 (riscos mistos). Ver conclusoes para resultado combinado."},
            "CT": {"score": "alerta", "text": "APOE e4 heterozigoto (rs429358=CT). Ver conclusoes para isoforma completa com rs7412."},
            "CC": {"score": "critico", "text": "APOE e4/e4 (rs429358=CC). Risco ~12-15x de Alzheimer. Prevencao agressiva: exercicio diario, dieta mediterranea, sono, controle cardiovascular. Consulte neurologista."},
        },
    },
    "rs5882": {
        "gene": "CETP", "trait": "Perfil Lipidico e Longevidade",
        "variants": {
            "GG": {"score": "normal", "text": "Transferencia normal de colesterol entre lipoproteinas."},
            "GA": {"score": "favoravel", "text": "CETP I405V — tendencia a HDL mais alto. Associado a longevidade excepcional em estudos. Fator protetor."},
            "AG": {"score": "favoravel", "text": "CETP I405V — perfil lipidico favoravel."},
            "AA": {"score": "favoravel", "text": "CETP I405V homozigoto — HDL elevado, forte associacao com longevidade. Continue mantendo estilo de vida saudavel."},
        },
    },
    "rs6265": {
        "gene": "BDNF", "trait": "Saude Cerebral no Envelhecimento",
        "variants": {
            "CC": {"score": "normal", "text": "BDNF normal — boa neuroplasticidade basal. Exercicio e aprendizado continuo mantem a saude cerebral."},
            "CT": {"score": "atencao", "text": "BDNF reduzido — mais vulneravel a declinio cognitivo com idade. Exercicio aerobico e o estimulador mais potente de BDNF."},
            "TC": {"score": "atencao", "text": "BDNF reduzido. Priorize exercicio e estimulacao cognitiva."},
            "TT": {"score": "alerta", "text": "BDNF significativamente reduzido. Exercicio diario, aprendizado de novas habilidades, socializacao ativa e sono de qualidade sao criticos para manter saude cognitiva."},
        },
    },
    "rs1800795": {
        "gene": "IL6", "trait": "Inflamacao Cronica e Envelhecimento",
        "variants": {
            "CC": {"score": "normal", "text": "IL-6 normal — envelhecimento inflamatorio (inflammaging) de progressao padrao."},
            "CG": {"score": "normal", "text": "IL-6 intermediaria."},
            "GC": {"score": "normal", "text": "IL-6 intermediaria."},
            "GG": {"score": "alerta", "text": "IL-6 elevada — 'inflammaging' acelerado. Anti-inflamatorios naturais: omega-3, curcuma, exercicio regular, sono adequado. Evite obesidade (tecido adiposo produz IL-6)."},
        },
    },
    "rs4880": {
        "gene": "SOD2", "trait": "Estresse Oxidativo e Envelhecimento",
        "variants": {
            "TT": {"score": "favoravel", "text": "SOD2 alta atividade — eficiente neutralizacao de radicais livres mitocondriais. Fator protetor contra envelhecimento."},
            "TC": {"score": "normal", "text": "SOD2 intermediaria — defesa adequada contra radicais livres."},
            "CT": {"score": "normal", "text": "SOD2 intermediaria."},
            "CC": {"score": "atencao", "text": "SOD2 reduzida — maior acumulo de dano oxidativo mitocondrial. CoQ10 (100-200mg/dia), dieta rica em antioxidantes e exercicio ajudam a compensar."},
        },
    },
    "rs2228479": {
        "gene": "MC1R", "trait": "Envelhecimento da Pele",
        "variants": {
            "GG": {"score": "normal", "text": "Envelhecimento cutaneo padrao."},
            "GA": {"score": "atencao", "text": "Envelhecimento cutaneo acelerado. SPF diario e retinoides topicos reduzem impacto."},
            "AG": {"score": "atencao", "text": "Envelhecimento cutaneo acelerado."},
            "AA": {"score": "alerta", "text": "Envelhecimento cutaneo significativamente acelerado. Protecao solar rigorosa + retinoides + antioxidantes topicos."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# SENSORY — Percepcao Sensorial
# ═══════════════════════════════════════════════════════════════════════════════

SENSORY_SNPS = {
    "rs713598": {
        "gene": "TAS2R38", "trait": "Sensibilidade ao Amargo",
        "variants": {
            "GG": {"score": "normal", "text": "Degustador medio — percebe amargor moderadamente. Brocolis, cafe e cerveja IPA tem sabor padrao."},
            "GC": {"score": "atencao", "text": "Super-degustador parcial — sensibilidade aumentada ao amargo. Pode rejeitar vegetais cruciferos (brocolis, couve) e cafe forte."},
            "CG": {"score": "atencao", "text": "Sensibilidade aumentada ao amargo. Tendencia a rejeitar brocolis e cafe forte."},
            "CC": {"score": "alerta", "text": "Super-degustador — amargor intenso. Brocolis, rucula, cafe preto e cerveja IPA podem ser intoleraveis. Cozinhar vegetais e adicionar gordura reduz o amargor."},
        },
    },
    "rs72921001": {
        "gene": "OR6A2", "trait": "Percepcao de Coentro",
        "variants": {
            "CC": {"score": "normal", "text": "Percepcao normal de coentro — sabor herbaceo agradavel para a maioria."},
            "CA": {"score": "atencao", "text": "Portador do alelo 'sabao' — pode perceber coentro como sabor de sabao ou metalico. Cerca de 14% da populacao tem essa variante."},
            "AC": {"score": "atencao", "text": "Pode perceber coentro como sabor de sabao."},
            "AA": {"score": "alerta", "text": "Forte percepcao de sabor de sabao no coentro. Substitua por salsa, cebolinha ou manjericao nas receitas."},
        },
    },
    "rs2274333": {
        "gene": "CA6", "trait": "Percepcao de Umami e Sabor",
        "variants": {
            "AA": {"score": "normal", "text": "Producao normal de gustina (proteina salivar). Percepcao padrao de sabores."},
            "AG": {"score": "atencao", "text": "Producao reduzida de gustina — sensibilidade a sabores pode ser menor. Pode preferir alimentos mais temperados."},
            "GA": {"score": "atencao", "text": "Sensibilidade reduzida a sabores."},
            "GG": {"score": "alerta", "text": "Producao significativamente reduzida de gustina. Pode precisar de mais tempero para perceber sabores. Tendencia a preferir alimentos mais salgados/condimentados."},
        },
    },
    "rs4481887": {
        "gene": "OR2M7", "trait": "Deteccao de Aspargo na Urina",
        "variants": {
            "GG": {"score": "normal", "text": "Consegue detectar o odor caracteristico do aspargo na urina. Cerca de 40% das pessoas nao conseguem."},
            "GA": {"score": "normal", "text": "Deteccao intermediaria do odor de aspargo."},
            "AG": {"score": "normal", "text": "Deteccao intermediaria do odor de aspargo."},
            "AA": {"score": "favoravel", "text": "Nao detecta o odor do aspargo na urina — anosmia especifica. Curiosidade genetica sem impacto clinico."},
        },
    },
    "rs10246939": {
        "gene": "TAS2R38", "trait": "Sensibilidade a Glucosinolatos",
        "variants": {
            "CC": {"score": "normal", "text": "Percepcao padrao de glucosinolatos (compostos amargos de brocolis, couve-de-bruxelas, repolho)."},
            "CT": {"score": "atencao", "text": "Sensibilidade aumentada a glucosinolatos. Pode evitar vegetais cruciferos, que sao ricos em compostos anti-cancer."},
            "TC": {"score": "atencao", "text": "Sensibilidade aumentada. Cozinhar reduz o amargor dos cruciferos."},
            "TT": {"score": "alerta", "text": "Alta sensibilidade. Tente preparar cruciferos assados com azeite e alho — o calor destroi parte dos glucosinolatos amargos enquanto mantem os beneficios."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# SLEEP — Sono e Cronobiologia
# ═══════════════════════════════════════════════════════════════════════════════

SLEEP_SNPS = {
    "rs1801260": {
        "gene": "CLOCK", "trait": "Cronotipo (Coruja vs Cotovia)",
        "variants": {
            "AA": {"score": "normal", "text": "Cronotipo padrao — nao fortemente matutino nem noturno. Rotina regular ajuda a manter ritmo saudavel."},
            "AG": {"score": "atencao", "text": "Tendencia noturna moderada (cronotipo 'coruja'). Pode ter dificuldade para dormir cedo. Exposicao a luz solar pela manha ajuda a recalibrar."},
            "GA": {"score": "atencao", "text": "Tendencia noturna moderada."},
            "GG": {"score": "alerta", "text": "Forte tendencia noturna — 'coruja' genetica. Dificuldade com horarios matutinos e provavel. Luz solar intensa pela manha (10-15min) e evitar telas a noite sao essenciais."},
        },
    },
    "rs2305160": {
        "gene": "PER2", "trait": "Fase Circadiana",
        "variants": {
            "CC": {"score": "normal", "text": "Ritmo circadiano de duracao padrao (~24h). Fase de sono regular."},
            "CT": {"score": "atencao", "text": "Fase circadiana levemente avancada — pode sentir sono mais cedo e acordar mais cedo naturalmente."},
            "TC": {"score": "atencao", "text": "Fase circadiana levemente avancada."},
            "TT": {"score": "atencao", "text": "Sindrome de fase avancada do sono — tendencia a dormir e acordar muito cedo. Se incomoda, luz brilhante no final da tarde pode atrasar o relogio biologico."},
        },
    },
    "rs57875989": {
        "gene": "ADRB1", "trait": "Necessidade de Sono (Dormidor Curto)",
        "variants": {
            "CC": {"score": "normal", "text": "Necessidade padrao de sono — 7-9 horas para funcionamento otimo."},
            "CT": {"score": "favoravel", "text": "Portador de variante de sono curto — pode funcionar bem com 6-6.5 horas de sono. Variante rara, identificada em familias de 'dormidores curtos naturais'."},
            "TC": {"score": "favoravel", "text": "Possivel dormidor curto natural."},
            "TT": {"score": "favoravel", "text": "Dormidor curto natural genetico — pode se sentir totalmente recuperado com ~6 horas. Extremamente raro."},
        },
    },
    "rs73598374": {
        "gene": "ADA", "trait": "Eficiencia do Sono Profundo",
        "variants": {
            "CC": {"score": "normal", "text": "Metabolismo normal de adenosina — acumulo de pressao de sono e qualidade de sono profundo padrao."},
            "CT": {"score": "favoravel", "text": "Metabolismo de adenosina alterado — pode ter sono profundo mais intenso e restorador. Tendencia a dormir mais profundamente."},
            "TC": {"score": "favoravel", "text": "Sono profundo potencialmente mais intenso."},
            "TT": {"score": "favoravel", "text": "Sono profundo muito intenso — metabolismo de adenosina significativamente alterado. Acordar pode ser mais dificil, mas o sono e mais restaurador."},
        },
    },
    "rs4753426": {
        "gene": "MTNR1B", "trait": "Sensibilidade a Melatonina",
        "variants": {
            "CC": {"score": "normal", "text": "Receptor de melatonina padrao. Ritmo circadiano responde normalmente a escuridao."},
            "CT": {"score": "atencao", "text": "Receptor de melatonina alterado — pode precisar de mais escuridao para iniciar o sono. Tambem associado a risco metabolico se comer muito tarde."},
            "TC": {"score": "atencao", "text": "Receptor de melatonina alterado. Evite comer 2-3h antes de dormir."},
            "TT": {"score": "alerta", "text": "Receptor de melatonina significativamente alterado. Blackout total no quarto, evitar telas 1h antes de dormir. Nao coma apos as 20h — risco metabolico aumentado."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# LONGEVITY — Longevidade
# ═══════════════════════════════════════════════════════════════════════════════

LONGEVITY_SNPS = {
    "rs2802292": {
        "gene": "FOXO3", "trait": "Gene da Longevidade",
        "variants": {
            "TT": {"score": "normal", "text": "Variante padrao de FOXO3. Longevidade depende principalmente de estilo de vida."},
            "TG": {"score": "favoravel", "text": "Portador do alelo de longevidade FOXO3 — associado a vida mais longa em multiplas populacoes (japoneses, alemaes, americanos). Fator protetor."},
            "GT": {"score": "favoravel", "text": "Portador de alelo FOXO3 de longevidade."},
            "GG": {"score": "otimo", "text": "Homozigoto para alelo de longevidade FOXO3 — forte associacao com vida centenaria em estudos globais. FOXO3 regula reparo de DNA, autofagia e resistencia ao estresse oxidativo."},
        },
    },
    "rs5882": {
        "gene": "CETP", "trait": "HDL e Longevidade Excepcional",
        "variants": {
            "GG": {"score": "normal", "text": "Transferencia de colesterol padrao entre lipoproteinas."},
            "GA": {"score": "favoravel", "text": "CETP I405V — tendencia a HDL mais alto. Associado a longevidade excepcional em estudos com centenarios Ashkenazi."},
            "AG": {"score": "favoravel", "text": "Perfil lipidico favoravel para longevidade."},
            "AA": {"score": "otimo", "text": "CETP I405V homozigoto — HDL consistentemente elevado. Forte associacao com longevidade excepcional e protecao cardiovascular."},
        },
    },
    "rs1042522": {
        "gene": "TP53", "trait": "Eficiencia de Reparo de DNA",
        "variants": {
            "GG": {"score": "normal", "text": "p53 Pro72 — apoptose ligeiramente mais lenta, mas melhor reparo de DNA. Levemente associado a maior longevidade."},
            "GC": {"score": "normal", "text": "p53 heterozigoto — equilibrio entre eficiencia de reparo e resposta a dano."},
            "CG": {"score": "normal", "text": "Equilibrio entre apoptose e reparo."},
            "CC": {"score": "normal", "text": "p53 Arg72 — apoptose mais eficiente (elimina celulas danificadas mais rapido). Melhor resposta a quimioterapia se necessaria."},
        },
    },
    "rs4420638": {
        "gene": "APOC1/APOE", "trait": "Cluster de Longevidade APOE",
        "variants": {
            "AA": {"score": "favoravel", "text": "Variante protetora no cluster APOE — associada a menor risco de Alzheimer e maior longevidade."},
            "AG": {"score": "normal", "text": "Perfil intermediario no cluster de longevidade APOE."},
            "GA": {"score": "normal", "text": "Perfil intermediario."},
            "GG": {"score": "atencao", "text": "Variante de risco no cluster APOE. Exercicio regular, dieta mediterranea e controle cardiovascular sao especialmente importantes para voce."},
        },
    },
    "rs2069837": {
        "gene": "IL6", "trait": "Inflamacao e Envelhecimento Saudavel",
        "variants": {
            "AA": {"score": "normal", "text": "Nivel padrao de IL-6. 'Inflammaging' de progressao normal."},
            "AG": {"score": "favoravel", "text": "Producao reduzida de IL-6 — menor inflammaging. Fator positivo para envelhecimento saudavel."},
            "GA": {"score": "favoravel", "text": "Menor inflamacao cronica — favorece longevidade."},
            "GG": {"score": "otimo", "text": "IL-6 significativamente reduzida. Excelente perfil anti-inflamatorio para envelhecimento saudavel."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# MENTAL — Saude Mental e Neuroquimica
# ═══════════════════════════════════════════════════════════════════════════════

MENTAL_SNPS = {
    "rs25531": {
        "gene": "SLC6A4", "trait": "Transportador de Serotonina",
        "variants": {
            "AA": {"score": "normal", "text": "Expressao alta do transportador de serotonina (5-HTTLPR longo). Maior resiliencia ao estresse emocional e menor risco de depressao reativa."},
            "AG": {"score": "atencao", "text": "Expressao intermediaria — sensibilidade moderada ao estresse emocional. Rede de apoio social e atividade fisica ajudam a manter equilibrio."},
            "GA": {"score": "atencao", "text": "Sensibilidade moderada ao estresse emocional."},
            "GG": {"score": "alerta", "text": "Expressao baixa de 5-HTT — maior sensibilidade a experiencias negativas. Exercicio regular, meditacao e terapia cognitivo-comportamental sao particularmente beneficos. Busque apoio profissional quando necessario."},
        },
    },
    "rs4680": {
        "gene": "COMT", "trait": "Equilibrio de Dopamina",
        "variants": {
            "GG": {"score": "warrior", "text": "COMT rapido (Val/Val) — 'guerreiro'. Dopamina limpa rapido: resiliente sob pressao, mas pode buscar estimulacao excessiva. Bom em situacoes de emergencia."},
            "GA": {"score": "normal", "text": "COMT intermediario — equilibrio entre foco sustentado e resiliencia ao estresse. Perfil flexivel."},
            "AG": {"score": "normal", "text": "COMT intermediario."},
            "AA": {"score": "worrier", "text": "COMT lento (Met/Met) — 'estrategista'. Dopamina elevada: foco excepcional e memoria de trabalho superior, mas vulneravel a ansiedade sob pressao. Meditacao, yoga e ambiente calmo otimizam desempenho."},
        },
    },
    "rs6265": {
        "gene": "BDNF", "trait": "Neuroplasticidade e Humor",
        "variants": {
            "CC": {"score": "normal", "text": "BDNF Val66Val — producao normal de fator neurotrofico. Boa neuroplasticidade e resposta a exercicio para humor."},
            "CT": {"score": "atencao", "text": "BDNF Val66Met — producao reduzida. Exercicio aerobico e o estimulador mais potente de BDNF e deve ser prioridade para saude mental. Meditacao tambem ajuda."},
            "TC": {"score": "atencao", "text": "BDNF reduzido. Exercicio e essencial para saude mental."},
            "TT": {"score": "alerta", "text": "BDNF Met66Met — producao significativamente reduzida. Exercicio DIARIO e critico para manter humor e cognição. Considere acompanhamento psicologico preventivo."},
        },
    },
    "rs1800497": {
        "gene": "DRD2", "trait": "Receptores de Dopamina e Recompensa",
        "variants": {
            "GG": {"score": "normal", "text": "Densidade normal de receptores D2 de dopamina. Sistema de recompensa equilibrado."},
            "GA": {"score": "atencao", "text": "DRD2 Taq1A — menor densidade de receptores. Pode buscar mais estimulacao (cafe, redes sociais, jogos). Exercicio e hobbies criativos satisfazem essa necessidade de forma saudavel."},
            "AG": {"score": "atencao", "text": "Menor densidade de receptores de dopamina. Busca de recompensa aumentada."},
            "AA": {"score": "alerta", "text": "Densidade significativamente reduzida de D2. Maior vulnerabilidade a comportamentos compulsivos (redes sociais, jogos, compras). Exercicio regular e rotinas estruturadas sao protetores. Busque apoio se notar padroes compulsivos."},
        },
    },
    "rs53576": {
        "gene": "OXTR", "trait": "Receptor de Ocitocina e Empatia",
        "variants": {
            "GG": {"score": "otimo", "text": "Alta sensibilidade a ocitocina — forte tendencia a empatia, vinculos sociais e confianca. Relacoes sociais sao muito importantes para seu bem-estar."},
            "GA": {"score": "normal", "text": "Sensibilidade intermediaria a ocitocina — equilibrio entre empatia e autonomia emocional."},
            "AG": {"score": "normal", "text": "Sensibilidade intermediaria a ocitocina."},
            "AA": {"score": "atencao", "text": "Menor sensibilidade a ocitocina — pode perceber menos sinais sociais e ter menos necessidade de contato fisico. Nao e 'melhor' ou 'pior', apenas diferente. Pode ser vantajoso em situacoes que exigem objetividade."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# FOOD — Sensibilidades Alimentares
# ═══════════════════════════════════════════════════════════════════════════════

FOOD_SNPS = {
    "rs2187668": {
        "gene": "HLA-DQ2.5", "trait": "Predisposicao a Doenca Celiaca",
        "variants": {
            "CC": {"score": "normal", "text": "Sem alelo HLA-DQ2.5 — risco muito baixo de doenca celiaca. Pode consumir gluten normalmente."},
            "CT": {"score": "atencao", "text": "Portador de HLA-DQ2.5 — predisposicao genetica a doenca celiaca. NAO significa que voce tem celiaca (~3% dos portadores desenvolvem). Se tiver sintomas gastrointestinais, faca sorologia anti-transglutaminase."},
            "TC": {"score": "atencao", "text": "Portador de HLA-DQ2.5. Predisposicao, nao diagnostico."},
            "TT": {"score": "alerta", "text": "Homozigoto HLA-DQ2.5 — risco significativamente aumentado de doenca celiaca. Recomenda-se sorologia anti-transglutaminase IgA. Se positiva, biopsia duodenal confirma. NAO retire gluten da dieta antes do teste — isso falseia o resultado."},
        },
    },
    "rs7775228": {
        "gene": "HLA-DQ8", "trait": "Celiaca Tipo 2 (HLA-DQ8)",
        "variants": {
            "CC": {"score": "normal", "text": "Sem alelo HLA-DQ8 de risco. Risco adicional de celiaca baixo por esta via."},
            "CT": {"score": "atencao", "text": "Portador de HLA-DQ8 — predisposicao adicional a celiaca (5-10% dos celiacos sao DQ8+ sem DQ2). Relevante se DQ2 tambem e positivo."},
            "TC": {"score": "atencao", "text": "Portador de HLA-DQ8."},
            "TT": {"score": "alerta", "text": "Homozigoto HLA-DQ8. Combinado com DQ2, aumenta significativamente o risco. Sorologia celiaca recomendada se sintomas."},
        },
    },
    "rs602662": {
        "gene": "FUT2", "trait": "Status Secretor (Microbioma e B12)",
        "variants": {
            "GG": {"score": "normal", "text": "Secretor — produz antigenos ABH nas mucosas. Microbioma intestinal diversificado. Absorve vitamina B12 normalmente pela via intrinseca."},
            "GA": {"score": "normal", "text": "Secretor (uma copia) — perfil normal de microbioma e absorcao de B12."},
            "AG": {"score": "normal", "text": "Secretor. Absorcao normal."},
            "AA": {"score": "atencao", "text": "Nao-secretor (~20% da populacao) — microbioma diferente, pode ter niveis mais baixos de B12 e maior resistencia a norovirus. Monitore B12 e considere suplementacao."},
        },
    },
    "rs4988235": {
        "gene": "MCM6/LCT", "trait": "Intolerancia a Lactose",
        "variants": {
            "TT": {"score": "normal", "text": "Persistencia da lactase — tolera lactose ao longo da vida. Pode consumir leite e derivados sem restricao."},
            "TC": {"score": "normal", "text": "Uma copia de persistencia — provavelmente tolerante a lactose."},
            "CT": {"score": "normal", "text": "Uma copia de persistencia."},
            "CC": {"score": "alerta", "text": "Intolerancia a lactose genetica — a producao de lactase diminui na idade adulta. Laticinios fermentados (iogurte, kefir, queijos curados) geralmente sao tolerados. Use enzima lactase antes de consumir leite."},
        },
    },
    "rs182549": {
        "gene": "MCM6", "trait": "Persistencia da Lactase (Europeu)",
        "variants": {
            "CC": {"score": "normal", "text": "Alelo europeu de persistencia da lactase. Mantém producao de lactase na vida adulta."},
            "CT": {"score": "normal", "text": "Uma copia — provavelmente tolerante a lactose."},
            "TC": {"score": "normal", "text": "Uma copia de persistencia."},
            "TT": {"score": "alerta", "text": "Sem alelo europeu de persistencia. Alta probabilidade de intolerancia a lactose na idade adulta. Laticinios fermentados e enzima lactase sao alternativas."},
        },
    },
    "rs1800497": {
        "gene": "DRD2/ANKK1", "trait": "Comportamento Alimentar Compulsivo",
        "variants": {
            "GG": {"score": "normal", "text": "Sistema de recompensa alimentar equilibrado. Saciedade e satisfacao com porcoes normais."},
            "GA": {"score": "atencao", "text": "Taq1A — menor ativacao dos receptores de recompensa por alimentos. Pode precisar de mais comida para sentir satisfacao. Comer devagar e sem distracao ajuda."},
            "AG": {"score": "atencao", "text": "Tendencia a comer mais para sentir satisfacao."},
            "AA": {"score": "alerta", "text": "Receptores de recompensa significativamente reduzidos. Maior risco de comer emocional e compulsao alimentar. Mindful eating, porcoes pre-servidas e exercicio regular como fonte alternativa de dopamina."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# THYROID — Tireoide
# ═══════════════════════════════════════════════════════════════════════════════

THYROID_SNPS = {
    "rs965513": {
        "gene": "FOXE1", "trait": "Predisposicao a Doenca Tireoidiana",
        "variants": {
            "GG": {"score": "normal", "text": "Sem alelo de risco FOXE1. Risco padrao de doenca tireoidiana."},
            "GA": {"score": "atencao", "text": "Portador de variante FOXE1 — risco 1.4x de hipotireoidismo/Hashimoto. Monitore TSH anualmente, especialmente se mulher."},
            "AG": {"score": "atencao", "text": "Portador FOXE1. TSH anual recomendado."},
            "AA": {"score": "alerta", "text": "Homozigoto FOXE1 — risco ~2x de doenca tireoidiana autoimune. TSH + anti-TPO anual obrigatorio. Sintomas: cansaco inexplicavel, ganho de peso, pele seca, sensibilidade ao frio."},
        },
    },
    "rs2476601": {
        "gene": "PTPN22", "trait": "Autoimunidade Tireoidiana (e outras)",
        "variants": {
            "GG": {"score": "normal", "text": "Sem variante de risco PTPN22. Risco padrao de autoimunidade."},
            "GA": {"score": "atencao", "text": "Variante PTPN22 R620W — risco aumentado de tireoide de Hashimoto, artrite reumatoide e diabetes tipo 1. Este gene e um regulador central da autoimunidade."},
            "AG": {"score": "atencao", "text": "Portador PTPN22 R620W. Risco aumentado de autoimunidade."},
            "AA": {"score": "alerta", "text": "Homozigoto PTPN22 — risco significativamente aumentado de multiplas doencas autoimunes. Acompanhamento com endocrinologista e reumatologista recomendado."},
        },
    },
    "rs179247": {
        "gene": "TSHR", "trait": "Receptor de TSH e Doenca de Graves",
        "variants": {
            "AA": {"score": "normal", "text": "Receptor de TSH padrao. Risco basal de Doenca de Graves."},
            "AT": {"score": "atencao", "text": "Variante no receptor de TSH — risco levemente aumentado de hipertireoidismo (Graves). Atencao a: taquicardia, perda de peso, tremor, irritabilidade."},
            "TA": {"score": "atencao", "text": "Variante TSHR. Atencao a sintomas de hipertireoidismo."},
            "TT": {"score": "alerta", "text": "Risco aumentado de Doenca de Graves (hipertireoidismo autoimune). Se sintomas: TSH + T4 livre + TRAb. Mais comum em mulheres 20-40 anos."},
        },
    },
    "rs3184504": {
        "gene": "SH2B3", "trait": "Autoimunidade e Tireoide",
        "variants": {
            "CC": {"score": "normal", "text": "Variante padrao SH2B3. Regulacao imunologica normal."},
            "CT": {"score": "atencao", "text": "SH2B3 rs3184504 — associada a risco aumentado de Hashimoto e hipotireoidismo. Tambem ligada a doenca celiaca e diabetes tipo 1."},
            "TC": {"score": "atencao", "text": "Portador SH2B3. Risco moderado."},
            "TT": {"score": "alerta", "text": "Homozigoto SH2B3 — perfil de risco autoimune elevado (tireoide + celiaca + DM1). TSH + anti-TPO + anti-tTG recomendados."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# EYES — Saude Ocular
# ═══════════════════════════════════════════════════════════════════════════════

EYES_SNPS = {
    "rs10490924": {
        "gene": "ARMS2", "trait": "Degeneracao Macular (DMRI) — Locus Principal",
        "variants": {
            "GG": {"score": "normal", "text": "Sem alelo de risco ARMS2. Risco padrao de DMRI."},
            "GT": {"score": "atencao", "text": "Portador de ARMS2 A69S — risco ~2.5x de degeneracao macular relacionada a idade (DMRI). Exame de fundo de olho anual apos 50 anos. Luteina + zeaxantina podem ajudar."},
            "TG": {"score": "atencao", "text": "Portador ARMS2. Exame oftalmologico anual apos 50."},
            "TT": {"score": "alerta", "text": "Homozigoto ARMS2 — risco ~7x de DMRI. Exame de fundo de olho anual obrigatorio apos 40 anos. Suplementar AREDS2 (luteina, zeaxantina, omega-3). Nao fumar — tabagismo multiplica o risco."},
        },
    },
    "rs1061170": {
        "gene": "CFH", "trait": "Complemento e DMRI",
        "variants": {
            "TT": {"score": "normal", "text": "CFH Y402H referencia. Risco padrao de DMRI."},
            "TC": {"score": "atencao", "text": "CFH Y402H heterozigoto — risco ~2x de DMRI. O sistema complemento contribui para inflamacao retiniana. Dieta anti-inflamatoria e protecao UV beneficiam."},
            "CT": {"score": "atencao", "text": "Portador CFH. Protecao UV e dieta anti-inflamatoria recomendados."},
            "CC": {"score": "alerta", "text": "CFH Y402H homozigoto — risco ~5-7x de DMRI. Exame oftalmologico regular essencial. AREDS2, oculos com protecao UV, nao fumar."},
        },
    },
    "rs2285714": {
        "gene": "CFI", "trait": "Regulacao do Complemento e DMRI",
        "variants": {
            "CC": {"score": "normal", "text": "Regulacao normal do complemento. Sem aumento de risco por este locus."},
            "CT": {"score": "atencao", "text": "Variante CFI — contribuicao adicional ao risco de DMRI via desregulacao do complemento."},
            "TC": {"score": "atencao", "text": "Portador CFI. Contribuicao ao risco de DMRI."},
            "TT": {"score": "alerta", "text": "CFI homozigoto — risco aumentado de DMRI. Combinado com CFH e ARMS2, o risco total pode ser muito elevado."},
        },
    },
    "rs1048661": {
        "gene": "LOXL1", "trait": "Glaucoma de Esfoliacao",
        "variants": {
            "GG": {"score": "normal", "text": "LOXL1 referencia. Risco padrao de glaucoma."},
            "GT": {"score": "atencao", "text": "Variante LOXL1 — associada a sindrome de esfoliacao e glaucoma. Medicao de pressao intraocular anual recomendada apos 40 anos."},
            "TG": {"score": "atencao", "text": "Portador LOXL1. Medicao de pressao ocular anual."},
            "TT": {"score": "alerta", "text": "LOXL1 homozigoto — risco significativamente aumentado de glaucoma de esfoliacao. Exame oftalmologico completo anual (pressao + campo visual + OCT)."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# BONES — Osteoporose e Saude Ossea
# ═══════════════════════════════════════════════════════════════════════════════

BONES_SNPS = {
    "rs2228570": {
        "gene": "VDR", "trait": "Receptor de Vitamina D e Densidade Ossea",
        "variants": {
            "CC": {"score": "normal", "text": "VDR FokI CC — absorcao eficiente de calcio. Densidade ossea favorecida com ingesta adequada de calcio e vitamina D."},
            "CT": {"score": "atencao", "text": "VDR FokI intermediario — absorcao de calcio pode ser moderadamente reduzida. Suplemente vitamina D3 e garanta 1000mg/dia de calcio."},
            "TC": {"score": "atencao", "text": "VDR intermediario. Atencao a calcio e vitamina D."},
            "TT": {"score": "alerta", "text": "VDR FokI TT — absorcao de calcio reduzida. Risco aumentado de osteoporose. Vitamina D3 (2000-4000UI), calcio (1200mg) e exercicio de impacto sao essenciais."},
        },
    },
    "rs1800012": {
        "gene": "COL1A1", "trait": "Colageno Tipo I e Risco de Fratura",
        "variants": {
            "GG": {"score": "normal", "text": "COL1A1 referencia — producao normal de colageno tipo I. Resistencia ossea padrao."},
            "GT": {"score": "atencao", "text": "COL1A1 Sp1 — producao alterada de colageno. Risco levemente aumentado de fraturas. Exercicio de impacto (caminhada, corrida leve, musculacao) fortalece ossos."},
            "TG": {"score": "atencao", "text": "Portador COL1A1 Sp1. Exercicio de impacto recomendado."},
            "TT": {"score": "alerta", "text": "COL1A1 Sp1 homozigoto — risco significativamente aumentado de osteoporose e fraturas. Densitometria ossea basal recomendada. Exercicio de impacto + vitamina D + calcio."},
        },
    },
    "rs3736228": {
        "gene": "LRP5", "trait": "Via Wnt e Massa Ossea",
        "variants": {
            "CC": {"score": "normal", "text": "LRP5 referencia — via Wnt normal para formacao ossea."},
            "CT": {"score": "atencao", "text": "LRP5 A1330V — via Wnt reduzida. Menor formacao ossea. Exercicio resistido e impacto sao especialmente importantes."},
            "TC": {"score": "atencao", "text": "Portador LRP5. Priorize exercicio resistido."},
            "TT": {"score": "alerta", "text": "LRP5 homozigoto — formacao ossea significativamente reduzida. Risco de osteoporose precoce. Densitometria, vitamina D, calcio e exercicio resistido sao criticos."},
        },
    },
    "rs4870044": {
        "gene": "ESR1", "trait": "Receptor de Estrogeno e Massa Ossea",
        "variants": {
            "CC": {"score": "normal", "text": "ESR1 referencia — resposta normal ao estrogeno para manutencao ossea."},
            "CT": {"score": "atencao", "text": "ESR1 variante — resposta reduzida ao estrogeno. Mulheres pos-menopausa: risco aumentado de perda ossea. Discuta terapia hormonal com ginecologista."},
            "TC": {"score": "atencao", "text": "Portadora ESR1. Atencao na pos-menopausa."},
            "TT": {"score": "alerta", "text": "ESR1 homozigoto — resposta significativamente reduzida ao estrogeno. Alto risco de osteoporose pos-menopausa. Densitometria precoce + avaliacao de TH."},
        },
    },
    "rs2282679": {
        "gene": "GC", "trait": "Vitamina D e Saude Ossea",
        "variants": {
            "GG": {"score": "normal", "text": "Transporte normal de vitamina D. Niveis adequados com exposicao solar e dieta."},
            "GT": {"score": "atencao", "text": "Tendencia a vitamina D mais baixa — afeta absorcao de calcio e saude ossea. Suplemente D3 2000-4000UI/dia."},
            "TG": {"score": "atencao", "text": "Vitamina D reduzida. Suplemente D3."},
            "TT": {"score": "alerta", "text": "Deficiencia provavel de vitamina D — impacto direto na mineralizacao ossea. Suplemente D3 4000-5000UI/dia + monitore 25-OH-D semestralmente."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# ALLERGY — Predisposicao Atopica e Alergias
# ═══════════════════════════════════════════════════════════════════════════════

ALLERGY_SNPS = {
    "rs7216389": {
        "gene": "ORMDL3/GSDMB", "trait": "Predisposicao a Asma",
        "variants": {
            "TT": {"score": "normal", "text": "Sem alelo de risco no locus 17q21. Risco padrao de asma."},
            "TC": {"score": "atencao", "text": "Portador do principal locus de risco de asma (17q21). Risco ~1.4x. Particularmente relevante se inicio na infancia. Evitar tabagismo (ativo e passivo)."},
            "CT": {"score": "atencao", "text": "Portador de risco para asma (17q21). Risco moderadamente aumentado."},
            "CC": {"score": "alerta", "text": "Homozigoto para o locus 17q21 — risco significativamente aumentado de asma, especialmente de inicio precoce. Se sintomas respiratorios: espirometria com broncodilatador."},
        },
    },
    "rs20541": {
        "gene": "IL13", "trait": "Producao de IgE e Atopia",
        "variants": {
            "GG": {"score": "normal", "text": "IL-13 padrao. Producao normal de IgE. Risco basal de atopia."},
            "GA": {"score": "atencao", "text": "IL-13 R130Q — producao aumentada de IgE. Predisposicao a rinite alergica, dermatite atopica e asma. Anti-histaminicos podem ser necessarios com mais frequencia."},
            "AG": {"score": "atencao", "text": "IL-13 variante. Tendencia atopica aumentada."},
            "AA": {"score": "alerta", "text": "IL-13 R130Q homozigoto — producao significativamente elevada de IgE. Perfil fortemente atopico. Alergista pode ajudar com manejo preventivo (imunoterapia, controle ambiental)."},
        },
    },
    "rs2228145": {
        "gene": "IL6R", "trait": "Inflamacao Alergica e Eczema",
        "variants": {
            "AA": {"score": "normal", "text": "IL-6R padrao. Sinalizacao inflamatoria normal."},
            "AC": {"score": "atencao", "text": "IL-6R D358A — sinalizacao inflamatoria alterada. Pode influenciar dermatite atopica e resposta inflamatoria cutanea. Hidratacao da pele e emolientes ajudam."},
            "CA": {"score": "atencao", "text": "IL-6R variante. Atencao a inflamacao cutanea."},
            "CC": {"score": "favoravel", "text": "IL-6R D358A homozigoto — paradoxalmente protetor para algumas doencas inflamatorias (artrite reumatoide). Perfil inflamatorio complexo."},
        },
    },
    "rs1800925": {
        "gene": "IL13", "trait": "Rinite Alergica",
        "variants": {
            "CC": {"score": "normal", "text": "Expressao normal de IL-13. Risco padrao de rinite alergica."},
            "CT": {"score": "atencao", "text": "Promotor de IL-13 alterado — expressao aumentada. Predisposicao a rinite alergica sazonal e perene. Controle ambiental (acaros, polen) e importante."},
            "TC": {"score": "atencao", "text": "Expressao aumentada de IL-13. Tendencia a rinite alergica."},
            "TT": {"score": "alerta", "text": "Expressao significativamente elevada de IL-13. Perfil de alto risco para rinite alergica cronica. Imunoterapia (vacina de alergia) pode ser discutida com alergista."},
        },
    },
    "rs10156191": {
        "gene": "AOC1/ABP1", "trait": "Degradacao de Histamina (DAO)",
        "variants": {
            "CC": {"score": "normal", "text": "Atividade normal de diamina oxidase (DAO). Degrada histamina alimentar eficientemente."},
            "CT": {"score": "atencao", "text": "Atividade reduzida de DAO — pode ter intolerancia a histamina: dores de cabeca, urticaria, congestao nasal apos alimentos fermentados, vinho, queijos curados. Tente dieta baixa em histamina por 2-4 semanas como teste."},
            "TC": {"score": "atencao", "text": "DAO reduzida. Atencao a alimentos ricos em histamina."},
            "TT": {"score": "alerta", "text": "DAO significativamente reduzida — intolerancia a histamina provavel. Evitar: vinho tinto, queijos curados, embutidos, fermentados, peixe enlatado. Suplemento de DAO antes das refeicoes pode ajudar (discutir com medico)."},
        },
    },
    "rs1049793": {
        "gene": "HNMT", "trait": "Metabolismo de Histamina (HNMT)",
        "variants": {
            "CC": {"score": "normal", "text": "Metilacao normal de histamina via HNMT. Processamento eficiente de histamina no sistema nervoso central."},
            "CG": {"score": "atencao", "text": "HNMT reduzido — metabolismo de histamina cerebral mais lento. Pode influenciar sono, ansiedade e sensibilidade a alimentos ricos em histamina."},
            "GC": {"score": "atencao", "text": "HNMT variante. Metabolismo de histamina reduzido."},
            "GG": {"score": "alerta", "text": "HNMT significativamente reduzido. Combinado com DAO baixo, cria perfil de alta sensibilidade a histamina. Dieta baixa em histamina e controle ambiental podem fazer grande diferenca."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# AUTOIMMUNE — Predisposicao Autoimune
# ═══════════════════════════════════════════════════════════════════════════════

AUTOIMMUNE_SNPS = {
    "rs2476601": {
        "gene": "PTPN22", "trait": "Predisposicao Autoimune Geral",
        "variants": {
            "GG": {"score": "normal", "text": "PTPN22 padrao. Risco basal de doencas autoimunes."},
            "GA": {"score": "atencao", "text": "PTPN22 R620W — variante associada a multiplas doencas autoimunes: tireoide de Hashimoto, artrite reumatoide, lupus, diabetes tipo 1. Risco ~1.5-2x para cada condicao individualmente."},
            "AG": {"score": "atencao", "text": "Portador PTPN22 R620W. Predisposicao autoimune aumentada."},
            "AA": {"score": "alerta", "text": "PTPN22 R620W homozigoto — risco significativamente aumentado de multiplas doencas autoimunes. Monitoramento de TSH, glicemia e marcadores inflamatorios recomendado."},
        },
    },
    "rs7574865": {
        "gene": "STAT4", "trait": "Lupus e Artrite Reumatoide",
        "variants": {
            "GG": {"score": "normal", "text": "STAT4 padrao. Risco basal de lupus e artrite reumatoide."},
            "GT": {"score": "atencao", "text": "STAT4 variante — risco ~1.5x de lupus eritematoso sistemico (LES) e artrite reumatoide. Mais relevante em mulheres (lupus afeta 9x mais mulheres)."},
            "TG": {"score": "atencao", "text": "Portador STAT4. Predisposicao a lupus."},
            "TT": {"score": "alerta", "text": "STAT4 homozigoto — risco ~2x de lupus. Se sintomas (dor articular, rash facial, fadiga, fotossensibilidade): dosagem de FAN e anti-DNA. Lupus e tratavel se diagnosticado precocemente."},
        },
    },
    "rs2241880": {
        "gene": "ATG16L1", "trait": "Doenca de Crohn / DII",
        "variants": {
            "AA": {"score": "normal", "text": "ATG16L1 padrao. Autofagia intestinal normal."},
            "AG": {"score": "atencao", "text": "ATG16L1 T300A — autofagia alterada no intestino. Risco ~1.4x de doenca de Crohn. Dieta anti-inflamatoria e probioticos podem ajudar. Se sintomas gastrointestinais cronicos: investigar DII."},
            "GA": {"score": "atencao", "text": "Portador ATG16L1. Predisposicao a doenca de Crohn."},
            "GG": {"score": "alerta", "text": "ATG16L1 T300A homozigoto — risco aumentado de Crohn. Atencao a diarreia cronica, dor abdominal, perda de peso inexplicada. Investigar com colonoscopia se sintomas persistentes."},
        },
    },
    "rs4349859": {
        "gene": "HLA-B*27", "trait": "Espondilite Anquilosante",
        "variants": {
            "GG": {"score": "normal", "text": "Sem marcador HLA-B27 neste locus. Risco baixo de espondilite anquilosante."},
            "GA": {"score": "alerta", "text": "Marcador proximo a HLA-B27 positivo — fortemente associado a espondilite anquilosante (dor lombar inflamatoria cronica). HLA-B27 tem OR ~100x, mas apenas ~5% dos portadores desenvolvem a doenca. Se dor lombar que piora com repouso e melhora com exercicio: investigar com reumatologista."},
            "AG": {"score": "alerta", "text": "Proximo a HLA-B27 positivo. Investigar se dor lombar inflamatoria."},
            "AA": {"score": "alerta", "text": "Forte marcador HLA-B27. Risco significativo de espondilite anquilosante. Dor lombar cronica (>3 meses, piora com repouso, melhora com movimento) deve ser investigada por reumatologista."},
        },
    },
    "rs12191877": {
        "gene": "HLA-C", "trait": "Psoriase",
        "variants": {
            "CC": {"score": "normal", "text": "Sem alelo de risco HLA-C para psoriase."},
            "CT": {"score": "atencao", "text": "Portador de alelo HLA-C de risco — predisposicao a psoriase (placas avermelhadas com escamas na pele). Estresse e um gatilho comum. Dermatologista pode orientar tratamento precoce."},
            "TC": {"score": "atencao", "text": "Portador de risco para psoriase."},
            "TT": {"score": "alerta", "text": "Risco aumentado de psoriase. Se lesoes cutaneas: consulte dermatologista. Psoriase tem tratamentos eficazes (biologicos, topicos). Associada tambem a artrite psoriasica e risco cardiovascular."},
        },
    },
    "rs6897932": {
        "gene": "IL7R", "trait": "Esclerose Multipla",
        "variants": {
            "CC": {"score": "normal", "text": "IL-7R padrao. Risco basal de esclerose multipla (EM)."},
            "CT": {"score": "atencao", "text": "IL-7R variante — risco levemente aumentado de esclerose multipla. EM e multifatorial (genetica + virus Epstein-Barr + vitamina D). Manter niveis adequados de vitamina D pode ser protetor."},
            "TC": {"score": "atencao", "text": "Portador IL-7R. Risco leve de EM."},
            "TT": {"score": "alerta", "text": "IL-7R homozigoto — risco aumentado de EM. Se sintomas neurologicos (formigamento, fraqueza, visao dupla, fadiga extrema): consultar neurologista. EM e tratavel se diagnosticada precocemente."},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYZE PANELS
# ═══════════════════════════════════════════════════════════════════════════════

ALL_PANELS = {
    "nutri": {"name": "Nutri", "name_full": "Nutricao e Metabolismo", "snps": NUTRI_SNPS},
    "fit": {"name": "Fit", "name_full": "Aptidao Fisica", "snps": FIT_SNPS},
    "skin": {"name": "Skin", "name_full": "Pele e Dermatologia", "snps": SKIN_SNPS},
    "aging": {"name": "Aging", "name_full": "Envelhecimento e Longevidade", "snps": AGING_SNPS},
    "sensory": {"name": "Sensory", "name_full": "Percepcao Sensorial", "snps": SENSORY_SNPS},
    "sleep": {"name": "Sleep", "name_full": "Sono e Cronobiologia", "snps": SLEEP_SNPS},
    "longevity": {"name": "Longevity", "name_full": "Longevidade", "snps": LONGEVITY_SNPS},
    "mental": {"name": "Mental", "name_full": "Saude Mental e Neuroquimica", "snps": MENTAL_SNPS},
    "food": {"name": "Food", "name_full": "Sensibilidades Alimentares", "snps": FOOD_SNPS},
    "thyroid": {"name": "Thyroid", "name_full": "Tireoide", "snps": THYROID_SNPS},
    "eyes": {"name": "Eyes", "name_full": "Saude Ocular", "snps": EYES_SNPS},
    "bones": {"name": "Bones", "name_full": "Saude Ossea", "snps": BONES_SNPS},
    "allergy": {"name": "Allergy", "name_full": "Predisposicao Atopica e Alergias", "snps": ALLERGY_SNPS},
    "autoimmune": {"name": "Autoimmune", "name_full": "Predisposicao Autoimune", "snps": AUTOIMMUNE_SNPS},
}

SCORE_COLORS = {
    "normal": "success",
    "favoravel": "success",
    "otimo": "success",
    "power": "primary",
    "endurance": "primary",
    "misto": "info",
    "warrior": "warning",
    "worrier": "warning",
    "atencao": "warning",
    "alerta": "danger",
    "critico": "danger",
}

SCORE_LABELS = {
    "normal": "Normal",
    "favoravel": "Favoravel",
    "otimo": "Otimo",
    "power": "Potencia",
    "endurance": "Resistencia",
    "misto": "Misto",
    "warrior": "Guerreiro",
    "worrier": "Estrategista",
    "atencao": "Atencao",
    "alerta": "Alerta",
    "critico": "Critico",
}

SCORE_LABELS_EN = {
    "normal": "Normal",
    "favoravel": "Favorable",
    "otimo": "Optimal",
    "power": "Power",
    "endurance": "Endurance",
    "misto": "Mixed",
    "warrior": "Warrior",
    "worrier": "Strategist",
    "atencao": "Attention",
    "alerta": "Alert",
    "critico": "Critical",
}


def analyze_panel(panel_key: str, genome_by_rsid: dict, lang: str = "pt") -> dict:
    """Analyze a single wellness panel against the genome.

    Returns: {
        "findings": [{gene, trait, rsid, genotype, score, text}, ...],
        "summary": {total, normal, atencao, alerta},
        "conclusions": [str, ...],
    }
    """
    panel = ALL_PANELS.get(panel_key)
    if not panel:
        return {"findings": [], "summary": {}, "conclusions": []}

    # Load EN translations if needed
    en_data = {}
    en_overrides = {}
    if lang == "en":
        try:
            from src.wellness_i18n import WELLNESS_EN, WELLNESS_EN_PANEL_OVERRIDES
            en_data = WELLNESS_EN
            en_overrides = WELLNESS_EN_PANEL_OVERRIDES
        except ImportError:
            pass
    labels = SCORE_LABELS_EN if lang == "en" else SCORE_LABELS

    findings = []
    for rsid, info in panel["snps"].items():
        if rsid not in genome_by_rsid:
            continue
        genotype = genome_by_rsid[rsid]["genotype"]
        variant = info["variants"].get(genotype)
        if not variant and len(genotype) == 2:
            variant = info["variants"].get(genotype[::-1])
            if variant:
                genotype = genotype[::-1]
        if not variant:
            continue

        trait = info["trait"]
        text = variant["text"]

        # Apply EN translation
        if lang == "en":
            # Check panel-specific override first
            override = en_overrides.get((panel_key, rsid))
            if override:
                trait = override.get("trait_en", trait)
                text = override.get("variants", {}).get(genotype, text)
            elif rsid in en_data:
                trait = en_data[rsid].get("trait_en", trait)
                text = en_data[rsid].get("variants", {}).get(genotype, text)

        findings.append({
            "gene": info["gene"],
            "trait": trait,
            "rsid": rsid,
            "genotype": genotype,
            "score": variant["score"],
            "text": text,
            "color": SCORE_COLORS.get(variant["score"], "secondary"),
            "label": labels.get(variant["score"], variant["score"]),
        })

    # Summary
    summary = {
        "total": len(findings),
        "normal": sum(1 for f in findings if f["score"] in ("normal", "favoravel", "otimo")),
        "atencao": sum(1 for f in findings if f["score"] in ("atencao", "misto", "warrior", "worrier")),
        "alerta": sum(1 for f in findings if f["score"] in ("alerta", "critico")),
    }

    # Conclusions — only for atencao/alerta findings
    conclusions = []
    for f in findings:
        if f["score"] in ("alerta", "critico"):
            conclusions.append(f"**{f['gene']}** ({f['trait']}): {f['text']}")
        elif f["score"] in ("atencao", "warrior", "worrier"):
            conclusions.append(f"**{f['gene']}** ({f['trait']}): {f['text']}")

    return {"findings": findings, "summary": summary, "conclusions": conclusions}


def _resolve_apoe(findings: list, genome_by_rsid: dict):
    """Replace the partial rs429358 APOE entry with the combined isoform result."""
    from src.analyzer import determine_apoe

    apoe = determine_apoe(genome_by_rsid)
    if not apoe:
        return

    for f in findings:
        if f["rsid"] == "rs429358":
            isoform = apoe["isoform"]
            f["gene"] = "APOE"
            f["trait"] = f"Isoforma {isoform}"
            f["text"] = f"**{isoform}** (rs429358={apoe['rs429358']}, rs7412={apoe['rs7412']}): {apoe['description']}"

            # Update score based on combined magnitude
            mag = apoe["magnitude"]
            if mag >= 4:
                f["score"] = "critico"
            elif mag >= 3:
                f["score"] = "alerta"
            elif mag >= 2:
                f["score"] = "atencao"
            else:
                f["score"] = "favoravel"
            f["color"] = SCORE_COLORS.get(f["score"], "secondary")
            f["label"] = SCORE_LABELS.get(f["score"], f["score"])
            break


def analyze_all_panels(genome_by_rsid: dict, lang: str = "pt") -> dict:
    """Analyze all wellness panels."""
    results = {key: analyze_panel(key, genome_by_rsid, lang=lang) for key in ALL_PANELS}

    # Resolve APOE isoform in Aging panel
    if "aging" in results and results["aging"]["findings"]:
        _resolve_apoe(results["aging"]["findings"], genome_by_rsid)
        # Rebuild conclusions with resolved APOE
        conclusions = []
        for f in results["aging"]["findings"]:
            if f["score"] in ("alerta", "critico", "atencao", "warrior", "worrier"):
                conclusions.append(f"**{f['gene']}** ({f['trait']}): {f['text']}")
        results["aging"]["conclusions"] = conclusions

    return results
