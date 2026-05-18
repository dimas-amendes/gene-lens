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

**Decision rule — where does a new string live?** Before reflexively adding `field` + `field_en` to a data dict, pick the right channel:

| Kind of text | Channel | Why |
|---|---|---|
| UI label, button, error, table header, status phrase | `STRINGS` in `src/i18n.py`, referenced via `t["key"]` in templates | Single source of truth, no duplication across templates |
| Clinically sensitive long-form text (hereditary condition narrative, family-planning guidance, prescriptive-language-adjacent copy) | **Hardcoded EN + PT pair** in the domain dict (`text_F`/`text_F_en`, `condition_pt`/`condition_en`) | Neural translation can shift medical meaning ("mastectomy profilática" → "preventive mastectomy" is fine; subtler clinical idioms aren't) |
| Short trait/category labels ("Eye color", "Skin pigmentation") | Either `STRINGS` or hardcoded pair — caller's call | Low risk either way; prefer `STRINGS` if reused in multiple places |
| Dynamic clinical annotations from external corpora (ClinVar significance text, PharmGKB drug notes, gene descriptions ingested in bulk) | **Argos neural EN→PT at runtime** via `src/translator.py` | Corpus too large to hardcode; manual translation doesn't scale |
| AI system prompts | `SYSTEM_PROMPT_EN` + `SYSTEM_PROMPT_PT` pair in `src/local_ai.py` | Prompt engineering is fragile; an Argos retranslation could break instruction following |

**Default for new code**: if the text is shorter than a sentence, lives in a `STRINGS`-able UI surface, or could be reused → `src/i18n.py`. If it's domain data with safety implications → hardcoded EN+PT. If it's coming from an external feed → Argos. Only invent a new `_en`/`_pt` pair on a dict when none of the above fit.

**Definition of done.** A PR adding a new string is not done until both languages render correctly. CI doesn't enforce this — code review does. If you see a hardcoded literal in a PR diff, block it.

## Efficiency Rules

1. **i18n from the start** — see the dedicated section above; this is rule #1.

2. **Use background agents for large writes**: Translation files, large data dicts, and repetitive code generation should be delegated to background agents. Keep the main context for architecture decisions and integration.

3. **Test with `python -c` before restarting Flask**: Verify code compiles and functions work correctly via inline Python before killing/restarting the server. Avoid restart cycles for syntax errors.

4. **Batch related edits**: Group related changes (e.g., new panel + i18n strings + template update + sample genome SNPs) into a single focused operation instead of editing the same files across multiple rounds.

## Architecture Rules

- **Privacy first**: `NetworkBlocker` must wrap ALL analysis code. Translation runs inside the blocker.
- **NetworkBlocker is THREAD-LOCAL** (since the gray-screen-loading bug): the monkey-patch of `socket.socket` / `getaddrinfo` is installed globally but only RAISES on threads inside `with NetworkBlocker():`. Other threads (Flask serving static assets, Argos translator install) keep networking normally. Do NOT call `NetworkBlocker` from a Flask request handler — only from background analysis threads. Nesting is supported via a per-thread depth counter; inner `__exit__` does not unblock the outer scope. Regression locked by `tests/test_privacy.py::TestNetworkBlockerThreadIsolation`.
- **AI chat hits local Ollama via HTTP loopback only**: `chat_about_analysis` posts to `http://127.0.0.1:11434/api/chat` (NOT `ollama run` subprocess). The CLI rendering was soft-wrapping mid-word and truncating PT replies. HTTP gives us deterministic `num_predict` / `num_ctx`. Privacy posture identical (same daemon, pure loopback). Locked by `test_request_targets_local_ollama_loopback`. Streaming (`chat_about_analysis_stream`) still uses subprocess; migrate only if it surfaces in the UI path.
- **No prescriptive language**: Use "associated with", "may indicate", "discuss with your physician" — never "you have", "you should take", "recommended dose".
- **Sex-aware routing is CHROMOSOMAL, not clinical**: `infer_sex()` counts chromosome Y SNPs and emits `M` / `F` / `None`. Known miscalls: Klinefelter (XXY), Turner (X0), complete androgen insensitivity (XY female), XX male (SRY translocation), mosaicism. Downstream code MUST honor `profile.get("sex")` over the inferred value when both exist (this is already wired in `analyze_hereditary_conditions`). Hereditary conditions use `text_F`, `text_M`, `text_neutral` variants — when no sex is known, fall back to `text_neutral`, never guess. If a condition has `text_M=None` (e.g. polyposis, mostly studied in women), the matcher must fall back to neutral text, not crash on `None`.
- **Hereditary condition matrix integrity**: every entry in `HEREDITARY_CONDITIONS` must have **both** PT and EN variants for `name`, `text_neutral`, `evidence`, `confirm`. Sex-specific text fields (`text_F` / `text_M`) are optional but, if PT is set, EN must be set too (and vice-versa). Locked by parametrized test in `tests/test_hereditary_conditions.py`.
- **Secure deletion**: Always use `secure_delete()` for genetic data files, never `unlink()`.
- **CSRF protection**: All POST routes are protected via Origin/Referer check in `_csrf_check()`.

## Console & log language

- `python main.py web` boots in EN by default. `--lang pt` (or `pt-BR`) switches startup banner, DB loader messages, and the initial dashboard language until the user's cookie overrides.
- DB loader messages go through `src.databases.set_lang(code)` + `_t(key)`. Both `_MSGS["en"]` and `_MSGS["pt"]` must carry the same key set — paridade enforced by `test_every_pt_key_exists_in_en_and_vice_versa`.
- The startup banner title is `"Dashboard Gene Lens"` in both languages.

## File Organization

- `dashboard.py` — Flask app, routes, conclusions builders, human conclusions (bilingual via `_HC` and `_TC` dicts). `run_dashboard(port, lang)` is the public entrypoint called from `main.py`.
- `src/wellness_panels.py` — 14 panels with PT text, EN translations in `src/wellness_i18n.py`
- `src/phenotype_i18n.py` — EN translations for phenotype + ancestry
- `src/hereditary_conditions.py` — Sex-aware condition matrix (15 conditions). `analyze_hereditary_conditions(disease_findings, profile, lang)` is the only consumer; matrix entries follow strict bilingual schema.
- `src/sex_inference.py` — `infer_sex(genome_by_rsid, threshold=50)` → `M` / `F` / `None`. Chromosomal heuristic only; honor `profile.sex` over it.
- `src/local_ai.py` — `chat_about_analysis` (blocking, HTTP), `chat_about_analysis_stream` (streaming, subprocess), `_build_chat_messages` (single source of truth for the Ollama `messages` array).
- `src/privacy.py` — `NetworkBlocker` (thread-local), `secure_delete`, `sanitize_report_metadata`.
- `src/databases.py` — `load_clinvar`, `load_pharmgkb`, `set_lang` for console messages.
- `src/reports.py` — Protocol builders with `_PROTOCOL_PT` / `_PROTOCOL_EN` dicts

## Testing

- **Run the suite**: `.venv/bin/python -m pytest tests/` (~4s, 228 tests at last count). System `python` is missing Flask — always use the venv.

### Severity classification (use when prioritizing test gaps)

When deciding what to test first, classify by what a regression *actually causes*. Same framework we used to triage the original test backlog:

- 🔴 **Critical** — regression causes a safety/clinical/privacy harm.
  Examples: hereditary-condition sex routing (man receives BRCA female-only guidance), `NetworkBlocker` (data leak during analysis, or the gray-screen loading bug). Must have tests *and* the test must fail before the fix lands.
- 🟠 **High** — regression silently corrupts analysis output or core data path.
  Examples: `databases` loaders (mutates every report), `sex_inference` (cascades into the hereditary matrix), `local_ai._build_chat_messages` (system prompt / role sanitization). Should have tests; bug here is hard to spot without them.
- 🟡 **Medium** — regression degrades UX or content, but doesn't break correctness.
  Examples: i18n parity (missing label = blank UI element), bilingual protocol dicts (report section without header). Tests are valuable as drift guards, not urgent.

When triaging: hit reds first, then oranges, then yellows. Don't write yellow tests when red gaps exist.
- **Manual smoke**: `sample/sample_genome.csv` (synthetic, 200+ SNPs) through the dashboard. Verify both languages render after any text change.
- **Privacy guarantee**: `python main.py privacy-check` after touching `src/privacy.py` or anything that runs inside `NetworkBlocker`.
- **Don't hit the network in tests.** AI chat tests mock `urllib.request.urlopen`; streaming tests mock `subprocess.Popen`; DB loader tests write synthetic TSVs to `tmp_path`. A test that times out for 80+ seconds is almost certainly trying to reach a real Ollama daemon — fix the mock.
- **When to add a test (the bar):**
  - Sex-aware routing change in `hereditary_conditions.py` → extend `tests/test_hereditary_conditions.py`.
  - New condition added to the matrix → the parametrized integrity test catches missing bilingual fields automatically.
  - New i18n key in `databases._MSGS` → paridade test catches half-translations automatically.
  - Fix for a user-reported bug → write the regression test FIRST, watch it fail, then fix.
  - New public function in `src/local_ai.py`, `src/privacy.py`, `src/hereditary_conditions.py`, `src/sex_inference.py`, `src/databases.py` → must ship with tests in the matching `tests/test_*.py`.

## Data classification (anti-leakage)

- **Tracked + safe**: `sample/*` (synthetic only; CI enforces "SYNTHETIC" header), `src/snp_database.py` and other `src/*.py` (public reference data: rsid+gene+description, no genotypes), reports/templates with no rsid+genotype pairs.
- **Tracked + forbidden**: any file outside `sample/` matching `rs[0-9]+[,\t][0-9XYMT]+[,\t][0-9]+[,\t][AGCT]{1,2}`. CI rejects.
- **Untracked (gitignored)**: `input/`, `output/`, `history/`, `data/*.tsv`, `*.log`, `.genetics_consent`. Never `git add -f` these.
- **Adding new fixtures**: put in `sample/`, prefix header `# SYNTHETIC SAMPLE - NOT REAL GENETIC DATA`, update `sample/README.md`.
