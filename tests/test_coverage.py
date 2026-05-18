"""
Per-panel coverage report.

These tests pin two things:
1. The confidence-band math, so a UI built on top of it stays meaningful
   (a "high" badge has to mean ≥80% of markers actually present).
2. The result is fully JSON-serializable, because the dashboard persists
   every analysis to ~/history/*.json and a dataclass leak would crash
   reloads silently.
"""
import json

from src.coverage import APOE_SNPS, compute_coverage


def test_full_genome_yields_high_confidence():
    genome = {rsid: {"genotype": "AA"} for rsid in APOE_SNPS}
    cov = compute_coverage(genome)
    apoe = next(p for p in cov["panels"] if p["key"] == "apoe")
    assert apoe["present"] == 2
    assert apoe["total"] == 2
    assert apoe["confidence"] == "high"
    assert apoe["missing"] == []


def test_partial_apoe_is_flagged_partial():
    """APOE needs both SNPs to resolve an isoform — half coverage must
    not show up as 'high', otherwise users would trust an isoform call
    that was extrapolated from one marker."""
    genome = {"rs429358": {"genotype": "TT"}}
    cov = compute_coverage(genome)
    apoe = next(p for p in cov["panels"] if p["key"] == "apoe")
    assert apoe["present"] == 1
    assert apoe["confidence"] == "partial"  # 50% lands in partial band
    assert "rs7412" in apoe["missing"]


def test_empty_genome_marks_everything_low():
    cov = compute_coverage({})
    assert cov["summary"]["panels_high"] == 0
    assert cov["summary"]["markers_present"] == 0
    assert cov["summary"]["panels_low"] == cov["summary"]["panels_total"]


def test_summary_counts_match_per_panel_bands():
    cov = compute_coverage({})
    bands = {"high": 0, "partial": 0, "low": 0}
    for p in cov["panels"]:
        bands[p["confidence"]] += 1
    assert bands["high"] == cov["summary"]["panels_high"]
    assert bands["partial"] == cov["summary"]["panels_partial"]
    assert bands["low"] == cov["summary"]["panels_low"]


def test_result_is_json_serializable():
    # History persistence dumps the whole result with json.dump, so any
    # stray dataclass would crash silently when the user opens a past run.
    cov = compute_coverage({"rs429358": {"genotype": "TT"}})
    encoded = json.dumps(cov)
    decoded = json.loads(encoded)
    assert decoded["summary"]["markers_total"] == cov["summary"]["markers_total"]


def test_known_panels_present():
    """If someone renames a panel key, downstream templates referencing it
    (e.g. coverage_band_high) need to be updated. Lock the known set."""
    cov = compute_coverage({})
    keys = {p["key"] for p in cov["panels"]}
    must_have = {
        "apoe", "eye_color", "hair_color", "ancestry_aims",
        "pharmaco_curated", "wellness_nutri", "wellness_mental",
    }
    assert must_have.issubset(keys)


def test_missing_list_is_capped():
    """Wellness panels can have 10+ rsids — a panel with everything missing
    should still cap its 'missing' list so the UI doesn't render a wall of
    rsids. The summary count remains accurate via total - present."""
    cov = compute_coverage({})
    for p in cov["panels"]:
        assert len(p["missing"]) <= 10
