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
