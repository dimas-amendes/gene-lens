"""Tests for the reference-database downloader.

Network is mocked everywhere — these never hit PharmGKB or NCBI. The PharmGKB
path is 🟠 High severity: a regression here silently strips drug-gene findings
from every report, so we lock the happy path plus graceful degradation on
network and archive errors.
"""
import csv
import gzip
import io
import json
import zipfile
from contextlib import contextmanager
from email.message import Message
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

import download_databases as dd


def _make_zip(members: dict[str, bytes]) -> bytes:
    """Build an in-memory zip mimicking PharmGKB's clinicalAnnotations.zip."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)
    return buf.getvalue()


@contextmanager
def _fake_urlopen(payload: bytes):
    """Patch urlopen to return a context-manager response with .read()."""
    class _Resp:
        headers = Message()  # download_pharmgkb reads resp.headers for meta
        def __enter__(self_inner):
            return self_inner
        def __exit__(self_inner, *a):
            return False
        def read(self_inner):
            return payload
    with patch.object(dd, "urlopen", lambda *a, **k: _Resp()):
        yield


# Realistic-size TSV bodies (> the 1 KB integrity floor download_pharmgkb enforces).
_ANN_TSV = b"col\tval\n" + b"annotation\trow\n" * 200
_ALLELES_TSV = b"col\tval\n" + b"allele\trow\n" * 200


def test_pharmgkb_downloads_and_extracts_wanted_tsvs(tmp_path):
    payload = _make_zip({
        "clinical_annotations.tsv": _ANN_TSV,
        "clinical_ann_alleles.tsv": _ALLELES_TSV,
        "clinical_ann_evidence.tsv": b"ignored\n",  # present but not wanted
        "LICENSE.txt": b"CC-BY-SA\n",
    })
    dd.DATA_DIR = tmp_path
    with _fake_urlopen(payload):
        ok = dd.download_pharmgkb()

    assert ok is True
    assert (tmp_path / "clinical_annotations.tsv").read_bytes() == _ANN_TSV
    assert (tmp_path / "clinical_ann_alleles.tsv").read_bytes() == _ALLELES_TSV
    # We only lift the two TSVs the analyzer needs, not the whole archive.
    assert not (tmp_path / "clinical_ann_evidence.tsv").exists()
    assert not (tmp_path / "LICENSE.txt").exists()


def test_pharmgkb_deletes_corrupt_tiny_extract(tmp_path):
    # A valid zip but with truncated/near-empty TSVs -> treated as corrupt,
    # both files deleted, and False returned so the UI asks to retry.
    payload = _make_zip({
        "clinical_annotations.tsv": b"x\n",
        "clinical_ann_alleles.tsv": b"y\n",
    })
    dd.DATA_DIR = tmp_path
    with _fake_urlopen(payload):
        ok = dd.download_pharmgkb()

    assert ok is False
    assert not (tmp_path / "clinical_annotations.tsv").exists()
    assert not (tmp_path / "clinical_ann_alleles.tsv").exists()


def test_pharmgkb_corrupt_download_keeps_existing(tmp_path):
    # User has working files; a forced re-download comes back corrupt (tiny).
    # Safe-update must preserve the existing good files, not overwrite them.
    ann = tmp_path / "clinical_annotations.tsv"
    alleles = tmp_path / "clinical_ann_alleles.tsv"
    ann.write_bytes(_ANN_TSV)
    alleles.write_bytes(_ALLELES_TSV)
    dd.DATA_DIR = tmp_path
    payload = _make_zip({
        "clinical_annotations.tsv": b"x\n",  # corrupt/truncated
        "clinical_ann_alleles.tsv": b"y\n",
    })
    with _fake_urlopen(payload):
        ok = dd.download_pharmgkb(force=True)

    assert ok is False
    assert ann.read_bytes() == _ANN_TSV          # existing preserved
    assert alleles.read_bytes() == _ALLELES_TSV
    assert not (tmp_path / "clinical_annotations.tsv.part").exists()


def test_clinvar_corrupt_download_keeps_existing(tmp_path, monkeypatch):
    # An unreadable (non-gzip) download must not destroy a working ClinVar.
    monkeypatch.setattr(dd, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dd, "CLINVAR_TSV", tmp_path / "clinvar_alleles.tsv")
    good = tmp_path / "clinvar_alleles.tsv"
    good.write_bytes(b"GOOD EXISTING CLINVAR\n" * 50)

    def fake_urlretrieve(url, filename, reporthook=None):
        Path(filename).write_bytes(b"this is not a gzip file")
        return filename, Message()

    monkeypatch.setattr(dd, "urlretrieve", fake_urlretrieve)
    ok = dd.download_clinvar()

    assert ok is False
    assert good.read_bytes().startswith(b"GOOD EXISTING CLINVAR")  # preserved
    assert not (tmp_path / "clinvar_alleles.tsv.part").exists()     # temp cleaned


def test_pharmgkb_skips_when_already_present(tmp_path):
    (tmp_path / "clinical_annotations.tsv").write_text("existing")
    (tmp_path / "clinical_ann_alleles.tsv").write_text("existing")
    dd.DATA_DIR = tmp_path

    # If it tried to hit the network we'd know: urlopen is patched to explode.
    with patch.object(dd, "urlopen", side_effect=AssertionError("should not fetch")):
        ok = dd.download_pharmgkb()

    assert ok is True
    assert (tmp_path / "clinical_annotations.tsv").read_text() == "existing"


def test_pharmgkb_degrades_on_network_error(tmp_path):
    dd.DATA_DIR = tmp_path
    with patch.object(dd, "urlopen", side_effect=URLError("no route to host")):
        ok = dd.download_pharmgkb()

    assert ok is False
    assert not (tmp_path / "clinical_annotations.tsv").exists()


def test_pharmgkb_degrades_on_corrupt_archive(tmp_path):
    dd.DATA_DIR = tmp_path
    with _fake_urlopen(b"this is not a zip file"):
        ok = dd.download_pharmgkb()

    assert ok is False
    assert not (tmp_path / "clinical_annotations.tsv").exists()


def test_pharmgkb_degrades_when_archive_missing_expected_tsvs(tmp_path):
    payload = _make_zip({"something_else.tsv": b"data\n"})
    dd.DATA_DIR = tmp_path
    with _fake_urlopen(payload):
        ok = dd.download_pharmgkb()

    assert ok is False
    assert not (tmp_path / "clinical_annotations.tsv").exists()


# ── ClinVar allele extraction (schema-drift regression) ──────────────────────

# The columns download_clinvar reads from variant_summary.txt.
_CLINVAR_HEADER = [
    "Assembly", "Chromosome", "Start", "Stop", "Type",
    "ReferenceAllele", "AlternateAllele", "ReferenceAlleleVCF", "AlternateAlleleVCF",
    "VariationID", "RCVaccession", "#AlleleID", "GeneSymbol",
    "ClinicalSignificance", "ReviewStatus", "LastEvaluated",
    "SubmitterCategories", "PhenotypeList", "Origin", "PhenotypeIDS",
]


def _clinvar_row(assembly, chrom, pos, vtype, ref_legacy, alt_legacy, ref_vcf, alt_vcf):
    return {
        "Assembly": assembly, "Chromosome": chrom, "Start": pos, "Stop": pos,
        "Type": vtype, "ReferenceAllele": ref_legacy, "AlternateAllele": alt_legacy,
        "ReferenceAlleleVCF": ref_vcf, "AlternateAlleleVCF": alt_vcf,
        "VariationID": "1", "RCVaccession": "RCV1", "#AlleleID": "10",
        "GeneSymbol": "BRCA1", "ClinicalSignificance": "Pathogenic",
        "ReviewStatus": "criteria provided, single submitter",
        "LastEvaluated": "2024-01-01", "SubmitterCategories": "1",
        "PhenotypeList": "Cancer", "Origin": "germline", "PhenotypeIDS": "MedGen:1",
    }


def _fake_variant_summary_gz(rows) -> bytes:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=_CLINVAR_HEADER, delimiter="\t")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return gzip.compress(buf.getvalue().encode("utf-8"))


def test_clinvar_reads_alleles_from_vcf_columns(tmp_path, monkeypatch):
    """Regression for the ClinVar drift: real alleles live in the *VCF columns;
    the legacy ReferenceAllele/AlternateAllele are "na". The old filter read the
    legacy columns and kept ~36 of millions. This locks the VCF-column read."""
    rows = [
        # GRCh37 SNVs with real alleles only in the VCF columns (the live shape)
        _clinvar_row("GRCh37", "1", "100", "single nucleotide variant", "na", "na", "G", "A"),
        _clinvar_row("GRCh37", "2", "200", "single nucleotide variant", "na", "na", "C", "T"),
        # indel: VCF ref longer than one base -> excluded
        _clinvar_row("GRCh37", "3", "300", "Deletion", "na", "na", "GCTG", "G"),
        # wrong assembly -> excluded
        _clinvar_row("GRCh38", "4", "400", "single nucleotide variant", "na", "na", "G", "A"),
    ]
    gz_bytes = _fake_variant_summary_gz(rows)

    monkeypatch.setattr(dd, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dd, "CLINVAR_TSV", tmp_path / "clinvar_alleles.tsv")

    def fake_urlretrieve(url, filename, reporthook=None):
        Path(filename).write_bytes(gz_bytes)
        return filename, Message()

    monkeypatch.setattr(dd, "urlretrieve", fake_urlretrieve)

    assert dd.download_clinvar() is True
    out_lines = (tmp_path / "clinvar_alleles.tsv").read_text().strip().splitlines()
    # header + exactly the 2 GRCh37 SNVs (indel and GRCh38 dropped)
    assert len(out_lines) == 3
    body = "\n".join(out_lines[1:])
    assert "\tG\tA\t" in body and "\tC\tT\t" in body
    # and NOT the "na" legacy values
    assert "\tna\tna\t" not in body


def test_clinvar_relevance_filter_drops_benign_and_lowstar_vus(tmp_path, monkeypatch):
    """Only variants the dashboard can surface are kept: benign/likely-benign
    are dropped, and uncertain (VUS) survive only at >=2 gold stars."""
    def row(chrom, sig, review):
        r = _clinvar_row("GRCh37", chrom, "100", "single nucleotide variant",
                         "na", "na", "G", "A")
        r["ClinicalSignificance"] = sig
        r["ReviewStatus"] = review
        return r

    two_star = "criteria provided, multiple submitters, no conflicts"  # 3 stars
    one_star = "criteria provided, single submitter"                   # 1 star
    rows = [
        row("1", "Pathogenic", one_star),                 # keep
        row("2", "Benign", two_star),                     # drop (benign)
        row("3", "Likely benign", two_star),              # drop (likely benign)
        row("4", "Uncertain significance", one_star),     # drop (VUS, <2 stars)
        row("5", "Uncertain significance", two_star),     # keep (VUS, >=2 stars)
        row("6", "risk factor", one_star),                # keep (risk factor)
    ]
    gz_bytes = _fake_variant_summary_gz(rows)
    monkeypatch.setattr(dd, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dd, "CLINVAR_TSV", tmp_path / "clinvar_alleles.tsv")
    monkeypatch.setattr(dd, "urlretrieve",
                        lambda url, filename, reporthook=None: (Path(filename).write_bytes(gz_bytes), (filename, Message()))[1])

    assert dd.download_clinvar() is True
    lines = (tmp_path / "clinvar_alleles.tsv").read_text().strip().splitlines()
    # header + 3 kept (pathogenic, high-star VUS, risk factor)
    assert len(lines) == 4


# ── Update checking ──────────────────────────────────────────────────────────

def _headers(**kw) -> Message:
    m = Message()
    for k, v in kw.items():
        m[k] = v
    return m


def test_is_newer_prefers_etag_mismatch():
    server = _headers(ETag='"v2"', **{"Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT"})
    assert dd._is_newer(server, {"etag": '"v1"'}) is True
    assert dd._is_newer(server, {"etag": '"v2"'}) is False


def test_is_newer_falls_back_to_last_modified():
    server = _headers(**{"Last-Modified": "Wed, 01 Jan 2025 00:00:00 GMT"})
    older = {"last_modified": "Mon, 01 Jan 2024 00:00:00 GMT"}
    newer = {"last_modified": "Fri, 01 Jan 2027 00:00:00 GMT"}
    assert dd._is_newer(server, older) is True
    assert dd._is_newer(server, newer) is False


def test_is_newer_unknown_signals_do_not_nag():
    # No headers, or no stored meta -> treat as "not newer" (don't false-alarm).
    assert dd._is_newer(None, {"etag": '"v1"'}) is False
    assert dd._is_newer(_headers(ETag='"v2"'), {}) is False


def test_check_updates_reports_not_downloaded(tmp_path):
    dd.DATA_DIR = tmp_path  # empty
    with patch.object(dd, "_fetch_head", side_effect=AssertionError("no network")):
        status = dd.check_for_updates()
    assert status["clinvar"] == "not-downloaded"
    assert status["pharmgkb"] == "not-downloaded"


def test_check_updates_unknown_without_meta(tmp_path):
    (tmp_path / "clinvar_alleles.tsv").write_text("x")
    (tmp_path / "clinical_ann_alleles.tsv").write_text("x")
    dd.DATA_DIR = tmp_path  # markers present, but no .db_meta.json
    with patch.object(dd, "_fetch_head", side_effect=AssertionError("no network")):
        status = dd.check_for_updates()
    assert status["clinvar"] == "unknown"
    assert status["pharmgkb"] == "unknown"


def test_check_updates_detects_available_and_uptodate(tmp_path):
    (tmp_path / "clinvar_alleles.tsv").write_text("x")
    (tmp_path / "clinical_ann_alleles.tsv").write_text("x")
    (tmp_path / dd.DB_META_NAME).write_text(json.dumps({
        "clinvar": {"etag": '"old"'},
        "pharmgkb": {"etag": '"same"'},
    }))
    dd.DATA_DIR = tmp_path

    def fake_head(url):
        if url == dd._SOURCES["clinvar"]["url"]:
            return _headers(ETag='"new"')   # changed -> update available
        return _headers(ETag='"same"')      # unchanged -> up to date

    with patch.object(dd, "_fetch_head", side_effect=fake_head):
        status = dd.check_for_updates()
    assert status["clinvar"] == "update-available"
    assert status["pharmgkb"] == "up-to-date"


def test_check_updates_unknown_when_head_fails(tmp_path):
    (tmp_path / "clinvar_alleles.tsv").write_text("x")
    (tmp_path / "clinical_ann_alleles.tsv").write_text("x")
    (tmp_path / dd.DB_META_NAME).write_text(json.dumps({
        "clinvar": {"etag": '"a"'}, "pharmgkb": {"etag": '"b"'},
    }))
    dd.DATA_DIR = tmp_path
    with patch.object(dd, "_fetch_head", return_value=None):  # network down
        status = dd.check_for_updates()
    assert status["clinvar"] == "unknown"
    assert status["pharmgkb"] == "unknown"


def test_meta_written_on_pharmgkb_download(tmp_path):
    payload = _make_zip({
        "clinical_annotations.tsv": _ANN_TSV,
        "clinical_ann_alleles.tsv": _ALLELES_TSV,
    })
    dd.DATA_DIR = tmp_path

    class _Resp:
        headers = _headers(ETag='"pg1"', **{"Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT"})
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return payload

    with patch.object(dd, "urlopen", lambda *a, **k: _Resp()):
        assert dd.download_pharmgkb() is True

    meta = json.loads((tmp_path / dd.DB_META_NAME).read_text())
    assert meta["pharmgkb"]["etag"] == '"pg1"'
    assert meta["pharmgkb"]["last_modified"] == "Mon, 01 Jan 2024 00:00:00 GMT"
