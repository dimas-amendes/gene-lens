#!/usr/bin/env python3
"""
Quick launcher — double-click or run `python run.py` to start the dashboard.

Pass --debug (or set GENE_LENS_DEBUG=1) to enable Flask's auto-reload on .py
and template changes. Off by default to keep the local server lean.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dashboard import run_dashboard


def _print_preflight() -> None:
    from config import CLINVAR_TSV, PHARMGKB_ANNOTATIONS, PHARMGKB_ALLELES
    clinvar = CLINVAR_TSV.exists()
    pharm = PHARMGKB_ANNOTATIONS.exists() and PHARMGKB_ALLELES.exists()
    if clinvar and pharm:
        return
    print("─" * 60)
    if not clinvar:
        print("  ⚠  ClinVar database NOT FOUND — analyses will be empty")
        print("     Run: python main.py download")
    if not pharm:
        print("  ⚠  PharmGKB database NOT FOUND — no drug-gene findings")
        print("     See /settings for instructions")
    print("─" * 60)


if __name__ == "__main__":
    debug = "--debug" in sys.argv or os.environ.get("GENE_LENS_DEBUG") == "1"
    _print_preflight()
    run_dashboard(debug=debug)
