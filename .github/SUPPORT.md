# Getting help with Gene Lens

Before opening an Issue, please check the channel that fits your question — most are routed faster elsewhere.

## I have a question about how to use the tool

Read the relevant section of the README:

- [Install + first run](../README.md#quick-start)
- [Privacy architecture](../README.md#privacy-architecture)
- [Supported file formats](../README.md#supported-formats)

If the answer isn't there, open a **GitHub Discussion** rather than an Issue. Issues are for bugs and feature requests, Discussions are for "how do I…?" or "is X supposed to work like…?". The Discussions tab is enabled on the repo settings.

## I found a bug

Open a [Bug Report](../.github/ISSUE_TEMPLATE/bug_report.md). Please:

- Reproduce it against `sample/sample_genome.csv` first if possible — that rules out file-format issues.
- Include your OS + Python version + the exact CLI / dashboard step that triggered it.
- **Do not paste real genetic data.** A synthetic SNP that reproduces the issue is enough.

## I want to suggest a feature

Open a [Feature Request](../.github/ISSUE_TEMPLATE/feature_request.md).

## I found a security vulnerability

Do **not** open a public Issue. Follow [SECURITY.md](../SECURITY.md) for the private disclosure channels and the expected timeline.

## I want to contribute code

Read [CONTRIBUTING.md](../CONTRIBUTING.md). It covers:

- Setting up the venv
- The architecture (where to add SNPs, panels, conditions)
- The wording rules (exploratory, never diagnostic)
- The PR checklist

## I have a medical question

This project does not provide medical advice and will not interpret your results for you. The right people for that are:

- A **medical geneticist** or **genetic counselor** — find one through [findageneticcounselor.nsgc.org](https://findageneticcounselor.nsgc.org).
- Your **primary care physician** can refer you to a specialist.
- For specific drug-gene interactions, your **pharmacist** can often help interpret PharmGKB-style findings.
