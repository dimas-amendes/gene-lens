# Changelog

All notable changes to Gene Lens are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project tries to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-07-02

### Added (desktop app & first-run setup)
- Double-click desktop bundles so non-technical users can run Gene Lens
  without installing Python: a macOS `Gene Lens.app`, a single-file
  Windows `GeneLens.exe`, and a console (Terminal) build for watching
  logs. Built with PyInstaller (`packaging/gene_lens.spec` plus
  `build_macos.sh` / `build_windows.bat`) and published automatically on
  a version tag by `.github/workflows/release.yml`.
- `app_launcher.py`: the packaged entry point. Asks the language (a
  native macOS dialog in `.app` mode, a terminal prompt otherwise),
  starts the local server, and opens the browser.
- Browser first-run setup page (`/setup`): pick which reference databases
  to download (ClinVar required, PharmGKB optional), each with a plain
  explanation, a progress bar, and a clear "this is the only step that
  uses the internet, everything after is 100% offline" notice. The home
  route gates to it until the core database is present.
- Automatic PharmGKB download (the public clinical-annotations archive,
  no login), with graceful degradation if it is unavailable.
- Manual database update check: a "Check for updates" button in Settings
  and `python main.py check-updates`. Metadata-only, never auto-downloads,
  and records source freshness (Last-Modified / ETag) in a `.db_meta.json`
  sidecar so it can tell you when ClinVar or PharmGKB has a newer version.
- New brand logo (a DNA helix inside a lens) as `static/img/logo.svg` and
  `logo-icon.svg`, wired into every page header, a favicon on all pages,
  and macOS/Windows app icons (`packaging/icon.icns`, `icon.ico`).
- App version shown in the setup and settings footers, stamped into the
  macOS bundle Info.plist, and used in the release asset names.
- Frozen-bundle path handling (`config.py`): databases, history, logs,
  and I/O are written to a per-user writable directory
  (`~/Library/Application Support/GeneLens`, `%APPDATA%\GeneLens`) instead
  of the read-only app folder.
- Tests for the PharmGKB download and update check
  (`tests/test_download_databases.py`) and the first-run setup flow and
  gate (`tests/test_setup_flow.py`).

### Added
- Per-analysis chat persistence (`src/chat_store.py`). Conversations
  survive closing the drawer and live under `history/<hid>/chat.json`
  with atomic writes and secure deletion.
- Streaming generator `chat_about_analysis_stream()` in `src/local_ai.py`
  so future UI can render tokens as Ollama produces them instead of
  waiting for the full reply.
- Token-budget estimation (`estimate_tokens`, `estimate_prompt_tokens`)
  for sizing prompts against the context window.
- Friendly error translation for common Ollama failures: missing model
  (with the exact `ollama pull` command), service not running, out of
  memory, plus a fallback that surfaces the raw stderr.
- Context-window guard in the chat prompt — caps the analysis payload
  at 20k characters and tells the model when content was omitted, so it
  won't fabricate details about the truncated portion.
- Suggested starter questions in the chat empty state (4 prompts, EN+PT).
- Animated three-dot typing indicator while the AI is responding.
- Markdown rendering CSS for assistant replies (lists, code, headers,
  inline code, bold/italic, rsID chip styling).
- 39 new pytest tests covering privacy, parsers, panels, system status,
  the chat function, the streaming generator, the persistence layer,
  and token estimation.

### Changed
- Renamed product from "Genetic Health Analyzer" / "Analisador Genético
  Local" to **Gene Lens** across UI, CLI banner, report metadata, README
  titles, CI workflow name, and the i18n strings.
- Replaced 10 emoji glyphs in `consent.html` and `dashboard.html` with
  Tabler Icons served locally (font + CSS in `static/`), keeping the
  dashboard 100% offline.
- Full diacritic pass on the Portuguese README and i18n strings — every
  `Configuracoes`, `Saude`, `NAO`, `Conclusoes` now properly accented.
- "Why I Built This" README section rewritten to reflect the real
  motivation (family history of inherited conditions, the Nick Saraev
  post, findings that matched prior diagnoses).
- Install instructions updated for PEP 668 (mandatory `python -m venv`
  on modern macOS/Linux), both EN and PT.
- License switched from AGPL v3 to MIT — permissive use, copyright
  notice retention only, no service-disclosure obligation.
- CI workflow renamed `Gene Lens CI`, now runs the pytest suite on
  Python 3.10 / 3.11 / 3.12 instead of inline `python -c` smoke tests,
  with a separate i18n parity step.
- Reduced top spacing on the consent and upload screens so the warning
  and the file picker sit above the fold on shorter viewports.

### Added (infrastructure)
- `pyproject.toml` with package metadata, classifiers, pinned core deps,
  and optional `translation` / `local-ai` / `dev` extras.
- `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1).
- `sample/README.md` documenting the synthetic-only policy.
- `.github/workflows/db-canary.yml` — weekly Sunday check that the
  ClinVar and PharmGKB URLs still resolve and the ClinVar header
  schema hasn't shifted, with auto-issue on failure.
- Gitleaks secret scan in CI (with the `fetch-depth: 0` fix so the
  PARENT..HEAD diff actually resolves).
- Sample-fixture marker check: every file in `sample/` must declare
  `SYNTHETIC` in its first 5 lines.
- Dependabot grouped pip + github-actions, with `ollama` and
  `argostranslate` ignored so optional extras don't generate weekly PRs.

### Security
- `_csrf_check` is now a `before_request` hook only; the buggy inline
  call inside `/api/chat/ask` that turned every valid POST into a 403
  was removed.
- `/api/check-updates` is POST-only so the global CSRF/Origin guard
  covers it. As a GET it could have been fired from any site open in the
  browser, triggering outbound pings to NCBI/PharmGKB and leaking the
  user's IP.
- First-run setup download errors return an opaque code to the browser;
  the detailed exception (which can include filesystem paths) stays in
  the local log only.
- The `GENE_LENS_DATA_HOME` override is resolved with `.resolve()` so a
  `..` path cannot redirect where databases and downloads are written.
