# Project Rules — Gene Lens

## Language & i18n (MANDATORY)

**EN is the source-of-truth language. PT-BR is the translation.** Every new user-facing string must be wired through the i18n layer at write-time — never hardcoded inline, never "I'll translate it later". Retrofitting i18n costs ~10x the original write and has burned us repeatedly (PT outliers in `snp_database.py`, `analyzer.py`, `GENE_CONTEXT`, wellness panels leaked into the EN-default product).

**Concretely, when you add a new string:**

- **UI label / button / error / table header** → add EN + PT entries to `STRINGS` in `src/i18n.py`, reference via `t["key"]` in the template. Never `{{ "Save" }}` in a Jinja file.
- **Domain data** (gene description, SNP text, hereditary condition, family-planning detail) → store EN as the **bare key** (`note`, `description`, `text`), PT under the same key + `_pt` suffix (`note_pt`). Accessor function (`get_gene_context(gene, lang)`, `_t(item, key, lang)`, etc.) resolves at call time.
- **AI prompts** → ship `SYSTEM_PROMPT_EN` and `SYSTEM_PROMPT_PT` as a pair in `src/local_ai.py`, switch by `language` arg.
- **New analysis function** that emits user-facing text → accept `lang: Lang` (from `src/i18n.py`), default `"en"`, branch internally on it.

**The `Lang` type.** `Lang = Literal["en", "pt"]` lives in `src/i18n.py` alongside `LANGS`, `DEFAULT_LANG = "en"`, and `normalize_lang(value)`. Use `lang: Lang` on every public signature that consumes language. At any untrusted boundary (URL segment, cookie, query param), coerce with `normalize_lang(raw)` — never compare against literals like `if lang == "pt"` before normalization.

**UI ordering.** EN-first everywhere — language toggles, dropdowns, dashboard headers: `EN | PT-BR`, in that order.

**Fallback direction.** If a PT translation is missing, fall back to EN. Never the inverse. If `translate_medical` (Argos neural EN→PT) is unavailable, show the EN source — graceful degradation.

**Definition of done.** A PR adding a new string is not done until both languages render correctly. CI doesn't enforce this — code review does. If you see a hardcoded literal in a PR diff, block it.

## Efficiency Rules

1. **i18n from the start** — see the dedicated section above; this is rule #1.

2. **Use background agents for large writes**: Translation files, large data dicts, and repetitive code generation should be delegated to background agents. Keep the main context for architecture decisions and integration.

3. **Test with `python -c` before restarting Flask**: Verify code compiles and functions work correctly via inline Python before killing/restarting the server. Avoid restart cycles for syntax errors.

4. **Batch related edits**: Group related changes (e.g., new panel + i18n strings + template update + sample genome SNPs) into a single focused operation instead of editing the same files across multiple rounds.

## Architecture Rules

- **Privacy first**: NetworkBlocker must wrap ALL analysis code. Translation runs inside the blocker.
- **No prescriptive language**: Use "associated with", "may indicate", "discuss with your physician" — never "you have", "you should take", "recommended dose".
- **Sex-aware routing**: Hereditary conditions use `text_F`, `text_M`, `text_neutral` variants. Profile is optional — sex can be inferred from Y chromosome.
- **Secure deletion**: Always use `secure_delete()` for genetic data files, never `unlink()`.
- **CSRF protection**: All POST routes are protected via Origin/Referer check in `_csrf_check()`.

## File Organization

- `dashboard.py` — Flask app, routes, conclusions builders, human conclusions (bilingual via `_HC` and `_TC` dicts)
- `src/wellness_panels.py` — 14 panels with PT text, EN translations in `src/wellness_i18n.py`
- `src/phenotype_i18n.py` — EN translations for phenotype + ancestry
- `src/hereditary_conditions.py` — Sex-aware condition matrix (15 conditions)
- `src/reports.py` — Protocol builders with `_PROTOCOL_PT` / `_PROTOCOL_EN` dicts

## Testing

- Always test with `sample/sample_genome.csv` (synthetic, 200+ SNPs)
- Verify both languages work after any text change
- Run `python main.py privacy-check` after touching privacy code

## Data classification (anti-leakage)

- **Tracked + safe**: `sample/*` (synthetic only; CI enforces "SYNTHETIC" header), `src/snp_database.py` and other `src/*.py` (public reference data: rsid+gene+description, no genotypes), reports/templates with no rsid+genotype pairs.
- **Tracked + forbidden**: any file outside `sample/` matching `rs[0-9]+[,\t][0-9XYMT]+[,\t][0-9]+[,\t][AGCT]{1,2}`. CI rejects.
- **Untracked (gitignored)**: `input/`, `output/`, `history/`, `data/*.tsv`, `*.log`, `.genetics_consent`. Never `git add -f` these.
- **Adding new fixtures**: put in `sample/`, prefix header `# SYNTHETIC SAMPLE - NOT REAL GENETIC DATA`, update `sample/README.md`.
