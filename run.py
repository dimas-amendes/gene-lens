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

if __name__ == "__main__":
    debug = "--debug" in sys.argv or os.environ.get("GENE_LENS_DEBUG") == "1"
    run_dashboard(debug=debug)
