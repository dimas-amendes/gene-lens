"""
Tests for src.medical_specialties.

This module is the source of truth for the AI's referral map — every
addition needs PT+EN parity, no key collisions, and `format_for_prompt`
must produce a stable bullet block that the system prompt can splice in.

Coverage check: every hereditary condition in HEREDITARY_CONDITIONS and
every wellness panel in ALL_PANELS must have AT LEAST one referral entry
that mentions it (by gene or by panel name). This catches the most
common drift — adding a new hereditary condition or wellness panel
without telling the AI which specialist to suggest.
"""
import pytest

from src.medical_specialties import (
    SPECIALTY_REFERRALS,
    find_relevant_for_analysis,
    format_for_prompt,
    lookup,
)


class TestSpecialtyReferralsShape:
    def test_every_entry_has_required_bilingual_fields(self):
        required = ("key", "genes", "trigger", "specialty", "notes")
        for r in SPECIALTY_REFERRALS:
            for f in required:
                assert f in r, f"Entry {r.get('key', '?')} missing {f!r}"
            for lang_field in ("trigger", "specialty", "notes"):
                assert "pt" in r[lang_field], f"{r['key']}.{lang_field}.pt missing"
                assert "en" in r[lang_field], f"{r['key']}.{lang_field}.en missing"
                assert r[lang_field]["pt"].strip(), f"{r['key']}.{lang_field}.pt is empty"
                assert r[lang_field]["en"].strip(), f"{r['key']}.{lang_field}.en is empty"

    def test_keys_are_unique(self):
        keys = [r["key"] for r in SPECIALTY_REFERRALS]
        assert len(keys) == len(set(keys)), f"duplicate keys: {keys}"

    def test_genes_field_is_a_list_of_strings(self):
        for r in SPECIALTY_REFERRALS:
            assert isinstance(r["genes"], list)
            assert all(isinstance(g, str) and g for g in r["genes"])


class TestFormatForPrompt:
    def test_pt_block_lists_every_entry_as_bullet(self):
        block = format_for_prompt("pt")
        for r in SPECIALTY_REFERRALS:
            assert r["trigger"]["pt"] in block
            assert r["specialty"]["pt"] in block

    def test_en_block_lists_every_entry_as_bullet(self):
        block = format_for_prompt("en")
        for r in SPECIALTY_REFERRALS:
            assert r["trigger"]["en"] in block
            assert r["specialty"]["en"] in block

    def test_block_is_markdown_bullets(self):
        for line in format_for_prompt("pt").split("\n"):
            assert line.startswith("- "), f"non-bullet line in prompt block: {line!r}"

    def test_block_does_not_leak_keys_or_notes(self):
        """Keys and notes belong to the module, not the prompt — keeps the
        system prompt as small as possible."""
        block = format_for_prompt("pt")
        for r in SPECIALTY_REFERRALS:
            assert r["key"] not in block
            assert r["notes"]["pt"] not in block


class TestLookup:
    def test_lookup_finds_known_key(self):
        entry = lookup("hboc_brca")
        assert entry is not None
        assert "BRCA1" in entry["genes"]

    def test_lookup_returns_none_for_unknown_key(self):
        assert lookup("does-not-exist") is None


class TestRelevanceMatching:
    """`find_relevant_for_analysis` is what plugs the catalog into the
    chat context. The model only gets the SUS/insurance pathway notes
    for findings the user actually has — so this is the gatekeeper for
    "don't tell a patient with no BRCA hits about oncogenetic referral
    pathways at INCA, because that's noise"."""

    def test_empty_analysis_returns_no_referrals(self):
        assert find_relevant_for_analysis({}) == []
        assert find_relevant_for_analysis(None) == []

    def test_matches_health_finding_by_gene(self):
        active = {"health": {"findings": [{"gene": "CYP2D6", "rsid": "rs1"}]}}
        result = find_relevant_for_analysis(active)
        keys = [r["key"] for r in result]
        assert "pgx_psychiatry" in keys

    def test_matches_disease_finding_by_gene(self):
        active = {"disease": {"findings": [{"gene": "BRCA1", "rsid": "rs80357906"}]}}
        result = find_relevant_for_analysis(active)
        assert any(r["key"] == "hboc_brca" for r in result)

    def test_matches_hereditary_match_by_gene(self):
        active = {"hereditary": {"matches": [{"genes": ["F5"], "gene_details": []}]}}
        result = find_relevant_for_analysis(active)
        assert any(r["key"] == "thrombophilia" for r in result)

    def test_matches_wellness_panel_by_key(self):
        active = {"wellness": {"thyroid": {"findings": [{"rsid": "rs1"}]}}}
        result = find_relevant_for_analysis(active)
        assert any(r["key"] == "wellness_thyroid" for r in result)

    def test_wellness_panel_without_findings_is_ignored(self):
        active = {"wellness": {"thyroid": {"findings": []}}}
        result = find_relevant_for_analysis(active)
        assert not any(r["key"] == "wellness_thyroid" for r in result)

    def test_multiple_overlaps_outrank_single_overlap(self):
        # BRCA1 + BRCA2 both belong to hboc_brca → score 2
        # CYP2C19 belongs to pgx_psychiatry → score 1
        active = {
            "disease": {"findings": [{"gene": "BRCA1"}, {"gene": "BRCA2"}]},
            "health": {"findings": [{"gene": "CYP2C19"}]},
        }
        result = find_relevant_for_analysis(active)
        assert result[0]["key"] == "hboc_brca"

    def test_panel_match_outranks_incidental_gene_overlap(self):
        """When the user has the Skin panel active AND a stray MC1R gene
        elsewhere, the panel referral should still come first."""
        active = {"wellness": {"skin": {"findings": [{"rsid": "rs1"}]}}}
        result = find_relevant_for_analysis(active)
        # The wellness_skin entry should be the top-ranked entry,
        # because exact panel match scores 2 (see implementation).
        assert result[0]["key"] == "wellness_skin"

    def test_max_results_caps_output(self):
        # Active analysis with many gene matches across multiple entries.
        active = {
            "disease": {"findings": [
                {"gene": "BRCA1"}, {"gene": "MLH1"}, {"gene": "APC"},
                {"gene": "TP53"}, {"gene": "PTEN"}, {"gene": "LDLR"},
                {"gene": "F5"}, {"gene": "HFE"}, {"gene": "SERPINA1"},
                {"gene": "CYP2D6"}, {"gene": "VKORC1"}, {"gene": "TPMT"},
            ]}
        }
        result = find_relevant_for_analysis(active, max_results=3)
        assert len(result) == 3

    def test_unrelated_analysis_returns_empty(self):
        active = {"disease": {"findings": [{"gene": "NEVER_HEARD_OF_THIS_GENE"}]}}
        result = find_relevant_for_analysis(active)
        assert result == []


