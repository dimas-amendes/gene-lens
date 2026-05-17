# Analisador Genetico Local

> Leia em [Ingles](README.md).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![Local First](https://img.shields.io/badge/Privacidade-Local_First-brightgreen.svg)](#arquitetura-de-privacidade)

**Dashboard de exploracao genetica local-first.** Projetado para analise offline de dados brutos de DNA de servicos de genotipagem (23andMe, AncestryDNA, MyHeritage, Genera/MeuDNA) contra bancos de dados publicos de referencia (ClinVar, PharmGKB) — bloqueia acesso padrao de rede do Python durante analise e processa tudo na sua maquina.

Construido com Flask, Apache ECharts, Halfmoon CSS e fonte Geist. IA local opcional via Ollama e traducao neural via Argos Translate.

---

## Por que criei este projeto

Este sistema nasceu de uma necessidade pessoal: eu queria uma forma privada, offline e confiavel de olhar mais a fundo para a minha propria saude atraves do meu DNA, sem depender de servicos em nuvem. Como a ferramenta cumpriu esse objetivo para mim, decidi abri-la para a comunidade. Espero que seja util para a jornada de autoconhecimento de outras pessoas, e convido outros desenvolvedores a utilizarem e melhorarem o codigo.

---

## O que este projeto e / nao e

| Este projeto E | Este projeto NAO E |
|---|---|
| Uma ferramenta educacional de exploracao de dados brutos de DNA | Uma ferramenta de diagnostico ou dispositivo medico (SaMD) |
| Uma forma de gerar topicos de discussao para seu medico | Um substituto para testes geneticos clinicos |
| Um ponto de partida para curiosidade genomica pessoal | Um teste confirmatorio — resultado negativo nao exclui risco |
| Software open-source com disclaimers eticos rigorosos | Um produto que garante precisao clinica |

---

> [!WARNING]
> **ESTE SOFTWARE NAO E UM DISPOSITIVO MEDICO (SaMD). NAO SE DESTINA A DIAGNOSTICAR, TRATAR, CURAR OU PREVENIR QUALQUER DOENCA. FINALIDADE EXCLUSIVAMENTE EDUCACIONAL E DE AUTOCONHECIMENTO.**
>
> Testes de genotipagem de consumo (23andMe, Genera, AncestryDNA, etc.) possuem taxa de falso positivo de aproximadamente **40%** para variantes clinicamente significativas (Tandy-Connor et al., *Genetics in Medicine*, 2018). Isso significa que quase metade dos achados "patogenicos" de testes de consumo estao **errados** quando confirmados por sequenciamento clinico.
>
> **NUNCA altere medicamentos, dietas ou tratamentos baseado nestes resultados sem consultar um medico.** O autor/mantenedor **NAO se responsabiliza** por decisoes clinicas, sofrimento psicologico (ansiedade induzida por falsos positivos) ou quaisquer danos causados pelo uso deste software.
>
> Aconselhamento genetico profissional: [findageneticcounselor.nsgc.org](https://findageneticcounselor.nsgc.org)

---

## Funcionalidades

- **Privacidade local-first** — Acesso padrao de rede do Python e bloqueado (`socket` substituido) durante analise. Projetado para que dados de DNA nao saiam da sua maquina. Arquivos enviados sao sobrescritos com dados aleatorios apos processamento.
- **Dashboard interativo** — UI dark com visualizacoes ECharts (graficos, mapas de ancestralidade, tabelas de variantes), servido localmente em `127.0.0.1`. Zero dependencias de CDN.
- **Farmacogenomica** — Interacoes droga-gene do PharmGKB/CPIC com niveis de evidencia 1A/1B/2A/2B e anotacao baseada em referencia por gene.
- **Exploracao de variantes de doenca** — Classificacao de variantes do ClinVar (patogenica, provavelmente patogenica, fator de risco, protetora) com nivel de confianca (estrelas).
- **Roteamento clinico por sexo** — Renderizacao inteligente de condicoes hereditarias (HBOC/BRCA, Lynch, Prostata, Trombofilia, Hemocromatose, HF, Alfa-1 AT) condicionada ao sexo biologico, seguindo a abordagem de relatorios de laboratorios de grau clinico. Foca em condicoes monogenicas de alta acao em vez de tracos poligenicos ruidosos.
- **12 paineis de bem-estar** — Nutricao, fitness, pele, envelhecimento, percepcao sensorial, sono/cronobiologia, longevidade, saude mental, sensibilidades alimentares, tireoide, saude ocular e saude ossea.
- **Ancestralidade** — Estimativa continental a partir de 22 marcadores informativos (AIMs) com mapa-mundi interativo.
- **Fenotipo** — Predicao de cor dos olhos, cabelo, textura, sardas, alopecia androgenica (modelo HIrisPlex + loci GWAS). Cada predicao mostra sua base genetica (SNPs contribuintes).
- **Exploracao de planejamento familiar** — Exploracao de status de portador, fatores de risco gestacional (MTHFR, F5, F2), condicoes X-linked, transmissao de variantes dominantes.
- **Bilingue** — Interface completa em portugues (PT-BR) e ingles com traducao medica neural (Argos Translate).
- **Visao humanizada + tecnica** — Resumos em linguagem simples para autoexploracao ao lado de apendice tecnico detalhado para revisao medica.
- **IA local** — Interpretacao opcional de relatorios via Ollama (Llama, Gemma, etc.).

---

## Inicio Rapido

### Pre-requisitos

- **Python 3.10, 3.11 ou 3.12** (3.13+ pode funcionar mas nao e coberto pelo CI)
- ~500 MB de espaco em disco para bancos de dados de referencia

### 1. Clonar e instalar

```bash
git clone https://github.com/dimas-amendes/gene-lens.git
cd gene-lens

# Crie um ambiente virtual isolado (obrigatorio em macOS/Linux modernos
# porque o Python do sistema recusa instalacao global — PEP 668).
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

> **Por que venv?** No macOS (Python via Homebrew) e na maioria das distros Linux, `pip install` fora de um venv falha com `externally-managed-environment`. Usar `.venv` isola as dependencias do projeto do seu Python de sistema.
>
> Para sair do venv depois: `deactivate`. Para reentrar em uma nova sessao: `source .venv/bin/activate`.

### 2. Baixar bancos de dados (unica vez, requer internet)

```bash
python main.py download
```

Isso baixa:
- **ClinVar** (~120 MB comprimido) — gratuito, sem registro ([NCBI FTP](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/))
- **PharmGKB** — requer conta gratuita em [pharmgkb.org](https://www.pharmgkb.org/downloads). Baixe "Clinical Annotations" ZIP e extraia para `data/`.

> **Esta e a unica etapa que requer internet.** Apos o download dos bancos, toda analise e projetada para execucao local-first, offline.

### 3. Iniciar o dashboard

```bash
python run.py                    # Mais simples — double-click no Windows
python main.py web               # Via CLI
python main.py web --port 8080   # Porta customizada
```

Abra [http://127.0.0.1:5000](http://127.0.0.1:5000) no navegador.

### 4. Testar com dados sinteticos

Um genoma sintetico esta incluido para teste (nao precisa de DNA real):

```bash
# Via dashboard: faca upload de sample/sample_genome.csv na interface web
# Via CLI:
python main.py analyze sample/sample_genome.csv --name "Amostra"
```

### Opcional: Traducao neural (PT-BR)

```bash
pip install argostranslate
# O modelo (~100 MB) baixa automaticamente no primeiro uso
```

### Opcional: Interpretacao por IA local

```bash
# Instalar Ollama: https://ollama.ai
ollama pull llama3.1:8b
python main.py analyze input/seu_dna.txt --ai
```

---

## Como os achados sao priorizados

O sistema usa um modelo de evidencia em multiplas camadas para separar sinal de ruido:

| Camada | Fonte | O que significa |
|--------|-------|----------------|
| **ClinVar Review Status** (0-4 estrelas) | Revisao por especialistas NCBI | 4 estrelas = diretriz de pratica; 1 estrela = submissor unico; 0 = sem criterios |
| **Significancia Clinica** | Classificacao ClinVar | Patogenica > Provavelmente Patogenica > Fator de Risco > Incerta > Benigna |
| **Evidencia PharmGKB/CPIC** | Ensaios clinicos | Nivel 1A/1B = diretriz de dosagem CPIC; Nivel 2A/2B = documentado mas sem diretriz formal |
| **Matriz de Condicoes Hereditarias** | Regras curadas por condicao | Apenas condicoes monogenicas de alta acao com roteamento por sexo |

**Todos os achados notaveis requerem confirmacao clinica.** Um achado sinalizado aqui e um motivo para conversar com seu medico, nao um diagnostico.

---

## Limitacoes Conhecidas

1. **Genotipagem de consumo nao e sequenciamento clinico.** Chips de microarray testam ~600K-2M SNPs pre-selecionados; sequenciamento clinico de exoma/genoma cobre 20K+ genes de forma abrangente.
2. **Cobertura incompleta de variantes raras.** A maioria das mutacoes patogenicas em genes como BRCA1/2 sao privadas de familias — chips podem perder completamente.
3. **Doencas comuns sao poligenicas e multifatoriais.** Esta ferramenta nao calcula Polygenic Risk Scores (PRS). Condicoes como diabetes, hipertensao e depressao envolvem centenas de genes mais ambiente.
4. **Ancestralidade e fenotipo sao estimativas.** Baseados em marcadores limitados (~22 AIMs, ~16 SNPs de pigmentacao) e modelos de frequencia populacional. A ancestralidade real e muito mais complexa.
5. **Ausencia de variante nao exclui risco.** O arquivo pode simplesmente nao conter o SNP relevante. Um relatorio "limpo" nao significa risco genetico zero.

---

## Estrutura do Projeto

```
genetic-health-analyzer/
├── run.py                  # Lancador rapido (double-click)
├── main.py                 # Ponto de entrada CLI
├── dashboard.py            # Dashboard web Flask
├── download_databases.py   # Baixador de bancos (unico acesso a rede)
├── config.py               # Configuracao e caminhos
├── requirements.txt        # Dependencias Python
├── LICENSE                 # MIT
│
├── src/
│   ├── analyzer.py         # Motor de analise
│   ├── ancestry.py         # Ancestralidade continental (22 AIMs)
│   ├── consent.py          # Aceite de termos de uso
│   ├── databases.py        # Carregadores ClinVar & PharmGKB
│   ├── family_planning.py  # Exploracao de portador e riscos gestacionais
│   ├── hereditary_conditions.py  # Matriz de roteamento clinico por sexo
│   ├── i18n.py             # Internacionalizacao (PT-BR / EN)
│   ├── local_ai.py         # Integracao Ollama (opcional)
│   ├── parsers.py          # Parsers de formato DNA
│   ├── phenotype.py        # Predicao de aparencia (HIrisPlex + GWAS)
│   ├── privacy.py          # NetworkBlocker, exclusao segura
│   ├── reports.py          # Geracao de relatorios Markdown
│   ├── sex_inference.py    # Inferencia de sexo biologico por cromossomo Y
│   ├── snp_database.py     # Base curada (~200 variantes)
│   ├── translations.py     # Traducoes de termos medicos
│   ├── translator.py       # Pipeline de traducao neural
│   └── wellness_panels.py  # 12 paineis de bem-estar (~80 SNPs)
│
├── templates/              # Templates Jinja2
├── static/                 # Assets locais (zero CDN)
├── sample/                 # Dados sinteticos de teste
├── data/                   # Bancos de referencia (gitignored)
├── input/                  # Arquivos DNA do usuario (gitignored)
└── output/                 # Relatorios gerados (gitignored)
```

## Formatos Suportados

| Servico | Formato | Auto-detectado |
|---------|---------|:---:|
| 23andMe | TSV 4 colunas (rsid, chr, pos, genotipo) | Sim |
| AncestryDNA | TSV 5 colunas (rsid, chr, pos, alelo1, alelo2) | Sim |
| MyHeritage | CSV com RSID, CHROMOSOME, POSITION, RESULT | Sim |
| Genera / MeuDNA | CSV com RSID, CHROMOSOME, POSITION, RESULT | Sim |
| Generico | TSV ou CSV com colunas identificaveis de RSID, Cromossomo, Posicao e Genotipo/Resultado | Sim |

Arquivos comprimidos (`.gz`) sao suportados transparentemente.

---

## Arquitetura de Privacidade

Projetado para analise local-first, offline apos o download inicial dos bancos de dados.

**Protege contra:**
- Upload acidental para nuvem durante analise (socket bloqueado)
- Vazamento de dados via CDN (todos os assets servidos localmente)
- Telemetria ou rastreamento (zero requisicoes externas)
- Chamadas de rede padrao do Python durante processamento

**Nao protege contra:**
- Malware ja presente na maquina
- Pastas sincronizadas em nuvem (Dropbox, OneDrive, iCloud) — garanta que o diretorio de trabalho nao esta sincronizado
- Backups do sistema que podem capturar arquivos geneticos
- Subprocessos externos que contornam a camada de socket do Python

**Medidas tecnicas:**
1. **Bloqueio de Rede** — `socket.socket` e `socket.getaddrinfo` sao substituidos durante analise. Chamadas de rede padrao do Python geram `ConnectionError`.
2. **Exclusao Segura** — Arquivos DNA enviados sao sobrescritos com dados aleatorios antes da exclusao.
3. **Sem Metadados** — Relatorios nao contem informacoes do sistema (hostname, usuario, caminhos).
4. **Apenas Local** — Flask escuta exclusivamente em `127.0.0.1`. Nao acessivel de outras maquinas.
5. **Sem Telemetria** — Zero analytics, rastreamento ou requisicoes externas.

Verifique sua configuracao: `python main.py privacy-check`

---

## Atribuicao de Dados

- **ClinVar** — NCBI, National Library of Medicine. Landrum MJ, et al. *Nucleic Acids Research*, 2020. [ncbi.nlm.nih.gov/clinvar](https://www.ncbi.nlm.nih.gov/clinvar/)
- **PharmGKB** — Stanford University, NIH/NIGMS. Whirl-Carrillo M, et al. *Clinical Pharmacology & Therapeutics*, 2021. [pharmgkb.org](https://www.pharmgkb.org/)
- **CPIC** — Clinical Pharmacogenetics Implementation Consortium. Relling MV, Klein TE. *Clinical Pharmacology & Therapeutics*, 2011. [cpicpgx.org](https://cpicpgx.org/)
- **HIrisPlex** — Walsh S, et al. *Forensic Science International: Genetics*, 2013.

---

## Licenca

Licenciado sob a **MIT License**.

Voce pode usar, copiar, modificar, mesclar, publicar, distribuir, sublicenciar e vender copias deste software — inclusive para fins comerciais — desde que o aviso de copyright e a permissao sejam mantidos.

Veja [LICENSE](LICENSE) para o texto completo.

---

## Contribuindo

Contribuicoes sao bem-vindas!

1. Faca um fork do repositorio
2. Crie uma branch de feature (`git checkout -b feature/minha-feature`)
3. **Certifique-se de que nenhum dado pessoal/genetico esta incluido** nos commits
4. Submeta um Pull Request

Ao contribuir, voce concorda que suas contribuicoes serao licenciadas sob a MIT License.

---

## Agradecimentos

Inspirado na abordagem de exploracao bioinformatica demonstrada por [Nick Saraev](https://www.youtube.com/@nicksaraev). Embora o conceito original tenha fornecido a faísca, este projeto foi inteiramente reescrito com foco em execucao local-first, licenciamento permissivo MIT, disclaimers eticos rigorosos, roteamento clinico por sexo e acessibilidade para usuarios nao-tecnicos.

---

*Construido com cuidado pela privacidade e rigor cientifico. Seu DNA e so seu.*
