"""
Tests for *chromosomal* sex inference from chromosome Y / X SNP counts.

This module feeds the sex-aware hereditary conditions matrix, so a regression
here cascades: a misidentified subject gets the wrong cancer screening guidance.

IMPORTANT — what we DON'T test here:
    Chromosomal sex is not clinical sex. Real edge cases (Klinefelter XXY,
    Turner X0, XY females with androgen insensitivity, XX males with SRY
    translocation, mosaicism) will be miscalled by this heuristic and
    that's a *known limitation*, not a bug to fix in this module — the
    expectation is that the user can override via profile. We pin the
    known miscall in `test_klinefelter_xxy_is_miscalled_as_male_doc` so a
    future fix is intentional, not accidental.
"""
import pytest

from src.sex_inference import infer_sex


def _g(chrom):
    """Build a single genotype-row dict at the shape infer_sex expects."""
    return {"chromosome": chrom, "position": "1", "genotype": "AA"}


def _genome(*, y=0, x=0, autosomal=0):
    """Build a genome_by_rsid dict with the requested counts per chromosome."""
    genome = {}
    for i in range(y):
        genome[f"rsY{i}"] = _g("Y")
    for i in range(x):
        genome[f"rsX{i}"] = _g("X")
    for i in range(autosomal):
        genome[f"rs{i}"] = _g("1")
    return genome


# ── Happy paths ───────────────────────────────────────────────────────────────

def test_returns_male_when_y_count_exceeds_threshold():
    # Real chips ship ~2000-4000 Y SNPs for males; default threshold is 50.
    assert infer_sex(_genome(y=2000, x=8000)) == "M"


def test_returns_female_when_y_absent_but_x_present():
    assert infer_sex(_genome(y=0, x=8000)) == "F"


def test_y_exactly_at_threshold_calls_male():
    """Boundary: y_count == threshold must return 'M' (the comparison is >=)."""
    assert infer_sex(_genome(y=50, x=100), threshold=50) == "M"


def test_y_one_below_threshold_calls_female_if_x_sufficient():
    assert infer_sex(_genome(y=49, x=100), threshold=50) == "F"


def test_custom_threshold_is_honored():
    # A stricter chip might need 500 Y SNPs before calling male.
    genome = _genome(y=100, x=1000)
    assert infer_sex(genome, threshold=500) == "F"
    assert infer_sex(genome, threshold=100) == "M"


# ── Edge cases & insufficient data ────────────────────────────────────────────

def test_empty_genome_returns_none():
    assert infer_sex({}) is None


def test_too_few_x_and_no_y_returns_none():
    """If we don't have at least 10 X SNPs and no Y, we can't reliably call.
    Common with toy fixtures or panels that omit sex chromosomes."""
    assert infer_sex(_genome(y=0, x=5)) is None


def test_x_at_minimum_required_for_female_call():
    # The implementation requires x_count >= 10 to confidently call female.
    assert infer_sex(_genome(y=0, x=10)) == "F"
    assert infer_sex(_genome(y=0, x=9)) is None


def test_only_autosomal_data_returns_none():
    """A panel with only autosomes (no X/Y at all) must NOT guess a sex."""
    assert infer_sex(_genome(autosomal=1000)) is None


# ── Chromosome label aliases ──────────────────────────────────────────────────

def test_numeric_chromosome_labels_are_recognized():
    """Some parsers emit '23' for X and '24' for Y instead of letters.
    Both encodings must yield the same answer."""
    by_letter = _genome(y=2000, x=8000)
    by_number = {}
    for i, (k, v) in enumerate(by_letter.items()):
        v = dict(v)
        if v["chromosome"] == "Y":
            v["chromosome"] = "24"
        elif v["chromosome"] == "X":
            v["chromosome"] = "23"
        by_number[k] = v
    assert infer_sex(by_letter) == infer_sex(by_number) == "M"


def test_mixed_numeric_and_letter_labels_in_same_genome():
    """Real-world genomes occasionally have a mix (e.g. converted files).
    Counts must aggregate across encodings, not split."""
    genome = {}
    # 25 Y as letter + 25 Y as number = 50 total → meets default threshold.
    for i in range(25):
        genome[f"rsYa{i}"] = _g("Y")
    for i in range(25):
        genome[f"rsYb{i}"] = _g("24")
    # X data to keep the function from being all-Y.
    for i in range(50):
        genome[f"rsXa{i}"] = _g("X")
    assert infer_sex(genome, threshold=50) == "M"


def test_chromosome_field_as_int_is_handled():
    """Some parsers store chromosome as int, not str — str(int) must still match."""
    genome = {f"rsY{i}": {"chromosome": 24, "position": "1", "genotype": "AA"} for i in range(100)}
    assert infer_sex(genome) == "M"


# ── Robustness ────────────────────────────────────────────────────────────────

def test_missing_chromosome_field_is_ignored_not_crash():
    """Rows without a chromosome key must be skipped, not raise KeyError."""
    genome = {"rs1": {"position": "1", "genotype": "AA"}}  # no chromosome
    # No usable data → None, not an exception.
    assert infer_sex(genome) is None


def test_unknown_chromosome_labels_are_ignored():
    """A 'MT' (mitochondrial) row must not be counted as X or Y."""
    genome = {f"rsMT{i}": _g("MT") for i in range(100)}
    assert infer_sex(genome) is None


def test_low_y_high_x_returns_female_not_none():
    """The classic female chip: a handful of Y stray reads + lots of X."""
    assert infer_sex(_genome(y=3, x=5000)) == "F"


# ── Known limitations (documented miscalls, not bugs to "fix" here) ───────────

def test_klinefelter_xxy_is_miscalled_as_male_doc():
    """Klinefelter (47,XXY) has both a full Y chromosome and an extra X.
    A pure chrom-Y-presence heuristic calls this 'M' — which is the
    chromosomal answer but may not match clinical sex.

    Pinned here so any future change to handle XXY explicitly (e.g. by
    looking at X copy number) is a *deliberate* upgrade, not accidental.
    Downstream code should honor user-provided `sex` over the inference."""
    klinefelter = _genome(y=2000, x=12000)  # ~1.5x typical X count
    assert infer_sex(klinefelter) == "M"


def test_xy_female_androgen_insensitivity_is_miscalled_doc():
    """Complete androgen insensitivity: 46,XY karyotype but female phenotype.
    The chromosomal call here is 'M' — clinical sex would be 'F'. Pinned
    as a known miscall; user must override via profile.sex."""
    cais = _genome(y=2000, x=8000)
    assert infer_sex(cais) == "M"
