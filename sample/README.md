# sample/

This directory contains **synthetic test fixtures only**. No real human genome data lives here, ever.

## Files

- `sample_genome.csv` — 51 fictional SNPs in 23andMe-style CSV format, designed to exercise every analysis module. First line is always `# SYNTHETIC SAMPLE - NOT REAL GENETIC DATA`.

## Rules

1. **Any file added here MUST contain `SYNTHETIC` in its first 5 lines.** CI enforces this.
2. **Never paste a real consumer-genomics export here.** Real exports go in `input/` (gitignored).
3. **Never commit data derived from a real run** (history, output, logs) — `.gitignore` covers `history/`, `output/`, `*.log`.

## Why CSV with rsids is safe here

The combination `rsid,chr,pos,genotype` looks like real genome shape, which is why CI scans all repo files for that pattern and rejects matches outside `sample/`. Files here are explicitly whitelisted *because* the header marks them as fictional.
