"""
Tests for src.i18n — keeps the EN/PT STRINGS dicts in lockstep.

The product is EN-first, PT-BR is the translation. Drift between them is
the #1 source of bugs in this codebase: a template like `{{ t.foo_bar }}`
silently renders empty if `foo_bar` exists in PT but not in EN (or vice
versa), and we only notice when a user complains about a missing label.

This file catches that drift in CI, where it's free, instead of in
production, where it's not.
"""
import pytest

from src.i18n import (
    DEFAULT_LANG,
    LANGS,
    Lang,
    STRINGS,
    get_strings,
    normalize_lang,
)


# ── Key-set parity ────────────────────────────────────────────────────────────

def test_en_and_pt_string_dicts_share_the_exact_same_key_set():
    en = set(STRINGS["en"].keys())
    pt = set(STRINGS["pt"].keys())
    en_only = en - pt
    pt_only = pt - en
    assert not en_only, f"keys present in EN but missing in PT: {sorted(en_only)}"
    assert not pt_only, f"keys present in PT but missing in EN: {sorted(pt_only)}"


def test_every_supported_language_has_a_strings_block():
    for lang in LANGS:
        assert lang in STRINGS, f"LANGS lists {lang!r} but STRINGS has no block for it"


def test_no_strings_block_for_unsupported_language():
    """Catches a stray block left behind after a deprecation (e.g. removing
    'es' from LANGS but forgetting the dict entry — would still ship in the
    bundle and confuse readers)."""
    extras = set(STRINGS.keys()) - set(LANGS)
    assert not extras, f"STRINGS has untracked languages: {extras}"


# ── Values are non-empty ──────────────────────────────────────────────────────

@pytest.mark.parametrize("lang", LANGS)
def test_no_empty_string_values(lang):
    """A blank value usually means someone added a key, hit save, and
    forgot to fill the translation. Catches that on commit."""
    empty = [k for k, v in STRINGS[lang].items() if not str(v).strip()]
    assert not empty, f"{lang!r} has empty values for keys: {empty}"


@pytest.mark.parametrize("lang", LANGS)
def test_no_placeholder_todo_values(lang):
    """Reject obvious "I'll fill this in later" sentinels."""
    sentinels = ("TODO", "FIXME", "XXX", "...", "lorem")
    bad = []
    for k, v in STRINGS[lang].items():
        val = str(v).strip().lower()
        for s in sentinels:
            if val == s.lower() or val.startswith(f"{s.lower()}:"):
                bad.append((k, v))
                break
    assert not bad, f"{lang!r} has placeholder values: {bad}"


# ── Format-string structure must match across languages ───────────────────────

def _placeholders(s: str) -> set[str]:
    """Extract '{name}' style placeholders from a template string."""
    import re
    return set(re.findall(r"{([^}{:!]+)(?:[:!][^}]*)?}", s))


def test_format_placeholders_match_across_languages():
    """If EN says 'Found {count} variants', PT must also use {count} —
    otherwise `.format(count=…)` raises KeyError on the PT side at runtime.
    This is the kind of bug that only fires in production for PT users."""
    mismatches = []
    en = STRINGS["en"]
    for key in en:
        en_ph = _placeholders(str(en[key]))
        for other in LANGS:
            if other == "en":
                continue
            other_val = STRINGS[other].get(key)
            if other_val is None:
                continue  # covered by the parity test
            other_ph = _placeholders(str(other_val))
            if en_ph != other_ph:
                mismatches.append({
                    "key": key,
                    "en_placeholders": sorted(en_ph),
                    f"{other}_placeholders": sorted(other_ph),
                })
    assert not mismatches, f"placeholder mismatch between languages: {mismatches}"


# ── get_strings / normalize_lang public API ───────────────────────────────────

def test_get_strings_returns_the_right_block():
    assert get_strings("en") is STRINGS["en"]
    assert get_strings("pt") is STRINGS["pt"]


def test_get_strings_default_is_english():
    """EN is the source-of-truth language — the default must reflect that."""
    assert DEFAULT_LANG == "en"
    # And get_strings() with no arg should match.
    assert get_strings() is STRINGS["en"]


def test_normalize_lang_passes_known_codes_through():
    assert normalize_lang("en") == "en"
    assert normalize_lang("pt") == "pt"


def test_normalize_lang_coerces_unknowns_to_default():
    assert normalize_lang("xx") == DEFAULT_LANG
    assert normalize_lang("") == DEFAULT_LANG
    assert normalize_lang(None) == DEFAULT_LANG


def test_normalize_lang_does_not_accept_pt_br_form():
    """Cookie/URL boundary is documented to use bare 'pt'/'en'. If someone
    starts shipping 'pt-BR' through the boundary, we want them to add it
    deliberately, not silently — pin the current contract."""
    # 'pt-BR' is NOT in LANGS, so normalize should fall back. If a future
    # change adds it, update this test consciously.
    assert normalize_lang("pt-BR") == DEFAULT_LANG


# ── Lang Literal stays in sync with LANGS tuple ───────────────────────────────

def test_lang_literal_matches_langs_tuple():
    """LANGS is derived from `Lang = Literal[...]` via get_args. If someone
    redefines Lang without updating LANGS (or vice versa), drift is silent
    until a runtime check fails. Pin equivalence here."""
    from typing import get_args
    assert set(get_args(Lang)) == set(LANGS)


# ── HTML-bearing strings are explicitly allowlisted ──────────────────────────
#
# Most STRINGS are rendered with Jinja autoescape — embedding HTML defeats
# that. A small set of strings DO need formatting (`<strong>`, `<span>`)
# and are rendered with `|safe` in the templates. Pin the allowlist here so
# any NEW key that smuggles HTML in fails the test and forces a deliberate
# decision instead of a silent precedent.
HTML_ALLOWED_KEYS = {
    "medical_banner",
    "consent_purpose",
    "consent_fact_fp",
    "consent_fact_not_replace",
    "consent_fact_never_change",
    "consent_fact_no_liability",
    "ancestry_desc",
}


@pytest.mark.parametrize("lang", LANGS)
def test_only_allowlisted_strings_contain_html_tags(lang):
    import re
    # Match a real opening tag: '<' + ascii letter, not '<3' or '<=' or '<key>'
    # where the next char is a brace etc.
    tag_re = re.compile(r"<[A-Za-z]")
    leaked = []
    for k, v in STRINGS[lang].items():
        if k in HTML_ALLOWED_KEYS:
            continue
        if tag_re.search(str(v)):
            leaked.append((k, v))
    assert not leaked, (
        f"{lang!r} has new HTML-bearing strings outside the allowlist — "
        f"either render via a dedicated template, use |safe deliberately and "
        f"add the key to HTML_ALLOWED_KEYS, or move the markup into the template: "
        f"{leaked}"
    )
