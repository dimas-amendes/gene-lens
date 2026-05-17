#!/usr/bin/env python3
"""
Database downloader -- the ONLY script that accesses the network.

Downloads ClinVar and PharmGKB databases for local analysis.
Run this ONCE, then all analysis is 100% offline.

Usage:
    python download_databases.py              # Download all
    python download_databases.py --clinvar    # ClinVar only
    python download_databases.py --pharmgkb   # PharmGKB only

ClinVar: Free, no registration needed.
PharmGKB: Requires free account -- download manually if this fails.
"""
import argparse
import csv
import gzip
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.request import urlretrieve, Request, urlopen
from urllib.error import URLError

from config import DATA_DIR, CLINVAR_TSV, CLINVAR_GZ

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


def _progress_hook(block_num, block_size, total_size):
    """Simple download progress indicator."""
    if total_size > 0:
        downloaded = block_num * block_size
        pct = min(100, downloaded * 100 // total_size)
        mb = downloaded / (1024 * 1024)
        total_mb = total_size / (1024 * 1024)
        print(f"\r  [{pct:3d}%] {mb:.1f} / {total_mb:.1f} MB", end="", flush=True)


def download_clinvar():
    """Download ClinVar variant_summary.txt.gz and extract to filtered TSV.

    The raw file is ~120MB compressed, ~1GB uncompressed with 2.5M+ rows.
    We filter to only SNPs (ref/alt length 1) and write a compact TSV.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    url = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
    gz_path = DATA_DIR / "variant_summary.txt.gz"

    print(f"\n  Downloading ClinVar variant_summary.txt.gz...")
    print(f"  Source: {url}")
    print(f"  This file is ~120 MB -- may take a few minutes.\n")

    try:
        urlretrieve(url, str(gz_path), reporthook=_progress_hook)
        print()  # newline after progress
    except URLError as e:
        print(f"\n  [ERROR] Download failed: {e}")
        print("  Try downloading manually from:")
        print(f"    {url}")
        print(f"  And place the file at: {gz_path}")
        return False

    print("  Processing ClinVar into filtered TSV...")

    # Output columns we need
    out_columns = [
        "chrom", "pos", "ref", "alt", "start", "stop", "strand",
        "variation_type", "variation_id", "rcv", "scv", "allele_id",
        "symbol", "hgvs_c", "hgvs_p", "molecular_consequence",
        "clinical_significance", "clinical_significance_ordered",
        "pathogenic", "likely_pathogenic", "uncertain_significance",
        "likely_benign", "benign",
        "review_status", "review_status_ordered",
        "last_evaluated", "all_submitters", "submitters_ordered",
        "all_traits", "all_pmids", "inheritance_modes",
        "age_of_onset", "prevalence", "disease_mechanism",
        "origin", "xrefs", "dates_ordered", "gold_stars", "conflicted",
    ]

    # Column mapping from variant_summary.txt headers
    col_map = {
        "#AlleleID": "allele_id",
        "Type": "variation_type",
        "GeneSymbol": "symbol",
        "ClinicalSignificance": "clinical_significance",
        "ClinSigSimple": None,
        "RS# (dbSNP)": None,  # we build rsid from position
        "Assembly": None,  # filter column
        "Chromosome": "chrom",
        "Start": "pos",
        "Stop": "stop",
        "ReferenceAllele": "ref",
        "AlternateAllele": "alt",
        "ReviewStatus": "review_status",
        "NumberSubmitters": None,
        "PhenotypeList": "all_traits",
        "PhenotypeIDS": None,
        "RCVaccession": "rcv",
        "Origin": "origin",
        "VariationID": "variation_id",
        "Guidelines": None,
    }

    count = 0
    written = 0

    with gzip.open(str(gz_path), "rt", encoding="utf-8", errors="replace") as infile:
        reader = csv.DictReader(infile, delimiter="\t")

        with open(str(CLINVAR_TSV), "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_columns, delimiter="\t")
            writer.writeheader()

            for row in reader:
                count += 1
                if count % 500000 == 0:
                    print(f"    Processed {count:,} rows, kept {written:,}...")

                # Filter: only GRCh37 assembly (most consumer tests use this)
                assembly = row.get("Assembly", "")
                if assembly != "GRCh37":
                    continue

                ref = row.get("ReferenceAllele", "")
                alt = row.get("AlternateAllele", "")

                # Filter: only true SNPs
                if len(ref) != 1 or len(alt) != 1:
                    continue
                if ref == "na" or alt == "na":
                    continue

                # Build output row
                out_row = {
                    "chrom": row.get("Chromosome", ""),
                    "pos": row.get("Start", ""),
                    "ref": ref,
                    "alt": alt,
                    "start": row.get("Start", ""),
                    "stop": row.get("Stop", ""),
                    "strand": "+",
                    "variation_type": row.get("Type", ""),
                    "variation_id": row.get("VariationID", ""),
                    "rcv": row.get("RCVaccession", ""),
                    "scv": "",
                    "allele_id": row.get("#AlleleID", ""),
                    "symbol": row.get("GeneSymbol", ""),
                    "hgvs_c": "",
                    "hgvs_p": "",
                    "molecular_consequence": "",
                    "clinical_significance": row.get("ClinicalSignificance", ""),
                    "clinical_significance_ordered": row.get("ClinicalSignificance", "").lower(),
                    "pathogenic": "1" if "pathogenic" in row.get("ClinicalSignificance", "").lower() and "likely" not in row.get("ClinicalSignificance", "").lower() else "0",
                    "likely_pathogenic": "1" if "likely pathogenic" in row.get("ClinicalSignificance", "").lower() else "0",
                    "uncertain_significance": "1" if "uncertain" in row.get("ClinicalSignificance", "").lower() else "0",
                    "likely_benign": "1" if "likely benign" in row.get("ClinicalSignificance", "").lower() else "0",
                    "benign": "1" if row.get("ClinicalSignificance", "").lower().startswith("benign") else "0",
                    "review_status": row.get("ReviewStatus", ""),
                    "review_status_ordered": row.get("ReviewStatus", ""),
                    "last_evaluated": row.get("LastEvaluated", ""),
                    "all_submitters": row.get("SubmitterCategories", ""),
                    "submitters_ordered": "",
                    "all_traits": row.get("PhenotypeList", ""),
                    "all_pmids": "",
                    "inheritance_modes": "",
                    "age_of_onset": "",
                    "prevalence": "",
                    "disease_mechanism": "",
                    "origin": row.get("Origin", ""),
                    "xrefs": row.get("PhenotypeIDS", ""),
                    "dates_ordered": row.get("LastEvaluated", ""),
                    "gold_stars": _review_to_stars(row.get("ReviewStatus", "")),
                    "conflicted": "1" if "conflict" in row.get("ClinicalSignificance", "").lower() else "0",
                }
                writer.writerow(out_row)
                written += 1

    print(f"  Done: {count:,} total rows -> {written:,} SNPs written to {CLINVAR_TSV.name}")

    # Clean up raw download
    if gz_path.exists():
        gz_path.unlink()
        print(f"  Cleaned up: {gz_path.name}")

    return True


def _review_to_stars(review_status: str) -> int:
    """Convert ClinVar review status to gold stars (0-4)."""
    rs = review_status.lower()
    if "practice guideline" in rs:
        return 4
    if "expert panel" in rs:
        return 4
    if "multiple submitters" in rs and "no conflicts" in rs:
        return 3
    if "multiple submitters" in rs:
        return 2
    if "criteria provided" in rs:
        return 1
    return 0


def download_pharmgkb():
    """Provide instructions for PharmGKB download (requires free registration)."""
    print("\n  PharmGKB requires free registration for bulk downloads.")
    print()
    print("  Steps:")
    print("  1. Create free account at: https://www.pharmgkb.org/")
    print("  2. Go to: https://www.pharmgkb.org/downloads")
    print("  3. Download 'Clinical Annotations' zip file")
    print("  4. Extract these files to the data/ directory:")
    print(f"     - clinical_annotations.tsv -> {DATA_DIR}")
    print(f"     - clinical_ann_alleles.tsv -> {DATA_DIR}")
    print()

    # Check if files already exist
    ann = DATA_DIR / "clinical_annotations.tsv"
    alleles = DATA_DIR / "clinical_ann_alleles.tsv"
    if ann.exists() and alleles.exists():
        print("  [OK] PharmGKB files already present!")
        return True
    else:
        print("  [WAITING] Place the files in data/ and re-run to verify.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download reference databases for genetic analysis")
    parser.add_argument("--clinvar", action="store_true", help="Download ClinVar only")
    parser.add_argument("--pharmgkb", action="store_true", help="PharmGKB instructions only")
    args = parser.parse_args()

    print("=" * 60)
    print("  Genetic Database Downloader")
    print("  This is the ONLY script that accesses the network.")
    print("=" * 60)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not args.clinvar and not args.pharmgkb:
        # Download both
        download_clinvar()
        download_pharmgkb()
    elif args.clinvar:
        download_clinvar()
    elif args.pharmgkb:
        download_pharmgkb()

    print("\n" + "=" * 60)
    print("  After downloading, all analysis runs 100% OFFLINE.")
    print("  Your genetic data never leaves your machine.")
    print("=" * 60)


if __name__ == "__main__":
    main()
