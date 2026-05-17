# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability — especially one involving genetic data handling, privacy leakage, or network blocking bypass — please **do NOT open a public Issue**.

Instead, report it privately:

1. **Email**: [maintainer email — add before publishing]
2. **GitHub Security Advisories**: Use the "Report a vulnerability" button on the Security tab

### What qualifies as a security issue

- NetworkBlocker bypass (data could leak during analysis)
- Path traversal or file access beyond intended directories
- Genetic data exposure through logs, error messages, or metadata
- Session hijacking or unauthorized access to analysis results
- Uploaded files not being securely deleted

### Response timeline

- **Acknowledgment**: within 48 hours
- **Assessment**: within 7 days
- **Fix**: as soon as possible, depending on severity

## Supported Versions

| Version | Supported |
|---------|:---------:|
| Latest  | Yes       |

## Scope

This project is designed for **local-first, offline use**. The security model assumes:

- The host machine is trusted
- The working directory is not cloud-synced
- Flask runs on `127.0.0.1` only (not exposed to network)

The NetworkBlocker protects against standard Python network calls during analysis but does **not** protect against malware, external subprocesses, or OS-level network access.
