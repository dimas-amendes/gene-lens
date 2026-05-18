"""
Composite Risk Index (CRI).

This is the closest thing the project has to a polygenic risk score, but the
module is intentionally NOT a calibrated PRS — it's a transparent risk-allele
tally. These tests lock the contract that protects users from misreading it:

  - the score equals the number of risk-allele copies, no more no less
  - bands only kick in when there's enough coverage (≥3 SNPs called)
  - garbage genotypes (indels, single-char) never contribute to the score
  - the output is JSON-serializable, since dashboard history persists it
"""
import json

import pytest

from src.prs import PRS_PANELS, _count_risk_alleles, compute_prs


# ── Pure helper ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("genotype,risk_allele,expected", [
    ("AA", "A", 2),
    ("AT", "A", 1),
    ("TT", "A", 0),
    ("aa", "A", 2),  # case-insensitive
])
def test_counts_risk_allele_copies(genotype, risk_allele, expected):
    assert _count_risk_alleles(genotype, risk_allele) == expected


@pytest.mark.parametrize("garbage", ["", "A", "AAA", "DD", "II", "NN", None])
def test_garbage_genotypes_score_zero(garbage):
    """Indels and partial calls must never count — otherwise the tally is
    polluted by sequencing noise the user never opted into."""
    assert _count_risk_alleles(garbage, "A") == 0


# ── Panel-level behaviour ──────────────────────────────────────────────────

def test_empty_genome_yields_insufficient_bands():
    result = compute_prs({})
    assert result["panels"], "should always return every panel"
    for p in result["panels"]:
        assert p["band"] == "insufficient"
        assert p["score"] == 0


def test_full_risk_genome_gives_elevated_band():
    """If the user happens to be homozygous for the risk allele at every
    T2D SNP, the band must be 'elevated' — not 'average' or 'insufficient'."""
    t2d = PRS_PANELS["type2_diabetes"]
    genome = {
        rsid: {"genotype": risk * 2}
        for rsid, risk, *_ in t2d["snps"]
    }
    result = compute_prs(genome)
    t2d_result = next(p for p in result["panels"] if p["key"] == "type2_diabetes")
    assert t2d_result["snps_used"] == len(t2d["snps"])
    assert t2d_result["score"] == t2d_result["max_score"]
    assert t2d_result["band"] == "elevated"


def test_protective_genome_gives_below_average():
    t2d = PRS_PANELS["type2_diabetes"]
    # Use a non-risk allele at every locus — choose any base that isn't the
    # risk allele to guarantee zero copies.
    genome = {}
    for rsid, risk, *_ in t2d["snps"]:
        safe = "G" if risk != "G" else "C"
        genome[rsid] = {"genotype": safe * 2}
    result = compute_prs(genome)
    t2d_result = next(p for p in result["panels"] if p["key"] == "type2_diabetes")
    assert t2d_result["score"] == 0
    assert t2d_result["band"] == "below_average"


def test_two_snps_called_is_still_insufficient():
    """Bands require ≥3 SNPs called. Two is not enough to label a tendency —
    otherwise a chip that happens to include 2 risk-allele homozygotes
    would read as 'elevated' on noise alone."""
    t2d = PRS_PANELS["type2_diabetes"]
    rsid_a, risk_a, *_ = t2d["snps"][0]
    rsid_b, risk_b, *_ = t2d["snps"][1]
    genome = {
        rsid_a: {"genotype": risk_a * 2},
        rsid_b: {"genotype": risk_b * 2},
    }
    result = compute_prs(genome)
    t2d_result = next(p for p in result["panels"] if p["key"] == "type2_diabetes")
    assert t2d_result["snps_used"] == 2
    assert t2d_result["band"] == "insufficient"


def test_result_is_json_serializable():
    """History persistence dumps the whole result with json.dump."""
    result = compute_prs({"rs7903146": {"genotype": "TT"}})
    encoded = json.dumps(result)
    decoded = json.loads(encoded)
    assert {p["key"] for p in decoded["panels"]} == set(PRS_PANELS.keys())


def test_every_panel_has_at_least_five_snps():
    """A 1-2 SNP 'panel' would be misleading — the whole point of the module
    is to aggregate signal. Lock a floor so a future drive-by edit can't
    quietly shrink a panel below the band threshold."""
    for key, panel in PRS_PANELS.items():
        assert len(panel["snps"]) >= 5, f"{key} has too few SNPs"


def test_details_include_missing_snps():
    """The UI lists every SNP in a panel, even those absent from the chip,
    so the user can see what's missing. Pin that contract."""
    result = compute_prs({})
    t2d = next(p for p in result["panels"] if p["key"] == "type2_diabetes")
    assert len(t2d["details"]) == len(PRS_PANELS["type2_diabetes"]["snps"])
    assert all(d["present"] is False for d in t2d["details"])
