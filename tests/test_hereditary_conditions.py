"""
Tests for hereditary condition matching with sex-aware routing.

The matrix in src/hereditary_conditions.py is the most safety-critical surface
of the app: a regression here means a man could receive female-only HBOC
guidance (or vice-versa), or a sub-threshold variant could be surfaced as
"hereditary cancer detected". These tests lock the contract.
"""
import pytest

from src.hereditary_conditions import (
    HEREDITARY_CONDITIONS,
    _pick,
    analyze_hereditary_conditions,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _variant(gene: str, *, rsid: str = "rs0", stars: int = 2, genotype: str = "A/A"):
    """Build a minimal disease-finding dict that matches the analyzer's shape."""
    return {
        "gene": gene,
        "rsid": rsid,
        "user_genotype": genotype,
        "gold_stars": stars,
        "traits": "synthetic test trait",
        "zygosity_status": "heterozygous",
        "clinical_significance": "Pathogenic",
    }


def _findings(*pathogenic, risk=None, drug=None):
    return {
        "pathogenic": list(pathogenic),
        "likely_pathogenic": [],
        "risk_factor": list(risk or []),
        "drug_response": list(drug or []),
    }


# ── Empty / no-op cases ───────────────────────────────────────────────────────

def test_empty_findings_returns_empty_conditions_preserving_profile():
    out = analyze_hereditary_conditions({}, {"sex": "F", "sex_inferred": True}, lang="en")
    assert out["conditions"] == []
    assert out["sex"] == "F"
    assert out["sex_inferred"] is True
    assert out["lang"] == "en"


def test_findings_with_unmatched_genes_yield_no_conditions():
    out = analyze_hereditary_conditions(
        _findings(_variant("UNKNOWN_GENE_XYZ")),
        profile={"sex": "F"},
        lang="en",
    )
    assert out["conditions"] == []


def test_below_min_stars_is_filtered_out():
    # BRCA1 lives in HBOC with min_stars=1. A 0-star variant must be dropped.
    out = analyze_hereditary_conditions(
        _findings(_variant("BRCA1", stars=0)),
        profile={"sex": "F"},
        lang="en",
    )
    assert out["conditions"] == [], "0-star variants must not surface as hereditary conditions"


# ── Sex-aware routing ─────────────────────────────────────────────────────────

def test_female_with_hboc_gets_female_text_and_priority():
    out = analyze_hereditary_conditions(
        _findings(_variant("BRCA1", stars=2)),
        profile={"sex": "F"},
        lang="en",
    )
    cond = out["conditions"][0]
    assert cond["key"] == "hboc"
    assert cond["priority"] == HEREDITARY_CONDITIONS["hboc"]["priority_F"]
    # Female-specific text mentions ovarian cancer; male text does not.
    assert "ovarian" in cond["text"].lower()


def test_male_with_hboc_gets_male_text_and_priority():
    out = analyze_hereditary_conditions(
        _findings(_variant("BRCA2", stars=2)),
        profile={"sex": "M"},
        lang="en",
    )
    cond = out["conditions"][0]
    assert cond["key"] == "hboc"
    assert cond["priority"] == HEREDITARY_CONDITIONS["hboc"]["priority_M"]
    # Male HBOC text talks about prostate/pancreatic, never recommends mastectomy.
    text_low = cond["text"].lower()
    assert "prostate" in text_low
    assert "mastectomy" not in text_low


def test_female_and_male_hboc_texts_differ():
    """If they're the same string, sex-routing is broken — regression guard."""
    female = analyze_hereditary_conditions(
        _findings(_variant("BRCA1")), {"sex": "F"}, lang="en"
    )["conditions"][0]["text"]
    male = analyze_hereditary_conditions(
        _findings(_variant("BRCA1")), {"sex": "M"}, lang="en"
    )["conditions"][0]["text"]
    assert female != male


def test_unknown_sex_falls_back_to_neutral_text():
    out = analyze_hereditary_conditions(
        _findings(_variant("BRCA1")),
        profile={},  # no sex
        lang="en",
    )
    cond = out["conditions"][0]
    expected = HEREDITARY_CONDITIONS["hboc"]["text_neutral_en"]
    assert cond["text"] == expected
    # Neutral falls back to the more severe (lower-int) priority.
    assert cond["priority"] == min(
        HEREDITARY_CONDITIONS["hboc"]["priority_F"],
        HEREDITARY_CONDITIONS["hboc"]["priority_M"],
    )


def test_male_with_female_only_condition_falls_back_to_neutral():
    """Polyposis explicitly sets text_M=None — males must get neutral text,
    never a NoneType crash or female-only guidance."""
    out = analyze_hereditary_conditions(
        _findings(_variant("APC")),
        profile={"sex": "M"},
        lang="en",
    )
    cond = out["conditions"][0]
    assert cond["key"] == "polyposis"
    assert cond["text"] == HEREDITARY_CONDITIONS["polyposis"]["text_neutral_en"]
    assert cond["text"] is not None


# ── Localization ──────────────────────────────────────────────────────────────

def test_lang_en_returns_english_name_and_text():
    out = analyze_hereditary_conditions(
        _findings(_variant("BRCA1")), {"sex": "F"}, lang="en"
    )
    cond = out["conditions"][0]
    assert cond["name"] == HEREDITARY_CONDITIONS["hboc"]["name_en"]
    assert cond["evidence"] == HEREDITARY_CONDITIONS["hboc"]["evidence_en"]
    assert cond["confirm"] == HEREDITARY_CONDITIONS["hboc"]["confirm_en"]


def test_lang_pt_returns_portuguese_name_and_text():
    out = analyze_hereditary_conditions(
        _findings(_variant("BRCA1")), {"sex": "F"}, lang="pt"
    )
    cond = out["conditions"][0]
    assert cond["name"] == HEREDITARY_CONDITIONS["hboc"]["name_pt"]
    assert cond["evidence"] == HEREDITARY_CONDITIONS["hboc"]["evidence"]
    assert cond["confirm"] == HEREDITARY_CONDITIONS["hboc"]["confirm"]


def test_name_pt_and_name_en_both_present_in_output():
    """Downstream report code reads name_en / name_pt directly — both keys
    must be preserved regardless of the active language."""
    out = analyze_hereditary_conditions(
        _findings(_variant("BRCA1")), {"sex": "F"}, lang="en"
    )
    cond = out["conditions"][0]
    assert cond["name_en"] and cond["name_pt"]


def test_pick_falls_back_to_pt_when_en_variant_missing():
    item = {"foo": "valor pt", "foo_en": "value en", "bar": "so pt"}
    assert _pick(item, "foo", "en") == "value en"
    assert _pick(item, "foo", "pt") == "valor pt"
    # bar has no _en variant — must fall back to the PT field.
    assert _pick(item, "bar", "en") == "so pt"


# ── Sorting & multi-condition behavior ────────────────────────────────────────

def test_multiple_conditions_sorted_by_priority_ascending():
    """When several conditions match, output must be sorted by `priority`
    ascending (lower number = more clinically urgent)."""
    out = analyze_hereditary_conditions(
        _findings(
            _variant("HOXB13", rsid="rs_hox"),   # prostate, priority_M=1
            _variant("BRCA2", rsid="rs_brca"),   # hboc, priority_M=3
        ),
        profile={"sex": "M"},
        lang="en",
    )
    priorities = [c["priority"] for c in out["conditions"]]
    assert priorities == sorted(priorities)
    # prostate (1) must come before hboc (3) for a male.
    keys = [c["key"] for c in out["conditions"]]
    assert keys.index("prostate") < keys.index("hboc")


def test_risk_factor_and_drug_response_also_match_matrix():
    """F5/HFE-style variants live in risk_factor or drug_response buckets, not
    just `pathogenic`. The analyzer must still pull them into the matrix."""
    # F5 (Factor V Leiden) lives in the "thrombophilia" condition with
    # min_stars=1. Put it in risk_factor instead of pathogenic.
    out = analyze_hereditary_conditions(
        {"pathogenic": [], "likely_pathogenic": [],
         "risk_factor": [_variant("F5", stars=2)],
         "drug_response": []},
        profile={"sex": "F"},
        lang="en",
    )
    genes_surfaced = {g for c in out["conditions"] for g in c["genes_found"]}
    assert "F5" in genes_surfaced, "risk_factor variants must still feed the matrix"


def test_gene_details_carry_genotype_and_stars_through():
    out = analyze_hereditary_conditions(
        _findings(_variant("BRCA1", rsid="rs80357906", stars=3, genotype="A/G")),
        profile={"sex": "F"},
        lang="en",
    )
    detail = out["conditions"][0]["gene_details"][0]
    assert detail["gene"] == "BRCA1"
    assert detail["rsid"] == "rs80357906"
    assert detail["genotype"] == "A/G"
    assert detail["stars"] == 3


# ── Matrix integrity (catches typos in the dict itself) ───────────────────────

@pytest.mark.parametrize("key,cond", list(HEREDITARY_CONDITIONS.items()))
def test_every_condition_has_required_bilingual_fields(key, cond):
    """Every condition entry must carry both EN and PT variants for the
    user-facing fields, plus a min_stars threshold and a non-empty gene list."""
    required = [
        "name_pt", "name_en",
        "text_neutral", "text_neutral_en",
        "evidence", "evidence_en",
        "confirm", "confirm_en",
        "priority_F", "priority_M",
        "min_stars",
    ]
    for field in required:
        assert field in cond, f"{key}: missing field {field!r}"
        assert cond[field] not in (None, ""), f"{key}: field {field!r} is empty"
    assert cond["genes"], f"{key}: empty genes list"
    assert isinstance(cond["genes"], list)
    # Sex-specific text fields are optional (e.g. polyposis text_M=None) but
    # if PT variant exists, EN variant must exist too (and vice-versa).
    for base in ("text_F", "text_M"):
        pt_val = cond.get(base)
        en_val = cond.get(f"{base}_en")
        assert (pt_val is None) == (en_val is None), (
            f"{key}: {base} and {base}_en must both be set or both be None"
        )
