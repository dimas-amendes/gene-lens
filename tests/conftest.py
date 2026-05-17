"""
Shared pytest fixtures for the Gene Lens test suite.

Makes sure tests can find the top-level modules (config, dashboard, src/*)
without needing the package to be installed.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def sample_genome_path() -> Path:
    """Path to the synthetic genome fixture shipped with the repo."""
    return ROOT / "sample" / "sample_genome.csv"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT
