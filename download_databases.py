#!/usr/bin/env python3
"""
Database downloader -- the ONLY script that accesses the network.

Downloads ClinVar and PharmGKB databases for local analysis.
Run this ONCE, then all analysis is 100% offline.

Usage:
    python download_databases.py              # Download all
    python download_databases.py --clinvar    # ClinVar only
    python download_databases.py --pharmgkb   # PharmGKB only

ClinVar: Free, no registration needed.
PharmGKB: Requires free account -- download manually if this fails.
"""
import argparse
import csv
import gzip
import io
import json
import os
import shutil
import sys
import tempfile
import time
import zipfile
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import urlretrieve, Request, urlopen
from urllib.error import URLError

from config import (
    DATA_DIR, CLINVAR_TSV, CLINVAR_GZ,
    CLINVAR_DOWNLOAD_URL, PHARMGKB_DOWNLOAD_URL,
    CLINVAR_MIN_STARS_UNCERTAIN,
)

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


# ── Update tracking ──────────────────────────────────────────────────────────
# We delete the raw ClinVar .gz after processing, so the local file's mtime
# can't tell us how fresh the SOURCE is. Instead we record the source's
# Last-Modified / ETag at download time in a sidecar and compare against a
# lightweight HEAD when the user explicitly checks for updates. No automatic
# network on launch — the offline-after-setup promise stays intact.
DB_META_NAME = ".db_meta.json"

# Which on-disk artifact proves a source has been downloaded, and where to fetch
# its freshness headers from.
_SOURCES = {
    "clinvar": {"url": CLINVAR_DOWNLOAD_URL, "marker": "clinvar_alleles.tsv"},
    # Both PharmGKB TSVs are required (see _pharmgkb_missing); key off the rarer
    # alleles file so "up-to-date" can't disagree with "present".
    "pharmgkb": {"url": PHARMGKB_DOWNLOAD_URL, "marker": "clinical_ann_alleles.tsv"},
}


def _meta_path() -> Path:
    return DATA_DIR / DB_META_NAME


def _read_meta() -> dict:
    p = _meta_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write_meta(source: str, headers) -> None:
    """Persist the source's freshness signals (Last-Modified, ETag) after a
    successful download. `headers` is an http.client.HTTPMessage / EmailMessage.
    Best-effort: a write failure must never break the download itself."""
    try:
        meta = _read_meta()
        meta[source] = {
            "last_modified": headers.get("Last-Modified") if headers else None,
            "etag": headers.get("ETag") if headers else None,
            "downloaded_at": int(time.time()),
        }
        _meta_path().write_text(json.dumps(meta, indent=2), encoding="utf-8")
    except OSError:
        pass


def _fetch_head(url: str):
    """Fetch just the freshness headers (Last-Modified/ETag) of the source,
    return them or None on failure. We send HEAD, but urllib turns a 303
    (PharmGKB -> S3) into a GET on the redirect; we never read the body, so
    it's metadata-only either way (no database file is downloaded)."""
    try:
        req = Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (GeneLens)"})
        with urlopen(req, timeout=30) as resp:
            return resp.headers
    except (URLError, OSError):
        return None


def _is_newer(server_headers, stored: dict) -> bool:
    """True if the server copy looks newer than what we recorded. Prefer ETag
    (exact), fall back to Last-Modified date comparison. Unknown -> not newer
    (we don't nag the user on ambiguous signals)."""
    if server_headers is None or not stored:
        return False
    s_etag = server_headers.get("ETag")
    if s_etag and stored.get("etag"):
        return s_etag != stored["etag"]
    s_lm = server_headers.get("Last-Modified")
    if s_lm and stored.get("last_modified"):
        try:
            return parsedate_to_datetime(s_lm) > parsedate_to_datetime(stored["last_modified"])
        except (TypeError, ValueError):
            return False
    return False


