# Gene Lens

> Leia em [Inglês](README.md).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![Local First](https://img.shields.io/badge/Privacidade-Local_First-brightgreen.svg)](#arquitetura-de-privacidade)

**Dashboard de exploração genética local-first.** Projetado para análise offline de dados brutos de DNA de serviços de genotipagem (23andMe, AncestryDNA, MyHeritage, Genera/MeuDNA) contra bancos de dados públicos de referência (ClinVar, PharmGKB) — bloqueia o acesso padrão de rede do Python durante a análise e processa tudo na sua máquina.

Construído com Flask, Apache ECharts, Halfmoon CSS e fonte Geist. IA local opcional via Ollama e tradução neural via Argos Translate.

---

## Por que criei este projeto

Tem uma longa linha de doenças hereditárias na minha família — condições que apareceram em várias gerações, com componente genético documentado. Crescer com isso significa carregar uma pergunta silenciosa: quanto da minha saúde já está escrita, e quanto é coincidência?

Quando esbarrei num [post sobre explorar dados brutos do 23andMe contra bancos públicos](https://www.youtube.com/@nicksaraev), o assunto clicou. Eu tinha o arquivo. Os bancos de referência (ClinVar, PharmGKB) eram gratuitos. Só faltava uma ferramenta que não mandasse meu DNA pra algum serviço em nuvem pra ser processado.

Então construí uma. O que me surpreendeu não foi a parte técnica — foi a sobreposição. Várias variantes que a ferramenta sinalizou bateram com condições que já tinham sido confirmadas pelos meus médicos anos antes, às vezes pra coisas que eu nem tinha pensado em mencionar. Outros achados abriram perguntas que levei pra minha próxima consulta. O ponto nunca foi me auto-diagnosticar — foi parar de ser passageiro em conversas sobre o meu próprio corpo.

Se você tem um histórico familiar parecido, ou só é curioso, essa ferramenta existe pra isso. Roda inteira na sua máquina, seu DNA não sai dela, e os achados são enquadrados como pontos de partida pra conversas com um profissional — não respostas.

---

## O que este projeto é / não é

| Este projeto É | Este projeto NÃO É |
|---|---|
| Uma ferramenta educacional de exploração de dados brutos de DNA | Uma ferramenta de diagnóstico ou dispositivo médico (SaMD) |
| Uma forma de gerar tópicos de discussão para seu médico | Um substituto para testes genéticos clínicos |
| Um ponto de partida para curiosidade genômica pessoal | Um teste confirmatório — resultado negativo não exclui risco |
| Software open-source com disclaimers éticos rigorosos | Um produto que garante precisão clínica |

---

> [!WARNING]
> **ESTE SOFTWARE NÃO É UM DISPOSITIVO MÉDICO (SaMD). NÃO SE DESTINA A DIAGNOSTICAR, TRATAR, CURAR OU PREVENIR QUALQUER DOENÇA. FINALIDADE EXCLUSIVAMENTE EDUCACIONAL E DE AUTOCONHECIMENTO.**
>
> Testes de genotipagem de consumo (23andMe, Genera, AncestryDNA, etc.) possuem taxa de falso positivo de aproximadamente **40%** para variantes clinicamente significativas (Tandy-Connor et al., *Genetics in Medicine*, 2018). Isso significa que quase metade dos achados "patogênicos" de testes de consumo estão **errados** quando confirmados por sequenciamento clínico.
>
> **NUNCA altere medicamentos, dietas ou tratamentos baseado nestes resultados sem consultar um médico.** O autor/mantenedor **NÃO se responsabiliza** por decisões clínicas, sofrimento psicológico (ansiedade induzida por falsos positivos) ou quaisquer danos causados pelo uso deste software.
>
> Aconselhamento genético profissional: [findageneticcounselor.nsgc.org](https://findageneticcounselor.nsgc.org)

---

## Funcionalidades

- **Privacidade local-first** — O acesso padrão de rede do Python é bloqueado (`socket` substituído) durante a análise. Projetado para que dados de DNA não saiam da sua máquina. Arquivos enviados são sobrescritos com dados aleatórios após o processamento.
- **Dashboard interativo** — UI dark com visualizações ECharts (gráficos, mapas de ancestralidade, tabelas de variantes), servido localmente em `127.0.0.1`. Zero dependências de CDN.
- **Farmacogenômica** — Interações droga-gene do PharmGKB/CPIC com níveis de evidência 1A/1B/2A/2B e anotação baseada em referência por gene.
- **Exploração de variantes de doença** — Classificação de variantes do ClinVar (patogênica, provavelmente patogênica, fator de risco, protetora) com nível de confiança (estrelas).
- **Roteamento clínico por sexo** — Renderização inteligente de condições hereditárias (HBOC/BRCA, Lynch, Próstata, Trombofilia, Hemocromatose, HF, Alfa-1 AT) condicionada ao sexo biológico, seguindo a abordagem de relatórios de laboratórios de grau clínico. Foca em condições monogênicas de alta ação em vez de traços poligênicos ruidosos.
- **12 painéis de bem-estar** — Nutrição, fitness, pele, envelhecimento, percepção sensorial, sono/cronobiologia, longevidade, saúde mental, sensibilidades alimentares, tireoide, saúde ocular e saúde óssea.
- **Ancestralidade** — Estimativa continental a partir de 22 marcadores informativos (AIMs) com mapa-múndi interativo.
- **Fenótipo** — Predição de cor dos olhos, cabelo, textura, sardas, alopecia androgênica (modelo HIrisPlex + loci GWAS). Cada predição mostra sua base genética (SNPs contribuintes).
- **Exploração de planejamento familiar** — Exploração de status de portador, fatores de risco gestacional (MTHFR, F5, F2), condições X-linked, transmissão de variantes dominantes.
- **Bilíngue** — Interface completa em português (PT-BR) e inglês com tradução médica neural (Argos Translate).
- **Visão humanizada + técnica** — Resumos em linguagem simples para autoexploração ao lado de apêndice técnico detalhado para revisão médica.
- **IA local** — Interpretação opcional de relatórios via Ollama (Llama, Gemma, etc.).

---

## Início Rápido

### Pré-requisitos

- **Python 3.10, 3.11 ou 3.12** (3.13+ pode funcionar mas não é coberto pelo CI)
- ~500 MB de espaço em disco para bancos de dados de referência

### 1. Clonar e instalar

```bash
git clone https://github.com/dimas-amendes/gene-lens.git
cd gene-lens

# Crie um ambiente virtual isolado (obrigatório em macOS/Linux modernos
# porque o Python do sistema recusa instalação global — PEP 668).
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

> **Por que venv?** No macOS (Python via Homebrew) e na maioria das distros Linux, `pip install` fora de um venv falha com `externally-managed-environment`. Usar `.venv` isola as dependências do projeto do seu Python de sistema.
>
> Para sair do venv depois: `deactivate`. Para reentrar em uma nova sessão: `source .venv/bin/activate`.

### 2. Baixar bancos de dados (única vez, requer internet)

```bash
python main.py download
```

Isso baixa:
- **ClinVar** (~120 MB comprimido) — gratuito, sem registro ([NCBI FTP](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/))
- **PharmGKB** — requer conta gratuita em [pharmgkb.org](https://www.pharmgkb.org/downloads). Baixe "Clinical Annotations" ZIP e extraia para `data/`.

> **Esta é a única etapa que requer internet.** Após o download dos bancos, toda análise é projetada para execução local-first, offline.

### 3. Iniciar o dashboard

```bash
python run.py                    # Mais simples — double-click no Windows
python main.py web               # Via CLI
python main.py web --port 8080   # Porta customizada
```

Abra [http://127.0.0.1:5000](http://127.0.0.1:5000) no navegador.

### 4. Testar com dados sintéticos

Um genoma sintético está incluído para teste (não precisa de DNA real):

```bash
# Via dashboard: faça upload de sample/sample_genome.csv na interface web
# Via CLI:
python main.py analyze sample/sample_genome.csv --name "Amostra"
```

### Opcional: Tradução neural (PT-BR)

```bash
pip install argostranslate
# O modelo (~100 MB) baixa automaticamente no primeiro uso
```

### Opcional: Interpretação por IA local

```bash
# Instalar Ollama: https://ollama.ai
ollama pull llama3.1:8b
python main.py analyze input/seu_dna.txt --ai
```

---

## Como os achados são priorizados

O sistema usa um modelo de evidência em múltiplas camadas para separar sinal de ruído:

| Camada | Fonte | O que significa |
|--------|-------|----------------|
| **ClinVar Review Status** (0-4 estrelas) | Revisão por especialistas NCBI | 4 estrelas = diretriz de prática; 1 estrela = submissor único; 0 = sem critérios |
| **Significância Clínica** | Classificação ClinVar | Patogênica > Provavelmente Patogênica > Fator de Risco > Incerta > Benigna |
| **Evidência PharmGKB/CPIC** | Ensaios clínicos | Nível 1A/1B = diretriz de dosagem CPIC; Nível 2A/2B = documentado mas sem diretriz formal |
| **Matriz de Condições Hereditárias** | Regras curadas por condição | Apenas condições monogênicas de alta ação com roteamento por sexo |

**Todos os achados notáveis requerem confirmação clínica.** Um achado sinalizado aqui é um motivo para conversar com seu médico, não um diagnóstico.

---

## Limitações Conhecidas

1. **Genotipagem de consumo não é sequenciamento clínico.** Chips de microarray testam ~600K-2M SNPs pré-selecionados; o sequenciamento clínico de exoma/genoma cobre 20K+ genes de forma abrangente.
2. **Cobertura incompleta de variantes raras.** A maioria das mutações patogênicas em genes como BRCA1/2 são privadas de famílias — chips podem perder completamente.
3. **Doenças comuns são poligênicas e multifatoriais.** Esta ferramenta não calcula Polygenic Risk Scores (PRS). Condições como diabetes, hipertensão e depressão envolvem centenas de genes mais ambiente.
4. **Ancestralidade e fenótipo são estimativas.** Baseados em marcadores limitados (~22 AIMs, ~16 SNPs de pigmentação) e modelos de frequência populacional. A ancestralidade real é muito mais complexa.
5. **Ausência de variante não exclui risco.** O arquivo pode simplesmente não conter o SNP relevante. Um relatório "limpo" não significa risco genético zero.

---

## Estrutura do Projeto

```
gene-lens/
├── run.py                  # Lançador rápido (double-click)
├── main.py                 # Ponto de entrada CLI
├── dashboard.py            # Dashboard web Flask
├── download_databases.py   # Baixador de bancos (único acesso à rede)
├── config.py               # Configuração e caminhos
├── requirements.txt        # Dependências Python
├── LICENSE                 # MIT
│
├── src/
│   ├── analyzer.py         # Motor de análise
│   ├── ancestry.py         # Ancestralidade continental (22 AIMs)
│   ├── consent.py          # Aceite de termos de uso
│   ├── databases.py        # Carregadores ClinVar & PharmGKB
│   ├── family_planning.py  # Exploração de portador e riscos gestacionais
│   ├── hereditary_conditions.py  # Matriz de roteamento clínico por sexo
│   ├── i18n.py             # Internacionalização (PT-BR / EN)
│   ├── local_ai.py         # Integração Ollama (opcional)
│   ├── parsers.py          # Parsers de formato DNA
│   ├── phenotype.py        # Predição de aparência (HIrisPlex + GWAS)
│   ├── privacy.py          # NetworkBlocker, exclusão segura
│   ├── reports.py          # Geração de relatórios Markdown
│   ├── sex_inference.py    # Inferência de sexo biológico por cromossomo Y
│   ├── snp_database.py     # Base curada (~200 variantes)
│   ├── translations.py     # Traduções de termos médicos
│   ├── translator.py       # Pipeline de tradução neural
│   └── wellness_panels.py  # 12 painéis de bem-estar (~80 SNPs)
│
├── templates/              # Templates Jinja2
├── static/                 # Assets locais (zero CDN)
├── sample/                 # Dados sintéticos de teste
├── data/                   # Bancos de referência (gitignored)
├── input/                  # Arquivos DNA do usuário (gitignored)
└── output/                 # Relatórios gerados (gitignored)
```

## Formatos Suportados

| Serviço | Formato | Auto-detectado |
|---------|---------|:---:|
| 23andMe | TSV 4 colunas (rsid, chr, pos, genótipo) | Sim |
| AncestryDNA | TSV 5 colunas (rsid, chr, pos, alelo1, alelo2) | Sim |
| MyHeritage | CSV com RSID, CHROMOSOME, POSITION, RESULT | Sim |
| Genera / MeuDNA | CSV com RSID, CHROMOSOME, POSITION, RESULT | Sim |
| Genérico | TSV ou CSV com colunas identificáveis de RSID, Cromossomo, Posição e Genótipo/Resultado | Sim |

Arquivos comprimidos (`.gz`) são suportados transparentemente.

---

## Arquitetura de Privacidade

Projetado para análise local-first, offline após o download inicial dos bancos de dados.

**Protege contra:**
- Upload acidental para nuvem durante análise (socket bloqueado)
- Vazamento de dados via CDN (todos os assets servidos localmente)
- Telemetria ou rastreamento (zero requisições externas)
- Chamadas de rede padrão do Python durante o processamento

**Não protege contra:**
- Malware já presente na máquina
- Pastas sincronizadas em nuvem (Dropbox, OneDrive, iCloud) — garanta que o diretório de trabalho não está sincronizado
- Backups do sistema que podem capturar arquivos genéticos
- Subprocessos externos que contornam a camada de socket do Python

**Medidas técnicas:**
1. **Bloqueio de Rede** — `socket.socket` e `socket.getaddrinfo` são substituídos durante a análise. Chamadas de rede padrão do Python geram `ConnectionError`.
2. **Exclusão Segura** — Arquivos DNA enviados são sobrescritos com dados aleatórios antes da exclusão.
3. **Sem Metadados** — Relatórios não contêm informações do sistema (hostname, usuário, caminhos).
4. **Apenas Local** — Flask escuta exclusivamente em `127.0.0.1`. Não acessível de outras máquinas.
5. **Sem Telemetria** — Zero analytics, rastreamento ou requisições externas.

Verifique sua configuração: `python main.py privacy-check`

---

## Atribuição de Dados

- **ClinVar** — NCBI, National Library of Medicine. Landrum MJ, et al. *Nucleic Acids Research*, 2020. [ncbi.nlm.nih.gov/clinvar](https://www.ncbi.nlm.nih.gov/clinvar/)
- **PharmGKB** — Stanford University, NIH/NIGMS. Whirl-Carrillo M, et al. *Clinical Pharmacology & Therapeutics*, 2021. [pharmgkb.org](https://www.pharmgkb.org/)
- **CPIC** — Clinical Pharmacogenetics Implementation Consortium. Relling MV, Klein TE. *Clinical Pharmacology & Therapeutics*, 2011. [cpicpgx.org](https://cpicpgx.org/)
- **HIrisPlex** — Walsh S, et al. *Forensic Science International: Genetics*, 2013.

---

## Licença

Licenciado sob a **MIT License**.

Você pode usar, copiar, modificar, mesclar, publicar, distribuir, sublicenciar e vender cópias deste software — inclusive para fins comerciais — desde que o aviso de copyright e a permissão sejam mantidos.

Veja [LICENSE](LICENSE) para o texto completo.

---

## Contribuindo

Contribuições são bem-vindas!

1. Faça um fork do repositório
2. Crie uma branch de feature (`git checkout -b feature/minha-feature`)
3. **Certifique-se de que nenhum dado pessoal/genético está incluído** nos commits
4. Submeta um Pull Request

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a MIT License.

---

## Agradecimentos

Inspirado na abordagem de exploração bioinformática demonstrada por [Nick Saraev](https://www.youtube.com/@nicksaraev). Embora o conceito original tenha fornecido a faísca, este projeto foi inteiramente reescrito com foco em execução local-first, licenciamento permissivo MIT, disclaimers éticos rigorosos, roteamento clínico por sexo e acessibilidade para usuários não-técnicos.

---

*Construído com cuidado pela privacidade e rigor científico. Seu DNA é só seu.*
