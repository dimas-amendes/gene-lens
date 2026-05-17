"""
Configuration — all paths and constants in one place.
Privacy note: no URLs are contacted at runtime. Downloads are a separate, explicit step.
"""
from pathlib import Path

# ── Directories ──────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
INPUT_DIR = ROOT_DIR / "input"
OUTPUT_DIR = ROOT_DIR / "output"

# ── Database files ───────────────────────────────────────────────────────────
CLINVAR_TSV = DATA_DIR / "clinvar_alleles.tsv"
CLINVAR_GZ = DATA_DIR / "clinvar_alleles.tsv.gz"
PHARMGKB_ANNOTATIONS = DATA_DIR / "clinical_annotations.tsv"
PHARMGKB_ALLELES = DATA_DIR / "clinical_ann_alleles.tsv"
SNPEDIA_GFF = DATA_DIR / "snpedia.gff"

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