def check_for_updates() -> dict:
    """Compare each downloaded database against its source. Returns a dict
    keyed by source name with one of:
      'not-downloaded'   — no local copy yet
      'up-to-date'       — local matches source
      'update-available' — source is newer
      'unknown'          — downloaded before tracking, or HEAD failed/ambiguous
    Explicit, on-demand, read-only — the caller decides what to do about it.
    """
    meta = _read_meta()
    out = {}
    for name, spec in _SOURCES.items():
        if not (DATA_DIR / spec["marker"]).exists():
            out[name] = "not-downloaded"
            continue
        stored = meta.get(name)
        if not stored:
            out[name] = "unknown"
            continue
        head = _fetch_head(spec["url"])
        if head is None:
            out[name] = "unknown"
            continue
        out[name] = "update-available" if _is_newer(head, stored) else "up-to-date"
    return out


def _progress_hook(block_num, block_size, total_size):
    """Simple download progress indicator."""
    if total_size > 0:
        downloaded = block_num * block_size
        pct = min(100, downloaded * 100 // total_size)
        mb = downloaded / (1024 * 1024)
        total_mb = total_size / (1024 * 1024)
        print(f"\r  [{pct:3d}%] {mb:.1f} / {total_mb:.1f} MB", end="", flush=True)


def _discard_files(*paths) -> None:
    """Best-effort delete (public reference data, not genetic user data)."""
    for p in paths:
        try:
            if p.exists():
                p.unlink()
        except OSError:
            pass


def download_clinvar(progress_cb=None):
    """Download ClinVar and validate before replacing anything.

    Safe-update: the new copy is written to a temp file and only swapped into
    place (atomically) once it passes the integrity check. If the download is
    unreadable/truncated or the extract is suspiciously tiny, the temp is
    discarded and any EXISTING working database is left untouched — a bad
    re-download never destroys a good local copy. Returns False on failure so
    the caller can tell the user to retry.
    """
    gz_path = DATA_DIR / "variant_summary.txt.gz"
    tmp_tsv = CLINVAR_TSV.with_name(CLINVAR_TSV.name + ".part")
    had_existing = CLINVAR_TSV.exists()
    try:
        return _download_clinvar_impl(progress_cb, tmp_tsv, gz_path, had_existing)
    except (OSError, EOFError) as e:
        print(f"\n  [ERROR] ClinVar archive could not be read: {e}")
        _discard_files(tmp_tsv, gz_path)  # never touch the real file
        if had_existing:
            print("  The download was corrupted. Kept your existing ClinVar")
            print("  database; please try again when you can.")
        else:
            print("  The download looks corrupted or incomplete. Please try again.")
        return False


def _download_clinvar_impl(progress_cb, tmp_tsv, gz_path, had_existing):
    """Download ClinVar variant_summary.txt.gz and extract to filtered TSV.

    The raw file is ~120MB compressed, ~1GB uncompressed with ~9M rows. We keep
    only GRCh37 SNPs that the dashboard can actually surface — pathogenic,
    likely-pathogenic, risk factors, and >=2-star uncertain variants — dropping
    benign and low-confidence VUS. Result is ~880k rows / ~380MB, RAM-friendly.

    progress_cb(phase: str, pct: int) is an optional callback for UI progress:
    phase is "download" (pct 0-100) or "process" (pct -1, indeterminate).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    url = CLINVAR_DOWNLOAD_URL

    print(f"\n  Downloading ClinVar variant_summary.txt.gz...")
    print(f"  Source: {url}")
    print(f"  This file is ~120 MB -- may take a few minutes.\n")

    def _hook(block_num, block_size, total_size):
        _progress_hook(block_num, block_size, total_size)  # console line
        if progress_cb and total_size > 0:
            # Download is the first half of the overall bar (0-50%); the row
            # processing that follows fills 50-100%.
            pct = min(100, block_num * block_size * 100 // total_size)
            progress_cb("download", pct // 2)

    try:
        _, _clinvar_headers = urlretrieve(url, str(gz_path), reporthook=_hook)
        print()  # newline after progress
    except URLError as e:
        print(f"\n  [ERROR] Download failed: {e}")
        print("  Try downloading manually from:")
        print(f"    {url}")
        print(f"  And place the file at: {gz_path}")
        return False

    print("  Processing ClinVar into filtered TSV...")

    # Output columns we need
    out_columns = [
        "chrom", "pos", "ref", "alt", "start", "stop", "strand",
        "variation_type", "variation_id", "rcv", "scv", "allele_id",
        "symbol", "hgvs_c", "hgvs_p", "molecular_consequence",
        "clinical_significance", "clinical_significance_ordered",
        "pathogenic", "likely_pathogenic", "uncertain_significance",
        "likely_benign", "benign",
        "review_status", "review_status_ordered",
        "last_evaluated", "all_submitters", "submitters_ordered",
        "all_traits", "all_pmids", "inheritance_modes",
        "age_of_onset", "prevalence", "disease_mechanism",
        "origin", "xrefs", "dates_ordered", "gold_stars", "conflicted",
    ]

    # Column mapping from variant_summary.txt headers
    col_map = {
        "#AlleleID": "allele_id",
        "Type": "variation_type",
        "GeneSymbol": "symbol",
        "ClinicalSignificance": "clinical_significance",
        "ClinSigSimple": None,
        "RS# (dbSNP)": None,  # we build rsid from position
        "Assembly": None,  # filter column
        "Chromosome": "chrom",
        "Start": "pos",
        "Stop": "stop",
        "ReferenceAllele": "ref",
        "AlternateAllele": "alt",
        "ReviewStatus": "review_status",
        "NumberSubmitters": None,
        "PhenotypeList": "all_traits",
        "PhenotypeIDS": None,
        "RCVaccession": "rcv",
        "Origin": "origin",
        "VariationID": "variation_id",
        "Guidelines": None,
    }

    count = 0
    written = 0

    with gzip.open(str(gz_path), "rt", encoding="utf-8", errors="replace") as infile:
        reader = csv.DictReader(infile, delimiter="\t")

        with open(str(tmp_tsv), "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_columns, delimiter="\t")
            writer.writeheader()

            for row in reader:
                count += 1
                if count % 200000 == 0:
                    print(f"    Processed {count:,} rows, kept {written:,}...")
                    if progress_cb:
                        # Processing fills the 50-100% half of the bar (~9M rows).
                        progress_cb("process", 50 + min(49, count * 49 // 9_000_000))

                # Filter: only GRCh37 assembly (most consumer tests use this)
                assembly = row.get("Assembly", "")
                if assembly != "GRCh37":
                    continue

                # ClinVar keeps the real alleles in the VCF columns now; the
                # legacy ReferenceAllele/AlternateAllele are "na" on virtually
                # every row (that drift is what made the old filter keep ~36
                # variants out of millions). Prefer the VCF columns, fall back
                # to the legacy ones only if VCF is absent.
                ref = row.get("ReferenceAlleleVCF", "") or row.get("ReferenceAllele", "")
                alt = row.get("AlternateAlleleVCF", "") or row.get("AlternateAllele", "")

                # Filter: only true SNPs (single-base ref and alt)
                if len(ref) != 1 or len(alt) != 1:
                    continue
                if ref == "na" or alt == "na":
                    continue

                # Clinical-relevance filter: keep only variants the app can
                # actually surface. Benign / likely-benign never produce a risk
                # finding, and uncertain (VUS) variants are reported only at
                # >= CLINVAR_MIN_STARS_UNCERTAIN gold stars. Dropping the rest
                # cuts the extract from ~1.4 GB to a RAM-friendly size without
                # losing anything the dashboard shows.
                sig = row.get("ClinicalSignificance", "").lower()
                if sig.startswith("benign") or "likely benign" in sig:
                    continue
                if ("uncertain" in sig
                        and _review_to_stars(row.get("ReviewStatus", "")) < CLINVAR_MIN_STARS_UNCERTAIN):
                    continue

                # Build output row
                out_row = {
                    "chrom": row.get("Chromosome", ""),
                    "pos": row.get("Start", ""),
                    "ref": ref,
                    "alt": alt,
                    "start": row.get("Start", ""),
                    "stop": row.get("Stop", ""),
                    "strand": "+",
                    "variation_type": row.get("Type", ""),
                    "variation_id": row.get("VariationID", ""),
                    "rcv": row.get("RCVaccession", ""),
                    "scv": "",
                    "allele_id": row.get("#AlleleID", ""),
                    "symbol": row.get("GeneSymbol", ""),
                    "hgvs_c": "",
                    "hgvs_p": "",
                    "molecular_consequence": "",
                    "clinical_significance": row.get("ClinicalSignificance", ""),
                    "clinical_significance_ordered": row.get("ClinicalSignificance", "").lower(),
                    "pathogenic": "1" if "pathogenic" in row.get("ClinicalSignificance", "").lower() and "likely" not in row.get("ClinicalSignificance", "").lower() else "0",
                    "likely_pathogenic": "1" if "likely pathogenic" in row.get("ClinicalSignificance", "").lower() else "0",
                    "uncertain_significance": "1" if "uncertain" in row.get("ClinicalSignificance", "").lower() else "0",
                    "likely_benign": "1" if "likely benign" in row.get("ClinicalSignificance", "").lower() else "0",
                    "benign": "1" if row.get("ClinicalSignificance", "").lower().startswith("benign") else "0",
                    "review_status": row.get("ReviewStatus", ""),
                    "review_status_ordered": row.get("ReviewStatus", ""),
                    "last_evaluated": row.get("LastEvaluated", ""),
                    "all_submitters": row.get("SubmitterCategories", ""),
                    "submitters_ordered": "",
                    "all_traits": row.get("PhenotypeList", ""),
                    "all_pmids": "",
                    "inheritance_modes": "",
                    "age_of_onset": "",
                    "prevalence": "",
                    "disease_mechanism": "",
                    "origin": row.get("Origin", ""),
                    "xrefs": row.get("PhenotypeIDS", ""),
                    "dates_ordered": row.get("LastEvaluated", ""),
                    "gold_stars": _review_to_stars(row.get("ReviewStatus", "")),
                    "conflicted": "1" if "conflict" in row.get("ClinicalSignificance", "").lower() else "0",
                }
                writer.writerow(out_row)
                written += 1

    print(f"  Done: {count:,} total rows -> {written:,} SNPs kept (writing temp)")

    # Post-download integrity gate: a healthy ClinVar SNP extract is hundreds of
    # thousands of rows. A tiny result means an upstream schema change silently
    # broke the filter (exactly how the ReferenceAllele->VCF drift slipped by).
    # Discard the TEMP and fail — the real file (if any) is never touched, so a
    # bad re-download can't destroy a working database. count <= threshold means
    # a tiny synthetic/test input (not a real run), so don't flag it here.
    CLINVAR_MIN_EXPECTED = 100_000
    if count > CLINVAR_MIN_EXPECTED and written < CLINVAR_MIN_EXPECTED:
        print(
            f"\n  [ERROR] Only {written:,} SNPs from {count:,} rows — far below the "
            f"~{CLINVAR_MIN_EXPECTED:,} expected. The download is incomplete or the "
            "ClinVar layout changed."
        )
        _discard_files(tmp_tsv, gz_path)
        print("  Kept the existing database." if had_existing
              else "  Nothing was installed. Please try again.")
        return False

    # Valid: atomically swap the temp into place (replaces any existing copy in
    # one step, so a reader never sees a half-written file).
    os.replace(str(tmp_tsv), str(CLINVAR_TSV))
    print(f"  OK: {written:,} SNPs -> {CLINVAR_TSV.name}")

    # Record the SOURCE freshness before we delete the raw file — this is the
    # only moment we can see the server's Last-Modified/ETag for update checks.
    _write_meta("clinvar", _clinvar_headers)

    # Clean up raw download
    if gz_path.exists():
        gz_path.unlink()
        print(f"  Cleaned up: {gz_path.name}")

    return True


def _review_to_stars(review_status: str) -> int:
    """Convert ClinVar review status to gold stars (0-4)."""
    rs = review_status.lower()
    if "practice guideline" in rs:
        return 4
    if "expert panel" in rs:
        return 4
    if "multiple submitters" in rs and "no conflicts" in rs:
        return 3
    if "multiple submitters" in rs:
        return 2
    if "criteria provided" in rs:
        return 1
    return 0


# TSV members we lift out of the PharmGKB clinical-annotations zip. The archive
# also ships evidence/history TSVs and a LICENSE we don't consume here.
PHARMGKB_WANTED = ("clinical_annotations.tsv", "clinical_ann_alleles.tsv")


def download_pharmgkb(force=False):
    """Download and extract the PharmGKB clinical-annotations bundle.

    The clinicalAnnotations.zip is served publicly (the API 303-redirects to
    an S3 object, no login), so we can fetch it the same way as ClinVar and
    unzip just the two TSVs the analyzer needs into data/. Drug-gene findings
    are optional — on any failure we degrade gracefully and return False.

    force=True re-downloads even if the files already exist (used by the in-app
    "Update" action); the default skips when both files are present.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    ann = DATA_DIR / "clinical_annotations.tsv"
    alleles = DATA_DIR / "clinical_ann_alleles.tsv"
    if not force and ann.exists() and alleles.exists():
        print("  [OK] PharmGKB files already present!")
        return True

    url = PHARMGKB_DOWNLOAD_URL
    print(f"\n  Downloading PharmGKB clinical annotations...")
    print(f"  Source: {url}")
    print(f"  This file is ~1 MB.\n")

    saved_headers = None
    try:
        # A User-Agent avoids the occasional bot filter; urllib follows the
        # 303 redirect to S3 on its own.
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (GeneLens)"})
        with urlopen(req, timeout=60) as resp:
            saved_headers = resp.headers  # freshness of the final S3 object
            payload = resp.read()
    except (URLError, OSError) as e:
        print(f"  [ERROR] PharmGKB download failed: {e}")
        print("  Drug-gene findings will be unavailable. You can retry later,")
        print("  or download manually from https://www.pharmgkb.org/downloads")
        return False

    # Safe-update: extract to temp files, validate, and only then swap into
    # place. A corrupt re-download never overwrites a working local copy.
    tmp_for = {w: DATA_DIR / (w + ".part") for w in PHARMGKB_WANTED}
    had_existing = ann.exists() and alleles.exists()
    try:
        extracted = []
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            names = {Path(n).name: n for n in zf.namelist()}
            for wanted in PHARMGKB_WANTED:
                member = names.get(wanted)
                if member is None:
                    continue
                with zf.open(member) as src, open(tmp_for[wanted], "wb") as dst:
                    shutil.copyfileobj(src, dst)
                extracted.append(wanted)
    except (zipfile.BadZipFile, OSError) as e:
        print(f"  [ERROR] Could not extract PharmGKB archive (corrupt or")
        print(f"  incomplete download): {e}. Please try again.")
        _discard_files(*tmp_for.values())  # drop any half-written partials
        return False

    # Integrity: both TSVs present and non-trivial (a valid
    # clinical_annotations.tsv is hundreds of KB). Tiny = truncated/corrupt.
    ann_tmp, all_tmp = tmp_for["clinical_annotations.tsv"], tmp_for["clinical_ann_alleles.tsv"]
    _PHARMGKB_MIN_BYTES = 1024
    valid = (ann_tmp.exists() and all_tmp.exists()
             and ann_tmp.stat().st_size >= _PHARMGKB_MIN_BYTES
             and all_tmp.stat().st_size >= _PHARMGKB_MIN_BYTES)
    if not valid:
        print("  [ERROR] PharmGKB download looks corrupt or incomplete.")
        _discard_files(*tmp_for.values())
        print("  Kept your existing PharmGKB files." if had_existing
              else "  Please try again.")
        return False

    os.replace(str(ann_tmp), str(ann))
    os.replace(str(all_tmp), str(alleles))
    _write_meta("pharmgkb", saved_headers)
    print(f"  Done: extracted {', '.join(extracted)} to {DATA_DIR.name}/")
    return True


def main():
    parser = argparse.ArgumentParser(description="Download reference databases for genetic analysis")
    parser.add_argument("--clinvar", action="store_true", help="Download ClinVar only")
    parser.add_argument("--pharmgkb", action="store_true", help="PharmGKB instructions only")
    args = parser.parse_args()

    print("=" * 60)
    print("  Genetic Database Downloader")
    print("  This is the ONLY script that accesses the network.")
    print("=" * 60)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not args.clinvar and not args.pharmgkb:
        # Download both
        download_clinvar()
        download_pharmgkb()
    elif args.clinvar:
        download_clinvar()
    elif args.pharmgkb:
        download_pharmgkb()

    print("\n" + "=" * 60)
    print("  After downloading, all analysis runs 100% OFFLINE.")
    print("  Your genetic data never leaves your machine.")
    print("=" * 60)


if __name__ == "__main__":
    main()
