# Gene Lens

> Read this in [Portuguese (PT-BR)](README.pt-BR.md).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![CI](https://github.com/dimas-amendes/gene-lens/actions/workflows/ci.yml/badge.svg)](https://github.com/dimas-amendes/gene-lens/actions/workflows/ci.yml)
[![Local First](https://img.shields.io/badge/Privacy-Local_First-brightgreen.svg)](#privacy-architecture)

**Local-first genetic exploration dashboard.** Designed for offline analysis of raw DNA data from consumer genotyping services (23andMe, AncestryDNA, MyHeritage, Genera/MeuDNA) against public reference databases (ClinVar, PharmGKB). Blocks standard Python network access during analysis and processes everything on your machine.

Built with Flask, Apache ECharts, Halfmoon CSS, and Geist font. Optional local AI via Ollama and neural translation via Argos Translate.

---

## Why this exists

Consumer genetic tests give you something polished but shallow. Eye color, caffeine tolerance, cilantro preference. The raw file underneath contains far more, and public reference databases like ClinVar and PharmGKB map those variants back to actual clinical literature. Most existing tools that bridge the two ship your DNA to someone else's cloud to do it.

Gene Lens is built so you can do that exploration without your DNA leaving your machine. Network access is blocked during analysis. No telemetry, no CDN, no external calls. Findings are framed as questions to bring to your doctor, never as diagnoses, because consumer chips have ~40% false positives for clinically significant variants.

If there are inherited conditions in your family, or you're just curious about what your raw data actually says, this tool exists for that.

---

## What This Project Is / Is Not

| This project IS | This project IS NOT |
|---|---|
| An educational exploration tool for consumer DNA raw data | A diagnostic tool or medical device (SaMD) |
| A way to generate discussion topics for your physician | A replacement for clinical genetic testing |
| A starting point for personal genomic curiosity | A confirmatory test, a negative result does not rule out risk |
| Open-source software with strong ethical disclaimers | A product that guarantees clinical accuracy |

---

> [!WARNING]
> **THIS SOFTWARE IS NOT A MEDICAL DEVICE (SaMD). IT IS NOT INTENDED TO DIAGNOSE, TREAT, CURE, OR PREVENT ANY DISEASE. FOR EDUCATIONAL AND SELF-KNOWLEDGE PURPOSES ONLY.**
>
> Consumer genotyping chips (used by 23andMe, Genera, AncestryDNA, etc.) have an approximately **40% false positive rate** for clinically significant variants (Tandy-Connor et al., *Genetics in Medicine*, 2018). This means nearly half of "pathogenic" findings from consumer tests are **wrong** when confirmed by clinical-grade sequencing.
>
> **NEVER change medications, diets, or treatments based on these results without consulting a physician.** The author/maintainer assumes **NO LIABILITY** for clinical decisions, psychological distress (anxiety induced by false positives), or any damages caused by the use of this software.
>
> For professional genetic counseling: [findageneticcounselor.nsgc.org](https://findageneticcounselor.nsgc.org)

---

## Features

- **Local-first privacy**. Standard Python network access is blocked (`socket` monkey-patched) during analysis. Designed so DNA data does not leave your machine. Uploaded files are securely overwritten after processing.
- **Interactive dashboard**. Dark-themed web UI with ECharts visualizations (charts, ancestry maps, variant tables), served locally on `127.0.0.1`. Zero CDN dependencies.
- **Pharmacogenomics**. Drug-gene interactions from PharmGKB/CPIC with evidence levels 1A/1B/2A/2B and reference-based annotation per gene.
- **Disease variant exploration**. Variant classification from ClinVar (pathogenic, likely pathogenic, risk factors, protective) with gold-star confidence ratings.
- **Sex-aware clinical routing**. Intelligent rendering of hereditary condition findings (HBOC/BRCA, Lynch, Prostate, Thrombophilia, Hemochromatosis, FH, Alpha-1 AT) conditioned on biological sex, matching the reporting approach of clinical-grade laboratories. Focuses on highly actionable monogenic conditions rather than noisy polygenic traits.
- **12 wellness panels**. Nutrition, fitness, skin, aging, sensory perception, sleep/chronobiology, longevity, mental health, food sensitivities, thyroid, eye health, and bone health.
- **Ancestry estimation**. Continental ancestry from 22 Ancestry Informative Markers (AIMs) with interactive world map.
- **Phenotype prediction**. Eye color, hair color, hair texture, freckling, androgenetic alopecia (HIrisPlex model + GWAS loci). Each prediction shows its genetic basis (contributing SNPs).
- **Family planning exploration**. Carrier-status exploration, gestational risk factors (MTHFR, F5, F2), X-linked conditions, dominant variant transmission.
- **Bilingual**. Full Portuguese (PT-BR) and English interface with neural medical translation (Argos Translate).
- **Humanized + technical views**. Plain-language summaries for self-exploration alongside detailed technical appendix for physician review.
- **Local AI interpretation**. Optional report interpretation via Ollama (Llama, Gemma, etc.).

---

## Screenshots

![Upload screen with profile fields and supported formats](assets/screenshots/01-landing.png)

*Upload your DNA file. Profile fields are all optional, sex can be inferred from the Y chromosome if you'd rather not specify.*

![Dashboard overview with KPI strip and analysis charts](assets/screenshots/02-dashboard.png)

*After analysis: top-of-page KPI strip plus six tabs covering Health & Risks, Medications, Wellness, Advanced Health, and Heritage. Charts use a single-hue palette so the data shape carries the signal, not the colors.*

![Local AI chat answering a pharmacogenomics question about medications](assets/screenshots/03-ai-chat.png)

*Local AI (Ollama) discussing the user's medication metabolism. Replies are grounded in the analysis, never prescriptive, and always point back to the doctor. Footer shows the model, wall-clock time, and token count, proof that nothing leaves the machine.*

![Print-friendly report with Save as PDF button](assets/screenshots/04-report.png)

*The `/report` view: print-first layout with `⌘P → Save as PDF` so you can hand a tidy document to your physician.*

---

## For non-technical users (no Python, no terminal)

You do not need to install Python or know any commands. Download one file, open
it, and use Gene Lens in your normal web browser.

**1. Download the file for your computer** from the
[Releases page](https://github.com/dimas-amendes/gene-lens/releases):

- **macOS** — `GeneLens-<version>-macOS.zip`
- **Windows** — `GeneLens-<version>-Windows.zip`

All downloads are `.zip` files. This is because a macOS app is really a folder
(a "bundle"), and a GitHub Release can only host single files, so it has to be
zipped; Windows is zipped too just to keep every download consistent.

**2. Open it.**

- **macOS** — double-click the zip to unzip it, then double-click **Gene Lens**.
- **Windows** — double-click the zip to unzip it, then double-click **GeneLens.exe**.

**3. First time only, get past the security warning** (the app is not paid-signed,
so the system is cautious):

- **macOS** — if it says *"can't be opened because it is from an unidentified
  developer"*, right-click (Control-click) **Gene Lens** and choose **Open**,
  then **Open** again. macOS remembers it after that.
- **Windows** — if you see *"Windows protected your PC"*, click **More info**,
  then **Run anyway**.

**4. Follow the setup.** It asks your language (English or Portuguese), then your
browser opens a **setup page** where you choose which reference databases to
download (ClinVar, required; PharmGKB, optional), each explained in plain words.
This one download is **the only time Gene Lens uses the internet**. After it
finishes, everything runs on your computer and nothing ever leaves it.

That is it. From then on you upload your raw DNA file and read your results, all
locally. Keep the little window (or the browser tab) open while you use it;
closing it stops the app.

Your reports and data are saved on your own machine, not inside the app:

- **macOS** — `~/Library/Application Support/GeneLens/`
- **Windows** — `%APPDATA%\GeneLens\`

> The app is a local web dashboard. The macOS/Windows file you downloaded is a
> small launcher that starts a server on your own computer and opens your browser
> at it, so the interface is the same everywhere. On macOS there is also a
> `GeneLens-<version>-Terminal-macOS.zip` if you prefer to run it from a terminal
> and watch the logs.

### Keeping the databases current

Downloads are one-time and the app stays fully offline afterward. To check for
newer reference data on your terms, open **Settings** in the app and click
**Check for updates** (or run `python main.py check-updates` from a source
checkout). It only compares dates; it never auto-downloads.

The optional AI chat (Ollama) and neural PT-BR translation are **not** bundled;
the app works without them and points you to install them if you want those
extras. See the optional sections below.

---

## Quick Start

> For developers, or to build the bundles yourself. End users can use the
> prebuilt download above instead.

### Prerequisites

- **Python 3.10, 3.11, or 3.12** (3.13+ may work but isn't covered by CI)
- ~500 MB disk space for reference databases

### 1. Clone and install

```bash
git clone https://github.com/dimas-amendes/gene-lens.git
cd gene-lens

# Create an isolated virtual environment (required on modern macOS/Linux
# because system Python refuses global installs — PEP 668).
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

> **Why a venv?** On macOS (Homebrew Python) and most Linux distros, `pip install` outside a venv fails with `externally-managed-environment`. Using `.venv` isolates the project's dependencies from your system Python.
>
> To leave the venv later: `deactivate`. To re-enter on a new shell session: `source .venv/bin/activate`.

### 2. Download reference databases (one-time, requires internet)

```bash
python main.py download
```

This downloads:
- **ClinVar** (~120 MB compressed), free, no registration ([NCBI FTP](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/))
- **PharmGKB**: requires a free account at [pharmgkb.org](https://www.pharmgkb.org/downloads). Download "Clinical Annotations" ZIP and extract to `data/`.

> **This is the only step that requires internet.** After database download, all analysis is designed for local-first, offline execution.

### 3. Start the dashboard

```bash
python run.py                    # Simplest — double-click on Windows
python main.py web               # Via CLI
python main.py web --port 8080   # Custom port
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

### 4. Test with sample data

A synthetic genome file is included for testing (no real DNA needed):

```bash
# Via dashboard: upload sample/sample_genome.csv in the web UI
# Via CLI:
python main.py analyze sample/sample_genome.csv --name "Sample"
```

### Optional: Neural translation (PT-BR)

```bash
pip install argostranslate
python main.py install-translator-model   # one-time ~100 MB download of the en->pt model
```

Only required if you want analyses in Portuguese. English analyses don't need it.

### Optional: Local AI interpretation

```bash
# Install Ollama: https://ollama.ai
ollama pull llama3.1:8b
python main.py analyze input/your_dna.txt --ai
```

### Build the desktop bundle yourself

The prebuilt downloads come from `packaging/`. To build locally (PyInstaller
must run on the target OS — no cross-compilation):

```bash
pip install -r requirements.txt -r requirements-dev.txt
bash packaging/build_macos.sh        # macOS  -> dist/GeneLens-macos.zip
packaging\build_windows.bat          # Windows -> dist/GeneLens-windows.zip
```

CI does this automatically on a version tag via `.github/workflows/release.yml`.

---

## How Findings Are Prioritized

The system uses a multi-layered evidence model to separate signal from noise:

| Layer | Source | What It Means |
|-------|--------|--------------|
| **ClinVar Review Status** (0-4 stars) | NCBI expert review | 4 stars = practice guideline; 1 star = single submitter; 0 = no assertion criteria |
| **Clinical Significance** | ClinVar classification | Pathogenic > Likely Pathogenic > Risk Factor > Uncertain > Benign |
| **PharmGKB/CPIC Evidence** | Clinical trials | Level 1A/1B = CPIC dosing guideline; Level 2A/2B = documented but no formal guideline |
| **Hereditary Condition Matrix** | Curated per-condition rules | Only monogenic, high-actionability conditions with sex-aware routing |

**All notable findings require clinical confirmation.** A finding flagged here is a reason to talk to your doctor, not a diagnosis.

---

## Known Limitations

1. **Consumer genotyping is not clinical sequencing.** Microarray chips test ~600K-2M pre-selected SNPs; clinical whole-exome/genome sequencing covers 20K+ genes comprehensively.
2. **Incomplete coverage of rare variants.** Most pathogenic mutations in genes like BRCA1/2 are private to families, chips may miss them entirely.
3. **Common diseases are polygenic and multifactorial.** This tool does not calculate Polygenic Risk Scores (PRS). Conditions like diabetes, hypertension, and depression involve hundreds of genes plus environment.
4. **Ancestry and phenotype are estimates.** Based on limited markers (~22 AIMs, ~16 pigmentation SNPs) and population-frequency models. Real ancestry is far more complex.
5. **Absence of a variant does not exclude risk.** The file may simply not contain the relevant SNP. A "clean" report does not mean zero genetic risk.

---

## Project Structure

```
genetic-health-analyzer/
├── run.py                  # Quick launcher (double-click)
├── main.py                 # CLI entry point
├── dashboard.py            # Flask web dashboard
├── download_databases.py   # Database downloader (only network access)
├── config.py               # Configuration and paths
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT
│
├── src/
│   ├── analyzer.py         # Lifestyle & disease analysis engine
│   ├── ancestry.py         # Continental ancestry (22 AIMs)
│   ├── consent.py          # Terms acceptance system
│   ├── databases.py        # ClinVar & PharmGKB loaders
│   ├── family_planning.py  # Carrier-status & gestational exploration
│   ├── hereditary_conditions.py  # Sex-aware clinical routing matrix
│   ├── i18n.py             # Internationalization (PT-BR / EN)
│   ├── local_ai.py         # Ollama integration (optional)
│   ├── parsers.py          # DNA file format parsers
│   ├── phenotype.py        # Appearance prediction (HIrisPlex + GWAS)
│   ├── privacy.py          # NetworkBlocker, secure delete
│   ├── reports.py          # Markdown report generation
│   ├── sex_inference.py    # Biological sex inference from Y chromosome
│   ├── snp_database.py     # Curated SNP database (~200 variants)
│   ├── translations.py     # Medical term translations
│   ├── translator.py       # Neural translation pipeline
│   └── wellness_panels.py  # 12 wellness panels (~80 SNPs)
│
├── templates/              # Jinja2 HTML templates
├── static/                 # Local assets (zero CDN)
├── sample/                 # Synthetic test data
├── data/                   # Reference databases (gitignored)
├── input/                  # User DNA files (gitignored)
└── output/                 # Generated reports (gitignored)
```

## How to get your raw DNA file

Gene Lens needs the raw genotyping file your testing service generated, not the polished report they show you in their app. Every major consumer service lets you download this for free, but the option is buried in account settings.

| Service | Where to find it | Wait time |
|---|---|:---:|
| **23andMe** | Account menu → **Browse Raw Data** → **Download Raw Data**. Re-enter your password to confirm. | Immediate |
| **AncestryDNA** | **Settings** → **DNA** tab → **Download Raw DNA Data**. Confirm via email link. | ~24 h |
| **MyHeritage** | **Settings** → **Manage DNA Kits** → ⋯ menu → **Download Raw Data**. | ~24 h |
| **Genera / MeuDNA** | Resultados → **Exportar dados brutos**. | Immediate |

**Important:**

- The file usually arrives as a `.zip`. **Unzip it** before uploading, Gene Lens reads the inner `.txt` or `.csv`, not the archive. (Files already gzipped as `.gz` are read transparently.)
- The download is your **private genetic data**. Don't email it, paste it into chat tools, or upload it to other services. Gene Lens never sends it anywhere, keep it that way.
- Some services email a confirmation link or require 2FA before releasing the file. That's the service protecting you; follow their flow.
- If your service isn't listed, the **Generic** format below works for any TSV/CSV that exposes RSID, Chromosome, Position, and Genotype columns.

Drop the unzipped file into the dashboard (drag-and-drop on `/`) or into `input/` and run `python main.py analyze input/your_dna.txt`.

## Supported Formats

| Service | Format | Auto-detected |
|---------|--------|:---:|
| 23andMe | 4-column TSV (rsid, chr, pos, genotype) | Yes |
| AncestryDNA | 5-column TSV (rsid, chr, pos, allele1, allele2) | Yes |
| MyHeritage | CSV with RSID, CHROMOSOME, POSITION, RESULT | Yes |
| Genera / MeuDNA | CSV with RSID, CHROMOSOME, POSITION, RESULT | Yes |
| Generic | TSV or CSV with identifiable RSID, Chromosome, Position, and Genotype/Result columns | Yes |

Compressed files (`.gz`) are supported transparently.

---

## Privacy Architecture

Designed for local-first, offline analysis after the initial database download.

**Protects against:**
- Accidental cloud upload during analysis (socket blocked)
- CDN data leakage (all assets served locally)
- Telemetry or tracking (zero external requests)
- Standard Python network calls during processing

**Does not protect against:**
- Malware already present on the host machine
- Cloud-synced folders (Dropbox, OneDrive, iCloud), ensure your working directory is not synced
- System backups that may capture genetic files
- External subprocesses that bypass Python's socket layer

**Technical measures:**
1. **Network Blocker**. `socket.socket` and `socket.getaddrinfo` are monkey-patched during analysis. Standard Python network calls raise `ConnectionError`.
2. **Secure Delete**. Uploaded DNA files are overwritten with random data before deletion.
3. **No Metadata**. Reports contain no system-identifying information (no hostname, username, or file paths).
4. **Local Only**. Flask binds exclusively to `127.0.0.1`. Not accessible from other machines.
5. **No Telemetry**. Zero analytics, tracking, or external requests.

Verify your setup: `python main.py privacy-check`

---

## Data Attribution

- **ClinVar**. NCBI, National Library of Medicine. Landrum MJ, et al. *Nucleic Acids Research*, 2020. [ncbi.nlm.nih.gov/clinvar](https://www.ncbi.nlm.nih.gov/clinvar/)
- **PharmGKB**. Stanford University, NIH/NIGMS. Whirl-Carrillo M, et al. *Clinical Pharmacology & Therapeutics*, 2021. [pharmgkb.org](https://www.pharmgkb.org/)
- **CPIC**. Clinical Pharmacogenetics Implementation Consortium. Relling MV, Klein TE. *Clinical Pharmacology & Therapeutics*, 2011. [cpicpgx.org](https://cpicpgx.org/)
- **HIrisPlex**. Walsh S, et al. *Forensic Science International: Genetics*, 2013.

---

## License

Licensed under the **MIT License**.

You may freely use, copy, modify, merge, publish, distribute, sublicense, and sell copies of this software, including for commercial purposes, provided that the copyright notice and permission notice are retained.

See [LICENSE](LICENSE) for the full text.

---

## Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. **Ensure no personal/genetic data is included** in commits
4. Submit a Pull Request

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Acknowledgments

Inspired by the bioinformatics exploration approach demonstrated by [Nick Saraev](https://www.youtube.com/@nicksaraev). While the original concept provided the spark, this project was entirely rewritten with a focus on local-first execution, permissive MIT licensing, strict ethical disclaimers, sex-aware clinical routing, and accessibility for non-technical users.

---

*Built with care for privacy and scientific rigor. Your DNA is yours alone.*
