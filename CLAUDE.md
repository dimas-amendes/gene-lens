# Project Rules — Genetic Health Analyzer

## Efficiency Rules

1. **i18n from the start**: All user-facing text must be bilingual (EN/PT) from the moment it's written. Never add text in one language and translate later — it doubles the work and token cost.

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
