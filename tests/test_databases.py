"""
Tests for the ClinVar / PharmGKB loaders and the bilingual startup log helper.

The loaders feed the entire downstream analyzer — every disease/drug
finding flows through these dicts. A regression here silently mutates
every report.
"""
import csv
from pathlib import Path

import pytest

from src import databases
from src.databases import (
    _t,
    load_clinvar,
    load_pharmgkb,
    set_lang,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

CLINVAR_FIELDS = [
    "chrom", "pos", "ref", "alt", "symbol",
    "clinical_significance", "clinical_significance_ordered",
    "review_status", "gold_stars", "all_traits", "inheritance_modes",
    "hgvs_c", "hgvs_p", "molecular_consequence", "all_pmids", "xrefs",
    "age_of_onset", "prevalence", "all_submitters", "last_evaluated",
]


def _write_tsv(path: Path, fields: list, rows: list):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def _clinvar_row(**overrides):
    base = {
        "chrom": "1", "pos": "1000", "ref": "A", "alt": "G",
        "symbol": "BRCA1",
        "clinical_significance": "Pathogenic",
        "review_status": "criteria provided, multiple submitters",
        "gold_stars": "2",
        "all_traits": "Hereditary breast and ovarian cancer",
    }
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def reset_log_language():
    """Each test starts from the EN default so language state doesn't leak."""
    set_lang("en")
    yield
    set_lang("en")


# ── Bilingual log helper ──────────────────────────────────────────────────────

def test_set_lang_pt_changes_messages_to_portuguese():
    set_lang("pt")
    assert "Carregando" in _t("clinvar_loading", name="x.tsv")


def test_set_lang_en_returns_english_messages():
    set_lang("en")
    msg = _t("clinvar_loading", name="x.tsv")
    assert "Loading" in msg
    assert "x.tsv" in msg


def test_set_lang_accepts_pt_br_variant():
    """The CLI passes 'pt-BR' from argparse; the setter must normalize it."""
    set_lang("pt-BR")
    assert "Carregando" in _t("clinvar_loading", name="x.tsv")


def test_set_lang_unknown_code_falls_back_to_english():
    set_lang("xx")
    assert "Loading" in _t("clinvar_loading", name="x.tsv")


def test_set_lang_none_or_empty_does_not_crash():
    set_lang("")
    assert "Loading" in _t("clinvar_loading", name="x.tsv")
    set_lang(None)
    assert "Loading" in _t("clinvar_loading", name="x.tsv")


def test_t_unknown_key_returns_key_as_fallback():
    """Missing keys should fall back gracefully (key string), not KeyError."""
    assert _t("does_not_exist") == "does_not_exist"


def test_every_pt_key_exists_in_en_and_vice_versa():
    """If we add a PT message, we must add the EN one too — and vice versa.
    Catches half-translated additions."""
    pt = set(databases._MSGS["pt"].keys())
    en = set(databases._MSGS["en"].keys())
    assert pt == en, f"PT-only keys: {pt - en}; EN-only keys: {en - pt}"


# ── load_clinvar ──────────────────────────────────────────────────────────────

def test_load_clinvar_missing_file_returns_empty_dict(tmp_path: Path, capsys):
    out = load_clinvar(tmp_path / "does_not_exist.tsv")
    assert out == {}
    # Must log a [SKIP] message, not crash.
    assert "SKIP" in capsys.readouterr().out


def test_load_clinvar_builds_position_keyed_index(tmp_path: Path):
    tsv = tmp_path / "clinvar.tsv"
    _write_tsv(tsv, CLINVAR_FIELDS, [
        _clinvar_row(chrom="1", pos="1000", ref="A", alt="G", symbol="BRCA1"),
        _clinvar_row(chrom="17", pos="41245466", ref="C", alt="T", symbol="BRCA1"),
    ])
    index = load_clinvar(tsv)
    assert "1:1000" in index
    assert "17:41245466" in index
    assert index["1:1000"][0]["gene"] == "BRCA1"


def test_load_clinvar_filters_indels(tmp_path: Path):
    """ref/alt longer than 1 char = indel; skip to avoid false positives
    from consumer chips that mis-call indels."""
    tsv = tmp_path / "clinvar.tsv"
    _write_tsv(tsv, CLINVAR_FIELDS, [
        _clinvar_row(chrom="1", pos="1000", ref="A", alt="G"),     # SNP, keep
        _clinvar_row(chrom="1", pos="2000", ref="AT", alt="A"),    # deletion, drop
        _clinvar_row(chrom="1", pos="3000", ref="A", alt="ATG"),   # insertion, drop
        _clinvar_row(chrom="1", pos="4000", ref="", alt="A"),      # empty ref, drop
    ])
    index = load_clinvar(tsv)
    assert set(index.keys()) == {"1:1000"}, "only single-nucleotide variants must be indexed"


def test_load_clinvar_handles_same_position_with_multiple_alts(tmp_path: Path):
    """A position can have multiple alt alleles cataloged — both must be
    preserved in the list at that key."""
    tsv = tmp_path / "clinvar.tsv"
    _write_tsv(tsv, CLINVAR_FIELDS, [
        _clinvar_row(chrom="1", pos="1000", ref="A", alt="G", symbol="GENE1"),
        _clinvar_row(chrom="1", pos="1000", ref="A", alt="T", symbol="GENE1"),
    ])
    index = load_clinvar(tsv)
    assert len(index["1:1000"]) == 2
    alts = {e["alt"] for e in index["1:1000"]}
    assert alts == {"G", "T"}


def test_load_clinvar_returns_plain_dict_not_defaultdict(tmp_path: Path):
    """The loader uses defaultdict internally but must return a plain dict
    so callers don't accidentally create phantom entries on read."""
    from collections import defaultdict
    tsv = tmp_path / "clinvar.tsv"
    _write_tsv(tsv, CLINVAR_FIELDS, [_clinvar_row()])
    index = load_clinvar(tsv)
    assert not isinstance(index, defaultdict)
    # And confirm the no-phantom property directly:
    assert "nonexistent:0" not in index
    _ = index.get("nonexistent:0")
    assert "nonexistent:0" not in index


def test_load_clinvar_parses_gold_stars_as_int(tmp_path: Path):
    tsv = tmp_path / "clinvar.tsv"
    _write_tsv(tsv, CLINVAR_FIELDS, [
        _clinvar_row(pos="1", gold_stars="3"),
        _clinvar_row(pos="2", gold_stars=""),         # missing → 0
        _clinvar_row(pos="3", gold_stars="not_a_num"),  # garbage → 0
    ])
    index = load_clinvar(tsv)
    assert index["1:1"][0]["gold_stars"] == 3
    assert index["1:2"][0]["gold_stars"] == 0
    assert index["1:3"][0]["gold_stars"] == 0


def test_load_clinvar_carries_clinical_significance_through(tmp_path: Path):
    tsv = tmp_path / "clinvar.tsv"
    _write_tsv(tsv, CLINVAR_FIELDS, [
        _clinvar_row(clinical_significance="Likely pathogenic", all_traits="Lynch syndrome"),
    ])
    entry = load_clinvar(tsv)["1:1000"][0]
    assert entry["clinical_significance"] == "Likely pathogenic"
    assert entry["traits"] == "Lynch syndrome"


def test_load_clinvar_empty_file_with_only_header_returns_empty(tmp_path: Path):
    tsv = tmp_path / "clinvar.tsv"
    _write_tsv(tsv, CLINVAR_FIELDS, [])
    assert load_clinvar(tsv) == {}


def test_load_clinvar_logs_in_active_language(tmp_path: Path, capsys):
    set_lang("pt")
    tsv = tmp_path / "clinvar.tsv"
    _write_tsv(tsv, CLINVAR_FIELDS, [_clinvar_row()])
    load_clinvar(tsv)
    out = capsys.readouterr().out
    # PT prefix proves the language plumbing reaches the loader.
    assert "Carregando ClinVar" in out
    assert "carregadas" in out


# ── load_pharmgkb ─────────────────────────────────────────────────────────────

PHARMGKB_ANN_FIELDS = [
    "Clinical Annotation ID", "Variant/Haplotypes", "Gene",
    "Drug(s)", "Phenotype(s)", "Level of Evidence", "Phenotype Category",
]
PHARMGKB_ALLELE_FIELDS = [
    "Clinical Annotation ID", "Genotype/Allele", "Annotation Text",
]


def _write_pharmgkb_pair(tmp_path: Path, annotations, alleles):
    ann = tmp_path / "ann.tsv"
    alle = tmp_path / "alleles.tsv"
    _write_tsv(ann, PHARMGKB_ANN_FIELDS, annotations)
    _write_tsv(alle, PHARMGKB_ALLELE_FIELDS, alleles)
    return ann, alle


def test_load_pharmgkb_missing_file_returns_empty(tmp_path: Path, capsys):
    out = load_pharmgkb(
        annotations_path=tmp_path / "missing_ann.tsv",
        alleles_path=tmp_path / "missing_alleles.tsv",
    )
    assert out == {}
    assert "SKIP" in capsys.readouterr().out


def test_load_pharmgkb_joins_annotations_and_alleles_by_id(tmp_path: Path):
    ann, alle = _write_pharmgkb_pair(tmp_path,
        annotations=[{
            "Clinical Annotation ID": "CA1",
            "Variant/Haplotypes": "rs1799853",
            "Gene": "CYP2C9",
            "Drug(s)": "warfarin",
            "Phenotype(s)": "altered metabolism",
            "Level of Evidence": "1A",
            "Phenotype Category": "Dosage",
        }],
        alleles=[
            {"Clinical Annotation ID": "CA1", "Genotype/Allele": "AA",
             "Annotation Text": "reduced dose required"},
            {"Clinical Annotation ID": "CA1", "Genotype/Allele": "AG",
             "Annotation Text": "intermediate metabolizer"},
        ],
    )
    db = load_pharmgkb(ann, alle)
    assert "rs1799853" in db
    entry = db["rs1799853"]
    assert entry["gene"] == "CYP2C9"
    assert entry["drugs"] == "warfarin"
    assert entry["genotypes"]["AA"] == "reduced dose required"
    assert entry["genotypes"]["AG"] == "intermediate metabolizer"


def test_load_pharmgkb_ignores_non_rsid_variants(tmp_path: Path):
    """PharmGKB lists haplotypes like *CYP2C9*3 alongside rsIDs; the loader
    must only index variants that start with 'rs'."""
    ann, alle = _write_pharmgkb_pair(tmp_path,
        annotations=[
            {"Clinical Annotation ID": "CA1", "Variant/Haplotypes": "rs1799853", "Gene": "CYP2C9"},
            {"Clinical Annotation ID": "CA2", "Variant/Haplotypes": "CYP2C9*3", "Gene": "CYP2C9"},
        ],
        alleles=[
            {"Clinical Annotation ID": "CA1", "Genotype/Allele": "AA", "Annotation Text": "ok"},
            {"Clinical Annotation ID": "CA2", "Genotype/Allele": "*1/*3", "Annotation Text": "skip"},
        ],
    )
    db = load_pharmgkb(ann, alle)
    assert set(db.keys()) == {"rs1799853"}


def test_load_pharmgkb_drops_orphan_alleles(tmp_path: Path):
    """An allele row pointing at a missing annotation ID must be dropped, not crash."""
    ann, alle = _write_pharmgkb_pair(tmp_path,
        annotations=[
            {"Clinical Annotation ID": "CA1", "Variant/Haplotypes": "rs1", "Gene": "G1"},
        ],
        alleles=[
            {"Clinical Annotation ID": "CA1", "Genotype/Allele": "AA", "Annotation Text": "x"},
            {"Clinical Annotation ID": "CA_ORPHAN", "Genotype/Allele": "TT", "Annotation Text": "y"},
        ],
    )
    db = load_pharmgkb(ann, alle)
    assert "rs1" in db
    assert "AA" in db["rs1"]["genotypes"]
    assert len(db) == 1  # orphan was dropped


def test_load_pharmgkb_multiple_genotypes_aggregate_under_same_rsid(tmp_path: Path):
    ann, alle = _write_pharmgkb_pair(tmp_path,
        annotations=[
            {"Clinical Annotation ID": "CA1", "Variant/Haplotypes": "rs1", "Gene": "G1"},
        ],
        alleles=[
            {"Clinical Annotation ID": "CA1", "Genotype/Allele": "AA", "Annotation Text": "a"},
            {"Clinical Annotation ID": "CA1", "Genotype/Allele": "AG", "Annotation Text": "b"},
            {"Clinical Annotation ID": "CA1", "Genotype/Allele": "GG", "Annotation Text": "c"},
        ],
    )
    db = load_pharmgkb(ann, alle)
    assert set(db["rs1"]["genotypes"].keys()) == {"AA", "AG", "GG"}


def test_load_pharmgkb_logs_in_active_language(tmp_path: Path, capsys):
    set_lang("pt")
    ann, alle = _write_pharmgkb_pair(tmp_path,
        annotations=[{"Clinical Annotation ID": "CA1", "Variant/Haplotypes": "rs1", "Gene": "G"}],
        alleles=[{"Clinical Annotation ID": "CA1", "Genotype/Allele": "AA", "Annotation Text": "x"}],
    )
    load_pharmgkb(ann, alle)
    out = capsys.readouterr().out
    assert "Carregando anotações PharmGKB" in out
    assert "interações" in out
