# Security Policy

Gene Lens is a local-first tool that handles your own genetic data on your own machine. Security and privacy are the same conversation here — if something can leak data or be coerced into doing so, treat it as a security issue.

## Reporting a vulnerability

If you discover a vulnerability — especially one involving genetic data handling, privacy leakage, or NetworkBlocker bypass — please **do NOT open a public issue**.

Instead, report it privately through either:

1. **GitHub Security Advisories** — the "Report a vulnerability" button on the [Security tab](https://github.com/dimas-amendes/gene-lens/security). This is the preferred channel because it tracks the disclosure timeline and lets you collaborate on the fix in a private fork.
2. **Email** — the maintainer email listed on the [profile](https://github.com/dimas-amendes). Subject line: `[gene-lens security] <short description>`.

### What qualifies

- **NetworkBlocker bypass** — anything that causes data to be transmittable during analysis, including via subprocess, `os.system`, or dependency-level escape hatches.
- **Path traversal** — read/write outside the project's working directories from web routes (`/analyze`, `/history/load/<hid>`, `/api/chat/ask`, etc.).
- **Genotype or PII leakage** — through logs, error messages, generated reports, response metadata, or environment variables.
- **CSRF / cross-origin** — bypass of the `before_request` Origin/Referer check.
- **Unsanitized model output** — prompt injection that makes the AI chat exfiltrate context or execute embedded HTML/JS in the dashboard.
- **Insecure deletion** — uploaded files or chat transcripts left recoverable after the documented `secure_delete` / `clear()` calls.
- **Dependency vulnerabilities** with practical impact on this project's threat model (not every CVE qualifies — a CVE in Flask's debug toolbar doesn't matter for a tool that only listens on 127.0.0.1, for example).

### Response timeline

| Phase | Target |
|---|---|
| Acknowledgment of report | within 48 hours |
| First assessment + severity rating | within 7 days |
| Fix landed in `main` | depends on severity — critical issues block other work |
| Coordinated disclosure | once a fix ships, credit reporter unless anonymous is requested |

## Threat model

Gene Lens is **single-user, offline-first**. The security model assumes:

1. **The host machine is trusted.** If your machine has malware, no software-level guarantee survives. We don't protect against `dtrace`, kernel module exfil, screen recording, or memory inspection by another process running as the same user.
2. **The working directory is not cloud-synced.** Dropbox, OneDrive, iCloud, Google Drive sync folders are out of scope — files placed in `input/` or `output/` will be uploaded by *that software*, not by us. The README calls this out explicitly.
3. **Flask listens only on `127.0.0.1`.** If you front the dashboard with a tunnel (ngrok, tailscale, etc.) to make it reachable from elsewhere, that traffic path is your responsibility and outside our threat model.
4. **The user runs `download_databases.py` deliberately.** This is the only script that touches the network. Analysis paths assume the databases are already on disk.

The NetworkBlocker protects against accidental Python-level network calls during analysis. It does **not** protect against:

- Subprocesses started by future code (use `subprocess` carefully and audit each call against the analysis hot path)
- C extensions that bypass Python's socket layer
- OS-level networking from outside the Python process

If you find a way to coerce data out of the analysis hot path — even indirectly — that's in scope for this policy.

## Supported versions

The project is pre-1.0. Only `main` is supported; security fixes won't be backported to earlier commits because there are no released tags yet. After `v0.1.0` is cut, the most recent minor version will receive fixes.

| Version | Supported |
|---|:---:|
| `main` | yes |

## Hardening you can do today

Most of the safety floor is set up at install time. Quick checklist:

- Run `python main.py privacy-check` after every privacy-sensitive change you make to the repo.
- Keep the project directory **outside** any cloud-sync folder.
- Don't expose port `5000` past localhost. The Docker image's `compose` file binds `127.0.0.1:5000:5000` explicitly.
- Verify uploads are deleted: after an analysis finishes, `input/` should not contain your DNA file (`secure_delete` runs automatically; if it doesn't, that's a bug worth reporting).
- For the optional AI chat: only install Ollama models you trust. The chat function feeds your analysis context to the model — that's the whole point — but if you've installed a malicious model, it sees that data too. Pull from the official Ollama library only.
