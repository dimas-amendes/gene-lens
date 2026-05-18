# Contributing to Gene Lens

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

**For privacy-critical changes** (anything in `src/privacy.py`, `src/consent.py`, `src/chat_store.py`, or `download_databases.py`):
- Open an Issue first to discuss the change
- Update or extend the relevant test (`tests/test_privacy.py`, `tests/test_chat_store.py`)
- Re-read [SECURITY.md](SECURITY.md) and check the threat model still holds
- Run `python main.py privacy-check` after the change

**For the AI chat** (`src/local_ai.py`):
- Keep the system prompts (PT + EN) non-prescriptive — they're the only thing standing between the model and a diagnostic-sounding reply
- The prompt builder is shared between blocking and streaming variants via `_build_chat_prompt` — don't fork the logic
- Add a test in `tests/test_local_ai_chat.py` for any new error class or output shape

### 3. Test locally

```bash
# One-time: install dev dependencies (pytest) on top of runtime deps
pip install -r requirements.txt -r requirements-dev.txt

# Run the full test suite (~5s, currently 269 tests)
pytest tests/

# Quick manual smoke
python -c "from src.parsers import load_genome; g,_,f = load_genome('sample/sample_genome.csv'); print(f'{len(g)} SNPs, {f}')"

# Run the dashboard end-to-end
python run.py
# Then upload sample/sample_genome.csv and verify your changes
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

# Contribuindo para o Gene Lens

Obrigado pelo interesse em contribuir! Este projeto aceita melhorias da comunidade, mas tem diretrizes rigorosas para proteger a privacidade dos usuarios e manter o rigor cientifico.

## Politica de Idioma

**Todas as Issues, Pull Requests, mensagens de commit e revisões de código devem ser em inglês.** Isso garante que a comunidade global possa participar. Comentários no código podem ser em inglês ou português.

---

## Critérios de Rejeição Imediata

Os seguintes itens serão rejeitados sem revisão:

- **Dados genéticos reais** em qualquer arquivo, commit ou comentário
- **Chamadas de rede durante análise** — o NetworkBlocker é uma garantia central
- **Linguagem diagnóstica** — "você tem", "você está em risco", "dose recomendada", "você deve tomar"
- **Módulos de Polygenic Risk Score (PRS)** — complexos, dependentes de etnia, enganosos com chips de consumo
- **Alterações no código de privacidade** (`src/privacy.py`, `src/consent.py`, `src/chat_store.py`, `download_databases.py`) sem discussão prévia em Issue

## O que Aceitamos

- Correções de bugs com casos de teste reproduzíveis
- Novos painéis de SNPs bem validados (com citações e qualidade de evidência)
- Melhorias de tradução (PT-BR / EN)
- Melhorias de UI/UX no dashboard
- Melhorias de documentação

## Como Contribuir

1. **Abra uma Issue primeiro** para discutir a abordagem
2. **Siga a arquitetura existente** (veja exemplos nos painéis de wellness)
3. **Teste localmente** com `sample/sample_genome.csv`
4. **Submeta um Pull Request** preenchendo o template completo
5. **Aguarde o CI passar** antes de solicitar revisão

### Para mudanças sensíveis à privacidade

Se você está editando `src/privacy.py`, `src/consent.py`, `src/chat_store.py` ou `download_databases.py`:

- Abra uma Issue primeiro pra discutir a mudança
- Atualize ou estenda o teste relevante (`tests/test_privacy.py`, `tests/test_chat_store.py`)
- Releia [SECURITY.md](SECURITY.md) e confirme que o modelo de ameaça continua válido
- Rode `python main.py privacy-check` depois da mudança

### Para o chat com IA (`src/local_ai.py`)

- Mantenha os system prompts (PT + EN) não-prescritivos — eles são a única coisa entre o modelo e uma resposta que soe como diagnóstico
- O construtor de prompt é compartilhado entre as variantes bloqueante e streaming via `_build_chat_prompt` — não duplique a lógica
- Adicione um teste em `tests/test_local_ai_chat.py` para qualquer nova classe de erro ou formato de saída

### Mantendo sua branch em sincronia (prefira rebase)

Quando a `main` avançar enquanto seu PR estiver aberto, **rebase** sua branch em cima da `main` em vez de mergear a `main` nela. Isso mantém o histórico do PR linear e o diff focado no que você efetivamente alterou:

```bash
git fetch origin
git rebase origin/main
git push --force-with-lease
```

Evite `git merge main` em uma branch de feature — cria merge commits que poluem o diff do PR com mudanças da `main` que você não fez.

Se você está colaborando com outra pessoa na mesma branch, combine antes de rebasear e sempre use `--force-with-lease` (nunca `--force`).

PRs são mergeados via squash na `main`, então commits individuais da sua branch não vão parar no histórico da `main` — pode commitar quantas vezes quiser enquanto trabalha.

## Diretrizes de Linguagem

Este projeto usa **linguagem exploratória**, não clínica/diagnóstica:

| NÃO use | Use em vez disso |
|---|---|
| "Você tem condição X" | "Variante associada a condição X detectada" |
| "Você está em risco de" | "Pode indicar predisposição a" |
| "Dose recomendada: 500mg" | "Literatura referencia doses de 400-800mg (discutir com médico)" |
| "Risco de doença" | "Exploração de variantes de doença" |
| "Interpretação clínica" | "Anotação baseada em referência" |

## Licenca

Ao contribuir, voce concorda que suas contribuicoes serao licenciadas sob a **MIT License**.
