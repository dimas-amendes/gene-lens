#!/usr/bin/env python3
"""
Quick launcher — double-click or run `python run.py` to start the dashboard.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dashboard import run_dashboard

if __name__ == "__main__":
    run_dashboard()
