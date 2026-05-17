# Contributing to Genetic Health Analyzer

> Leia em portugues abaixo / Portuguese version below.

Thank you for your interest in contributing! This project welcomes improvements from the community, but has strict guidelines to protect user privacy and maintain scientific rigor.

## Language Policy

**All Issues, Pull Requests, commit messages, and code reviews must be in English.** This ensures the global community can participate. Code comments may be in English or Portuguese.

The project interface supports both English and Portuguese (PT-BR), and i18n contributions in Portuguese are welcome — but the development workflow itself is in English.

---

## Immediate Rejection Criteria

The following will be rejected without review:

- **Real DNA data** in any file, commit message, or comment
- **Network calls during analysis** — the NetworkBlocker is a core guarantee
- **Diagnostic wording** — "you have", "you are at risk", "recommended dose", "you should take"
- **Polygenic Risk Score (PRS) modules** — complex, ethnicity-dependent, misleading from consumer chips
- **Changes to privacy code** (`src/privacy.py`) without prior discussion in an Issue

## What We Accept

- Bug fixes with reproducible test cases
- New well-validated SNP analysis panels (with peer-reviewed citations and evidence quality)
- Translation improvements (PT-BR / EN)
- UI/UX improvements to the dashboard
- Documentation improvements
- Performance optimizations

## How to Contribute

### 1. Open an Issue first
For anything beyond a typo fix, please open an Issue to discuss the approach before writing code.

### 2. Follow the existing architecture

**For new SNP panels** (e.g., a new wellness panel):
- Add SNP definitions to `src/wellness_panels.py` following the existing pattern
- Register in `ALL_PANELS`
- Add i18n strings in BOTH `pt` and `en` sections of `src/i18n.py`
- Add the panel to the template loop in `templates/dashboard.html`
- Add test SNPs to `sample/sample_genome.csv`
- Each SNP must have peer-reviewed evidence (cite the study and note evidence strength)

**For sex-aware hereditary conditions:**
- Add to the matrix in `src/hereditary_conditions.py`
- Provide `text_F`, `text_M`, and `text_neutral` variants
- Set appropriate `priority_F` and `priority_M`
- Include `min_stars` threshold from ClinVar

**For health exploration notes** (topics for physician discussion):
- Use the `_PROTOCOL_PT` / `_PROTOCOL_EN` translation dictionaries in `src/reports.py`
- Reference ranges from literature only — never prescriptive language
- Always frame as "topics to discuss with your doctor"

### 3. Test locally
```bash
# Parse sample genome
python -c "from src.parsers import load_genome; g,_,f = load_genome('sample/sample_genome.csv'); print(f'{len(g)} SNPs, {f}')"

# Test all panels
python -c "
from src.parsers import load_genome
from src.wellness_panels import analyze_all_panels
g, _, _ = load_genome('sample/sample_genome.csv')
w = analyze_all_panels(g)
for k, v in w.items():
    print(f'{k}: {len(v.get(\"findings\", []))} findings')
"

# Run the dashboard
python run.py
# Upload sample/sample_genome.csv and verify your changes
```

### 4. Submit a Pull Request
- Fill out the PR template completely
- Ensure no genetic data is included
- Reference the Issue number
- Wait for CI to pass before requesting review

### 5. Keeping your branch in sync (prefer rebase)

When `main` advances while your PR is open, **rebase** your branch on top of `main` instead of merging `main` into it. This keeps the PR history linear and the diff focused on what you actually changed:

```bash
git fetch origin
git rebase origin/main
git push --force-with-lease
```

Avoid `git merge main` into a feature branch — it creates merge commits that pollute the PR diff with changes from `main` you didn't author.

If you're collaborating with someone else on the same branch, coordinate before rebasing and always use `--force-with-lease` (never `--force`).

PRs are squash-merged into `main`, so individual commits on your branch don't end up in `main` history — feel free to commit frequently while working.

## Wording Guidelines

This project uses **exploratory language**, not clinical/diagnostic language:

