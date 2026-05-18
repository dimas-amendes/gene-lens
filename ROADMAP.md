# Roadmap

The direction Gene Lens is heading, grouped by the milestone it'll land
in. This is a living document — items move between milestones as the
project learns from real use.

## v0.1.0 — first public release

The minimum bar for a tagged release.

- [x] Privacy-first analysis pipeline (NetworkBlocker + secure delete + local Flask)
- [x] Bilingual UI (EN + PT-BR) with full accent coverage
- [x] 14 wellness panels + sex-aware hereditary conditions + ancestry + phenotype
- [x] Local AI chat drawer (Ollama-backed) — optional, opt-in
- [x] Settings page with status-only component detection
- [x] Test suite (pytest, runs on Python 3.10/3.11/3.12)
- [x] CI: lint + tests + i18n parity + database-URL canary + secret scan
- [x] Docker + docker-compose for one-command run
- [ ] Screenshots in the README (upload screen, dashboard, findings, chat)
- [ ] Verified clean-machine setup walkthrough (one of each: macOS, Linux, Windows)
- [ ] Tagged release with notes pulled from CHANGELOG.md

## v0.2.0 — chat that feels native

Build the AI drawer into something users reach for, not a curiosity.

- [ ] Streaming responses — wire the existing `chat_about_analysis_stream` to the frontend with `fetch` + `ReadableStream`
- [ ] Markdown rendering in the assistant bubbles (CSS already in place)
- [ ] Inline rsID chips — assistant mentions `rs1234`, click scrolls to the finding
- [ ] Persistent chat per analysis via `chat_store` (load on drawer open, persist after each reply)
- [ ] Cancel-in-flight button while the model is generating
- [ ] Quick-action buttons on finding cards ("Ask AI about this finding")
- [ ] Token budget indicator in the drawer header ("3.2k / 8.2k tokens")

## v0.3.0 — accessibility + mobile

Make the dashboard usable on a phone and to assistive tech.

- [ ] Mobile-first layout pass — the dashboard breaks below ~768px today
- [ ] Keyboard navigation through tabs, accordions, and the drawer
- [ ] ARIA labels on the language switch, drawer controls, and dropzone
- [ ] Contrast audit (some grays don't reach WCAG AA on the dark theme)
- [ ] Cmd+K / Ctrl+K to open the chat drawer

## v0.4.0 — broader fidelity

Improvements that need careful design before they're built.

- [ ] Optional in-memory cache for repeated analyses (today every page load re-parses)
- [ ] Compare two analyses side by side (useful for family relatives)
- [ ] Export to printable PDF (today only Markdown reports)
- [ ] Carrier-screening expansion: opt-in extended panel for couples planning pregnancy, calibrated against ACMG carrier-screening recommendations
- [ ] More phenotype loci where evidence is strong (skin tone, height, lactose)

## Won't do (deliberate exclusions)

Items the project has decided against, to keep the scope honest:

- **Polygenic Risk Scores (PRS).** Ethnicity-dependent, prone to overinterpretation on consumer-chip data. The product's framing ("conversation starters, not answers") is incompatible with risk scores that quantify what they can't reliably measure.
- **Cloud / multi-user mode.** Goes against the core local-first promise. Anyone who wants a hosted version can fork — that's what MIT is for.
- **Telemetry of any kind.** Including "anonymous usage stats". The privacy floor stays at zero outbound network during analysis.
- **Prescriptive language.** Even when the literature supports a recommendation, the product never says "take X" or "you should". Phrasing is always exploratory.
- **Diagnostic claims.** Not a SaMD, not a medical device, will not pursue regulatory clearance — by design.
- **Cross-browser voice I/O (TTS/STT).** Web Speech API silently uses cloud providers in some browsers; conflicts with the offline guarantee.

---

To propose adding (or removing) something, open an Issue. Roadmap items
are not commitments — they're the current best guess at what would
improve the product.
