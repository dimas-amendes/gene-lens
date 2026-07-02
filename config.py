"""
Configuration — all paths and constants in one place.
Privacy note: no URLs are contacted at runtime. Downloads are a separate, explicit step.
"""
import os
import sys
from pathlib import Path

# ── Frozen-bundle awareness (PyInstaller) ────────────────────────────────────
# When shipped as a double-click executable, the app folder is read-only
# (macOS .app payload) or a volatile temp dir (one-file extraction), so we
# split two concerns:
#   BUNDLE_DIR  — where read-only bundled resources live (templates, static,
#                 sample, src reference data). PyInstaller extracts these to
#                 sys._MEIPASS; in dev it's just the project root.
#   _DATA_ROOT  — where we WRITE at runtime (databases, input, output). In a
#                 frozen build this must be a per-user, writable app-data dir;
#                 in dev it stays the project root so tests and the repo layout
#                 are untouched.
_FROZEN = bool(getattr(sys, "frozen", False))

if _FROZEN:
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
else:
    BUNDLE_DIR = Path(__file__).parent


def _user_data_root() -> Path:
    """Per-user writable directory for databases, input, and output.

    Override with GENE_LENS_DATA_HOME (also lets tests pin a tmp dir). Falls
    back to the platform-native app-data location.
    """
    override = os.environ.get("GENE_LENS_DATA_HOME")
    if override:
        # resolve() collapses any '..' so the override can't traverse out to an
        # unintended location where we'd then write databases/downloads.
        return Path(override).expanduser().resolve()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "GeneLens"
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "GeneLens"
    xdg = os.environ.get("XDG_DATA_HOME")
    # resolve() collapses '..' here too, matching the GENE_LENS_DATA_HOME path.
    base = Path(xdg).expanduser().resolve() if xdg else Path.home() / ".local" / "share"
    return base / "GeneLens"


# ── Directories ──────────────────────────────────────────────────────────────
_DATA_ROOT = _user_data_root() if _FROZEN else BUNDLE_DIR
DATA_DIR = _DATA_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
INPUT_DIR = _DATA_ROOT / "input"
OUTPUT_DIR = _DATA_ROOT / "output"
# Runtime-written too, so they must live under the writable root — in a frozen
# bundle Path(__file__).parent is read-only (.app) or volatile (onefile temp).
HISTORY_DIR = _DATA_ROOT / "history"
LOG_PATH = _DATA_ROOT / "dashboard.log"

# ── Database files ───────────────────────────────────────────────────────────
CLINVAR_TSV = DATA_DIR / "clinvar_alleles.tsv"
CLINVAR_GZ = DATA_DIR / "clinvar_alleles.tsv.gz"
PHARMGKB_ANNOTATIONS = DATA_DIR / "clinical_annotations.tsv"
PHARMGKB_ALLELES = DATA_DIR / "clinical_ann_alleles.tsv"
SNPEDIA_GFF = DATA_DIR / "snpedia.gff"

# ── Minimum valid sizes ──────────────────────────────────────────────────────
# A database file smaller than this is treated as corrupt/incomplete (not just
# "present"), so the UI flags it as missing and offers a re-download instead of
# silently accepting a broken copy. A healthy ClinVar SNP extract is ~380 MB and
# PharmGKB's TSVs are hundreds of KB, so these floors only catch broken files.
CLINVAR_MIN_VALID_BYTES = 10 * 1024 * 1024  # 10 MB
PHARMGKB_MIN_VALID_BYTES = 1024             # 1 KB per TSV

# ── Download URLs (used ONLY by download_databases.py) ───────────────────────
CLINVAR_DOWNLOAD_URL = (
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
)
PHARMGKB_DOWNLOAD_URL = (
    "https://api.pharmgkb.org/v1/download/file/data/clinicalAnnotations.zip"
)

# ── Analysis constants ───────────────────────────────────────────────────────
# PharmGKB evidence levels to include (CPIC guideline tiers)
PHARMGKB_MIN_EVIDENCE = {"1A", "1B", "2A", "2B"}

# ClinVar minimum gold stars for "notable uncertain significance"
CLINVAR_MIN_STARS_UNCERTAIN = 2

# Genome builds
SUPPORTED_BUILDS = {"GRCh37", "GRCh38"}
DEFAULT_BUILD = "GRCh37"
