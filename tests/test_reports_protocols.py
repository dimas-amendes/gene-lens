"""
Tests for the bilingual protocol dictionaries used by src/reports.py.

`_PROTOCOL_EN` and `_PROTOCOL_PT` feed the supplement/diet/exercise/
monitoring report builders. The four `_build_*` functions select one or
the other via `lang` and pull strings by key — a key present in EN but
missing in PT silently produces `None` in the rendered report (or a
KeyError mid-render in worst case). Lock paridade explicitly.
"""
import re

import pytest

from src.reports import (
    _PROTOCOL_EN,
    _PROTOCOL_PT,
    _build_diet_recs,
    _build_exercise_recs,
    _build_monitoring,
    _build_supplement_list,
)


# ── Key-set parity ────────────────────────────────────────────────────────────

def test_protocol_en_and_pt_share_the_exact_same_key_set():
    en = set(_PROTOCOL_EN.keys())
    pt = set(_PROTOCOL_PT.keys())
    en_only = en - pt
    pt_only = pt - en
    assert not en_only, f"keys present in EN but missing in PT: {sorted(en_only)}"
    assert not pt_only, f"keys present in PT but missing in EN: {sorted(pt_only)}"


@pytest.mark.parametrize("d_name,d", [("_PROTOCOL_EN", _PROTOCOL_EN), ("_PROTOCOL_PT", _PROTOCOL_PT)])
def test_no_empty_string_values(d_name, d):
    empty = [k for k, v in d.items() if not str(v).strip()]
    assert not empty, f"{d_name} has empty values for keys: {empty}"


@pytest.mark.parametrize("d_name,d", [("_PROTOCOL_EN", _PROTOCOL_EN), ("_PROTOCOL_PT", _PROTOCOL_PT)])
def test_no_placeholder_todo_values(d_name, d):
    sentinels = ("TODO", "FIXME", "XXX", "...")
    bad = [(k, v) for k, v in d.items() if str(v).strip().upper() in sentinels]
    assert not bad, f"{d_name} has placeholder values: {bad}"


# ── Markdown emphasis stays in sync ──────────────────────────────────────────

def _bold_segments(s: str) -> list[str]:
    """Extract **bold** segments — they signal section headers in the
    report builders. EN/PT versions must use the same number of them so
    the rendered structure matches across languages."""
    return re.findall(r"\*\*([^*]+)\*\*", s)


def test_bold_marker_count_matches_across_languages():
    """If an EN string has two **headers** and PT only has one, the
    rendered report layout diverges between languages — and worse, the
    `f.write(f"### **{...}**")` paths in report builders may emit
    half-formatted lines."""
    mismatches = []
    for key in _PROTOCOL_EN:
        if key not in _PROTOCOL_PT:
            continue
        en_n = len(_bold_segments(_PROTOCOL_EN[key]))
        pt_n = len(_bold_segments(_PROTOCOL_PT[key]))
        if en_n != pt_n:
            mismatches.append({"key": key, "en_bold_count": en_n, "pt_bold_count": pt_n})
    assert not mismatches, f"bold-marker count diverges between languages: {mismatches}"


# ── Builders return localized strings end-to-end ──────────────────────────────

def _mthfr_finding() -> dict:
    """Minimal MTHFR finding that satisfies all four builders' shape
    requirements (`magnitude` for supplement + monitoring branches)."""
    return {"MTHFR": {"genotype": "TT", "magnitude": 3, "status": "reduced"}}


def test_supplement_builder_returns_english_when_lang_en():
    """Spot-check: the MTHFR rationale text should come from `_PROTOCOL_EN`
    when lang='en' — not from PT, and not blank."""
    fd = _mthfr_finding()
    out_en = _build_supplement_list(fd, lang="en")
    out_pt = _build_supplement_list(fd, lang="pt")
    assert out_en and out_pt, "supplement builder produced nothing for MTHFR"
    # The two outputs must differ — same key, different language.
    en_blob = " ".join(map(str, out_en))
    pt_blob = " ".join(map(str, out_pt))
    assert en_blob != pt_blob, "lang switch had no effect on supplement output"
    # And the EN output should contain the EN rationale literal.
    assert _PROTOCOL_EN["mthfr_folate"] in en_blob
    assert _PROTOCOL_PT["mthfr_folate"] in pt_blob


def test_diet_builder_swaps_language():
    fd = {"APOA2": {"genotype": "CC", "status": "sensitive"}}
    en = _build_diet_recs(fd, lang="en")
    pt = _build_diet_recs(fd, lang="pt")
    assert en and pt
    assert " ".join(map(str, en)) != " ".join(map(str, pt))


def test_exercise_builder_swaps_language():
    fd = {"ACTN3": {"genotype": "RR", "status": "power"}}
    en = _build_exercise_recs(fd, lang="en")
    pt = _build_exercise_recs(fd, lang="pt")
    assert en and pt
    assert " ".join(map(str, en)) != " ".join(map(str, pt))


def test_monitoring_builder_swaps_language():
    fd = _mthfr_finding()
    en = _build_monitoring(fd, disease_findings={}, lang="en")
    pt = _build_monitoring(fd, disease_findings={}, lang="pt")
    assert en and pt
    assert " ".join(map(str, en)) != " ".join(map(str, pt))


def test_builders_default_to_english_when_lang_omitted():
    """The default arg on every `_build_*` is `lang='en'`. Confirm both
    behaviors agree (default vs. explicit en)."""
    fd = _mthfr_finding()
    assert _build_supplement_list(fd) == _build_supplement_list(fd, lang="en")


def test_builders_unknown_lang_falls_back_to_english():
    """Defense-in-depth: a typo at the call site shouldn't blow up — the
    selector is `_PROTOCOL_PT if lang == "pt" else _PROTOCOL_EN`, so any
    non-'pt' value resolves to EN."""
    fd = _mthfr_finding()
    assert _build_supplement_list(fd, lang="xx") == _build_supplement_list(fd, lang="en")


def test_builders_return_empty_when_no_relevant_variants():
    """No matching variants → empty list (or list of empty items). The
    builders must not raise."""
    fd = {}
    for builder in (_build_supplement_list, _build_diet_recs, _build_exercise_recs):
        out = builder(fd, lang="en")
        assert isinstance(out, list)
    out = _build_monitoring(fd, disease_findings={}, lang="en")
    assert isinstance(out, list)
