"""
Regression: the drug-gene clinical notes in the "Drug Interactions" conclusions
leaked Portuguese into the English dashboard. `_get_drug_gene_note` returned a
PT-only dict regardless of language. These are clinically sensitive strings, so
they live as a hardcoded EN+PT pair (per the project i18n decision table) and
the accessor must branch on `lang`.

Locks: EN mode never returns Portuguese medical text; both languages resolve
the same gene keys.
"""
import dashboard


def test_drug_gene_note_en_is_english():
    # A genotype that won't match a curated status → falls back to `_default`.
    note = dashboard._get_drug_gene_note("VKORC1", "ZZ", "en")
    assert note  # not empty
    assert "warfarin" in note.lower()
    # PT source phrases must not leak into the English note.
    assert "alvo da warfarina" not in note
    assert "metaboliza" not in note


def test_drug_gene_note_pt_is_portuguese():
    note = dashboard._get_drug_gene_note("VKORC1", "ZZ", "pt")
    assert "alvo da warfarina" in note


def test_drug_gene_note_defaults_to_english():
    # No lang arg → EN (project default), never Portuguese.
    note = dashboard._get_drug_gene_note("SLCO1B1", "ZZ")
    assert "statin" in note.lower()
    assert "estatina" not in note


def test_drug_gene_note_both_languages_cover_same_genes():
    genes = ("CYP2D6", "CYP2C19", "CYP2C9", "VKORC1", "DPYD",
             "TPMT", "SLCO1B1", "CYP3A5", "HLA-B", "CYP1A2")
    for gene in genes:
        en = dashboard._get_drug_gene_note(gene, "ZZ", "en")
        pt = dashboard._get_drug_gene_note(gene, "ZZ", "pt")
        assert en, f"{gene} missing EN note"
        assert pt, f"{gene} missing PT note"


def test_drug_gene_note_unknown_gene_is_empty():
    assert dashboard._get_drug_gene_note("NOTAGENE", "AA", "en") == ""
