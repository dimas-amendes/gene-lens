"""
Smoke-level checks for the analysis pipeline on the synthetic fixture.

These guard against regressions where a module starts returning empty
findings or crashing on the sample data, which is the canary every
contributor runs locally.
"""
from pathlib import Path

import pytest

from src.parsers import load_genome
from src.phenotype import analyze_phenotype
from src.wellness_panels import ALL_PANELS, analyze_all_panels


@pytest.fixture(scope="module")
def loaded_sample_genome(sample_genome_path: Path):
    genome, meta, fmt = load_genome(sample_genome_path)
    return genome, meta, fmt


def test_sample_produces_active_panels(loaded_sample_genome):
    genome, _, _ = loaded_sample_genome
    panels = analyze_all_panels(genome)
    active = [k for k, v in panels.items() if v.get("findings")]
    # The fixture is engineered to light up most panels; assert a healthy floor.
    assert len(active) >= 8, f"only {len(active)} panels had findings: {active}"


def test_all_panel_keys_returned(loaded_sample_genome):
    genome, _, _ = loaded_sample_genome
    panels = analyze_all_panels(genome)
    assert set(panels.keys()) == set(ALL_PANELS.keys())


def test_phenotype_marker_count(loaded_sample_genome):
    genome, _, _ = loaded_sample_genome
    pheno = analyze_phenotype(genome)
    assert pheno.get("markers_found", 0) > 5
    assert "baldness" in pheno


def test_panel_findings_have_required_fields(loaded_sample_genome):
    """Every finding dict must carry the keys the dashboard renders."""
    genome, _, _ = loaded_sample_genome
    panels = analyze_all_panels(genome)
    for panel_key, panel in panels.items():
        for finding in panel.get("findings", []):
            assert "rsid" in finding, f"{panel_key}: finding missing rsid"
            assert finding["rsid"].startswith("rs")