| Do NOT use | Use instead |
|---|---|
| "You have condition X" | "Variant associated with condition X detected" |
| "You are at risk for" | "May indicate predisposition to" |
| "Recommended dose: 500mg" | "Literature references doses of 400-800mg (discuss with physician)" |
| "Disease risk" | "Disease variant exploration" |
| "Clinical interpretation" | "Reference-based annotation" |
| "Risk assessment" | "Carrier-status exploration" |

## Code Style

- Python: follow existing patterns (no strict formatter enforced yet)
- Max line length: 150 characters
- Variable/function names: English
- Comments: English or Portuguese
- i18n strings: always add both PT-BR and EN

## Privacy Policy for Contributors

**NEVER commit:**
- Real genetic data (DNA files, genotypes, health reports)
- API keys, tokens, or credentials
- System paths containing usernames
- Any personally identifiable information

If you accidentally commit sensitive data, notify the maintainer immediately.

## License

By contributing, you agree that your contributions will be licensed under the **MIT License**.

---

# Contribuindo para o Analisador Genetico

Obrigado pelo interesse em contribuir! Este projeto aceita melhorias da comunidade, mas tem diretrizes rigorosas para proteger a privacidade dos usuarios e manter o rigor cientifico.

## Politica de Idioma

**Todas as Issues, Pull Requests, mensagens de commit e revisoes de codigo devem ser em ingles.** Isso garante que a comunidade global possa participar. Comentarios no codigo podem ser em ingles ou portugues.

---

## Criterios de Rejeicao Imediata

Os seguintes itens serao rejeitados sem revisao:

- **Dados geneticos reais** em qualquer arquivo, commit ou comentario
- **Chamadas de rede durante analise** — o NetworkBlocker e uma garantia central
- **Linguagem diagnostica** — "voce tem", "voce esta em risco", "dose recomendada", "voce deve tomar"
- **Modulos de Polygenic Risk Score (PRS)** — complexos, dependentes de etnia, enganosos com chips de consumo
- **Alteracoes no codigo de privacidade** (`src/privacy.py`) sem discussao previa em Issue

## O que Aceitamos

- Correcoes de bugs com casos de teste reproduziveis
- Novos paineis de SNPs bem validados (com citacoes e qualidade de evidencia)
- Melhorias de traducao (PT-BR / EN)
- Melhorias de UI/UX no dashboard
- Melhorias de documentacao

## Como Contribuir

1. **Abra uma Issue primeiro** para discutir a abordagem
2. **Siga a arquitetura existente** (veja exemplos nos paineis de wellness)
3. **Teste localmente** com `sample/sample_genome.csv`
4. **Submeta um Pull Request** preenchendo o template completo
5. **Aguarde o CI passar** antes de solicitar revisao

### Mantendo sua branch em sincronia (prefira rebase)

Quando a `main` avancar enquanto seu PR estiver aberto, **rebase** sua branch em cima da `main` em vez de mergear a `main` nela. Isso mantem o historico do PR linear e o diff focado no que voce efetivamente alterou:

```bash
git fetch origin
git rebase origin/main
git push --force-with-lease
```

Evite `git merge main` em uma branch de feature — cria merge commits que poluem o diff do PR com mudancas da `main` que voce nao fez.

Se voce esta colaborando com outra pessoa na mesma branch, combine antes de rebasear e sempre use `--force-with-lease` (nunca `--force`).

PRs sao mergeados via squash na `main`, entao commits individuais da sua branch nao vao parar no historico da `main` — pode commitar quantas vezes quiser enquanto trabalha.

## Diretrizes de Linguagem

Este projeto usa **linguagem exploratoria**, nao clinica/diagnostica:

| NAO use | Use em vez disso |
|---|---|
| "Voce tem condicao X" | "Variante associada a condicao X detectada" |
| "Voce esta em risco de" | "Pode indicar predisposicao a" |
| "Dose recomendada: 500mg" | "Literatura referencia doses de 400-800mg (discutir com medico)" |
| "Risco de doenca" | "Exploracao de variantes de doenca" |
| "Interpretacao clinica" | "Anotacao baseada em referencia" |

## Licenca

Ao contribuir, voce concorda que suas contribuicoes serao licenciadas sob a **MIT License**.
