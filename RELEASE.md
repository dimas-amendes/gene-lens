# Release Checklist — Gene Lens

Procedural checklist for cutting a release. The CHANGELOG documents *what*
shipped; this file documents *how* to ship it without breaking the privacy
promise or the local-only contract.

Work through the sections in order. Each item is a hard gate — don't tag
until everything checks.

---

## 1. Code health

- [ ] **Suite green**
  ```
  .venv/bin/python -m pytest tests/
  ```
  All tests passing, no `SKIPPED` / `XFAIL`. Current baseline: 228 tests, ~4s.
- [ ] **No stale `.pyc` / mixed Python versions**
  ```
  find . -name __pycache__ -type d -not -path "./.venv/*" -exec rm -rf {} +
  .venv/bin/python -m pytest tests/    # still green after cache rebuild
  ```
- [ ] **Import sanity**
  ```
  .venv/bin/python -c "import dashboard; import main"
  ```
  Surfaces NameErrors from i18n imports or stale `Lang` references that
  tests might not exercise.
- [ ] **`run.py --help` and `main.py --help`** both render without error.

## 2. Privacy & security audit

- [ ] **`python main.py privacy-check`** passes — confirms `.gitignore`
  excludes `input/`, `output/`, `history/`, `data/*.tsv`, `.genetics_consent`.
- [ ] **No genotype data outside `sample/`**:
  ```
  grep -rE "rs[0-9]+[,\t][0-9XYMT]+[,\t][0-9]+[,\t][AGCT]{1,2}" \
    --include="*.py" --include="*.txt" --include="*.csv" --include="*.json" \
    -- . | grep -v "^./sample/" | grep -v "^./.venv/" | grep -v "^./tests/"
  ```
  Must return nothing. If a fixture is needed, put it in `sample/` with the
  `# SYNTHETIC SAMPLE - NOT REAL GENETIC DATA` header.
- [ ] **No leaked secrets**:
  ```
  grep -rEn "api[_-]?key|secret|token|password" --include="*.py" \
    --include="*.html" -- . | grep -v "^./.venv/" | grep -v "test_"
  ```
  Inspect every hit — false positives are common (system prompt mentions
  "tokens"), but any real credential must be removed *and rotated*.
- [ ] **NetworkBlocker still thread-aware**:
  ```
  .venv/bin/python -m pytest tests/test_privacy.py::TestNetworkBlockerThreadIsolation -v
  ```
- [ ] **AI chat hits loopback only** (no accidental external call):
  ```
  .venv/bin/python -m pytest tests/test_local_ai_chat.py::TestChatAboutAnalysis::test_request_targets_local_ollama_loopback -v
  ```
- [ ] **Security headers stamped on every response**, including 403:
  ```
  .venv/bin/python -m pytest tests/test_dashboard_security.py::TestSecurityHeaders -v
  ```

## 3. i18n parity

- [ ] **STRINGS dict paridade** EN ↔ PT:
  ```
  .venv/bin/python -m pytest tests/test_i18n.py -v
  ```
- [ ] **Protocol dict paridade** (`_PROTOCOL_EN` / `_PROTOCOL_PT`):
  ```
  .venv/bin/python -m pytest tests/test_reports_protocols.py -v
  ```
- [ ] **Hereditary condition matrix integrity** (every condition bilingual):
  ```
  .venv/bin/python -m pytest tests/test_hereditary_conditions.py::test_every_condition_has_required_bilingual_fields -v
  ```
- [ ] **Manual smoke in both languages**: load sample, toggle EN↔PT, scroll
  every panel. No placeholder `{ keys }`, no `KeyError` flashes, no
  obviously machine-translated PT text in *hardcoded* dicts (Argos may
  translate dynamic ClinVar text — that's expected).

## 4. End-to-end smoke

Start clean:
```
rm -rf history/test-* input/test-* output/test-* 2>/dev/null
.venv/bin/python run.py --debug
```

Then in the browser:
- [ ] **Consent flow**: fresh `.genetics_consent` (`rm ~/.genetics_consent`)
  → `/` redirects through `/consent` → accept → lands on dashboard.
- [ ] **Try with sample** → loading page shows step progress → done →
  dashboard renders all panels (Health, Disease, Hereditary, Phenotype,
  Ancestry, Family Planning, Wellness).
- [ ] **`/report` route** renders the print-friendly version with no PT
  text leaked when in EN mode (or vice versa).
- [ ] **AI chat** (only if Ollama installed): ask a question, get a reply,
  check footer shows `model · time · tokens`. Stop button works mid-stream.
- [ ] **Settings page** correctly reports ClinVar, PharmGKB, Argos, Ollama
  presence. Install commands copy to clipboard.
- [ ] **History**: result appears in history list; click reloads it; delete
  removes the file (and only that file).

## 5. Docs sync

- [ ] **CHANGELOG.md**: move items from `[Unreleased]` into a new
  `[X.Y.Z] - YYYY-MM-DD` section. Group under `Added` / `Changed` /
  `Fixed` / `Removed` / `Security`.
- [ ] **README.md** screenshots current (if UI shifted): re-take the 4
  hero shots in EN dark mode, replace files under `assets/screenshots/`.
- [ ] **README.pt-BR.md** mirrors any structural changes in README.md.
- [ ] **CLAUDE.md** reflects any new architecture rules / file moves /
  decision rules introduced this cycle.
- [ ] **SECURITY.md** — confirm the disclosure email and the supported
  versions section still apply.

## 6. Version & git hygiene

- [ ] **Bump version** in `src/privacy.py:sanitize_report_metadata` (the
  `"version": "X.Y.Z"` literal) and anywhere else hardcoded
  (`grep -rn "version.*[0-9]\.[0-9]\.[0-9]" --include="*.py"`).
- [ ] **`git status` is clean** before tagging — every change accounted for.
- [ ] **No `.env`, `.genetics_consent`, `history/*.json`, `output/*` staged**
  (`git diff --cached --name-only`).
- [ ] **Commit msg style** matches existing log: `area: short subject`
  followed by body explaining *why*, not *what*.
- [ ] **Co-author line** present if Claude contributed:
  `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`

## 7. Tag & ship

- [ ] **Tag**: `git tag -s vX.Y.Z -m "vX.Y.Z"` (signed tag preferred; falls
  back to annotated if no GPG key configured).
- [ ] **Push**: `git push origin main && git push origin vX.Y.Z` —
  separately so the tag push fails loudly if main was rejected.
- [ ] **Verify fresh-clone works** end-to-end in a clean directory:
  ```
  cd /tmp && rm -rf gene-lens-fresh && git clone <repo> gene-lens-fresh
  cd gene-lens-fresh
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  python main.py download    # only if you can spare the bandwidth
  python run.py
  ```
  No errors, dashboard reachable. If anything fails here, the release is
  broken for first-time users — yank the tag and fix.

## 8. Post-release

- [ ] **`[Unreleased]` block** re-created at the top of CHANGELOG.md, empty
  but with the standard subsection headers ready.
- [ ] **Open issues** for anything that slipped: docs gaps, todos noted
  during smoke testing, deferred decisions.

---

## When to skip steps

This checklist is for *external* releases (tags users will install). For
internal pushes to `main` only sections 1-3 are mandatory; the rest can
wait for the next tag.

**Never skip section 2.** A privacy regression that ships, even to a
single user, is a privacy regression.