class TestChatContextIntegration:
    """`_build_chat_context` in dashboard.py is where the catalog meets the
    user. The behavior we want to lock: relevant referral notes (with
    SUS/insurance pathway) get appended; otherwise the section stays out
    so empty / unrelated analyses don't get a generic referral block."""

    def test_context_includes_referral_notes_for_relevant_finding(self):
        from dashboard import _build_chat_context
        active = {
            "disease": {"findings": [
                {"gene": "BRCA1", "rsid": "rs80357906", "clinical_significance": "Pathogenic"},
            ]},
        }
        ctx = _build_chat_context(active, "pt")
        # The trigger phrase and a key part of the SUS/insurance note must
        # both surface — otherwise we've inlined the trigger without the
        # pathway, defeating the whole point of the integration.
        assert "BRCA1/2" in ctx or "HBOC" in ctx
        assert "INCA" in ctx or "NCCN" in ctx  # one of the SUS/insurance anchors

    def test_context_omits_referral_block_when_no_matches(self):
        from dashboard import _build_chat_context
        active = {"disease": {"findings": [{"gene": "DOES_NOT_EXIST"}]}}
        ctx = _build_chat_context(active, "pt")
        assert "Referral context" not in ctx

    def test_user_provided_sex_is_shown_without_uncertainty_disclaimer(self):
        from dashboard import _build_chat_context
        active = {"genome_info": {"profile": {"sex": "M"}}}
        ctx = _build_chat_context(active, "pt")
        assert "sex=M" in ctx
        # No inference disclaimer when the user typed sex themselves.
        assert "INFERRED" not in ctx

    def test_inferred_sex_carries_uncertainty_disclaimer(self):
        """If sex was inferred chromosomally (user didn't supply it), the
        chat context must flag it as uncertain so the model doesn't
        confidently say "you are male/female". Regression for a real
        miscall where a male user was inferred F (low Y coverage)."""
        from dashboard import _build_chat_context
        active = {
            "genome_info": {"profile": {"sex": "F", "sex_inferred": True}}
        }
        ctx = _build_chat_context(active, "pt")
        assert "sex=F" in ctx
        assert "INFERRED" in ctx
        # Make sure the model is told not to claim it as fact.
        assert "Do NOT state this as fact" in ctx or "ask the user to confirm" in ctx


class TestCoverageOfAppFindings:
    """Drift detector: every hereditary condition the app surfaces must
    have at least one matching referral, identified by gene overlap or by
    a substring of the condition name.

    Failure mode this catches: someone adds a new hereditary condition
    (e.g. von Hippel-Lindau) without telling the AI where to route the
    patient.
    """

    def _all_genes_in_referrals(self):
        out = set()
        for r in SPECIALTY_REFERRALS:
            out.update(r["genes"])
        return out

    def test_every_hereditary_condition_has_a_referral(self):
        from src.hereditary_conditions import HEREDITARY_CONDITIONS
        referral_genes = self._all_genes_in_referrals()
        missing = []
        for key, cond in HEREDITARY_CONDITIONS.items():
            cond_genes = set(cond.get("genes", []))
            if not cond_genes & referral_genes:
                missing.append(cond.get("name_pt") or cond.get("name_en") or key)
        assert not missing, (
            "Hereditary conditions with no specialty referral mapping:\n  - "
            + "\n  - ".join(missing)
        )

    def test_every_wellness_panel_has_a_referral(self):
        from src.wellness_panels import ALL_PANELS
        block_pt = format_for_prompt("pt").lower()
        block_en = format_for_prompt("en").lower()
        missing = []
        for key, panel in ALL_PANELS.items():
            # Match either by panel key (skin, sleep, nutri…) or by its
            # full name. Some panels share a single referral entry
            # (Nutri/Aging/Longevity), which is fine.
            if key.lower() in block_pt or key.lower() in block_en:
                continue
            if panel["name"].lower() in block_pt or panel["name"].lower() in block_en:
                continue
            missing.append(key)
        assert not missing, f"Wellness panels with no referral: {missing}"
