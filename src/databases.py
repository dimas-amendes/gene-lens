"""
Database loaders for ClinVar and PharmGKB.

All data is loaded from local TSV files — no network access.
Builds in-memory indexes for O(1) lookup by rsID or chromosome:position.
"""
import csv
import sys
from pathlib import Path
from collections import defaultdict

from config import (
    CLINVAR_TSV, PHARMGKB_ANNOTATIONS, PHARMGKB_ALLELES,
    PHARMGKB_MIN_EVIDENCE,
)


# Startup log language. Default EN; the dashboard sets this via set_lang()
# when the user launches with `--lang pt`.
_lang = "en"

_MSGS = {
    "en": {
        "clinvar_missing": "[SKIP] ClinVar not found at {path}",
        "clinvar_loading": "Loading ClinVar from {name}...",
        "clinvar_loaded": "{count:,} ClinVar entries loaded -> {snps:,} SNP positions indexed",
        "pharmgkb_missing": "[SKIP] PharmGKB files not found",
        "pharmgkb_loading": "Loading PharmGKB annotations...",
        "pharmgkb_loaded": "{count:,} drug-gene interactions loaded",
    },
    "pt": {
        "clinvar_missing": "[PULAR] ClinVar não encontrado em {path}",
        "clinvar_loading": "Carregando ClinVar de {name}...",
        "clinvar_loaded": "{count:,} entradas ClinVar carregadas -> {snps:,} posições SNP indexadas",
        "pharmgkb_missing": "[PULAR] Arquivos PharmGKB não encontrados",
        "pharmgkb_loading": "Carregando anotações PharmGKB...",
        "pharmgkb_loaded": "{count:,} interações droga-gene carregadas",
    },
}


def set_lang(code: str):
    """Set the language for startup/DB log messages. Accepts 'en' or 'pt'."""
    global _lang
    _lang = "pt" if (code or "").lower().startswith("pt") else "en"


def _t(key: str, **kwargs) -> str:
    template = _MSGS.get(_lang, _MSGS["en"]).get(key, key)
    return template.format(**kwargs)


def _safe_int(val: str) -> int:
    """Parse int from string, returning 0 for any non-numeric value."""
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


def load_clinvar(path: Path = None) -> dict:
    """Load ClinVar alleles TSV and build position-keyed index.

    Returns: {"chr:pos": [ClinVarEntry, ...]}
    where ClinVarEntry is a dict with variant details.
    """
    path = path or CLINVAR_TSV
    if not path.exists():
        print(f"  {_t('clinvar_missing', path=path)}")
        return {}

    print(f"  {_t('clinvar_loading', name=path.name)}")
    index = defaultdict(list)
    count = 0

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            count += 1
            chrom = row.get("chrom", "")
            pos = row.get("pos", "")
            ref = row.get("ref", "")
            alt = row.get("alt", "")

            # Only process true SNPs (single nucleotide variants)
            # Indels from 23andMe data cause false positives
            if len(ref) != 1 or len(alt) != 1:
                continue

            pos_key = f"{chrom}:{pos}"
            index[pos_key].append({
                "chrom": chrom,
                "pos": pos,
                "ref": ref,
                "alt": alt,
                "gene": row.get("symbol", ""),
                "clinical_significance": row.get("clinical_significance", ""),
                "clinical_significance_ordered": row.get("clinical_significance_ordered", ""),
                "review_status": row.get("review_status", ""),
                "gold_stars": _safe_int(row.get("gold_stars", "0")),
                "traits": row.get("all_traits", ""),
                "inheritance": row.get("inheritance_modes", ""),
                "hgvs_c": row.get("hgvs_c", ""),
                "hgvs_p": row.get("hgvs_p", ""),
                "molecular_consequence": row.get("molecular_consequence", ""),
                "pmids": row.get("all_pmids", ""),
                "xrefs": row.get("xrefs", ""),
                "age_of_onset": row.get("age_of_onset", ""),
                "prevalence": row.get("prevalence", ""),
                "submitters": row.get("all_submitters", ""),
                "last_evaluated": row.get("last_evaluated", ""),
            })

    snp_positions = len(index)
    print(f"  {_t('clinvar_loaded', count=count, snps=snp_positions)}")
    return dict(index)


def load_pharmgkb(
    annotations_path: Path = None,
    alleles_path: Path = None,
) -> dict:
    """Load PharmGKB clinical annotations with genotype-specific text.

    Returns: {rsid: {gene, drugs, phenotype, level, category, genotypes: {genotype: text}}}
    """
    annotations_path = annotations_path or PHARMGKB_ANNOTATIONS
    alleles_path = alleles_path or PHARMGKB_ALLELES

    if not annotations_path.exists() or not alleles_path.exists():
        print(f"  {_t('pharmgkb_missing')}")
        return {}

    print(f"  {_t('pharmgkb_loading')}")

    # Step 1: Load annotation metadata
    annotation_meta = {}
    with open(annotations_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            ann_id = row.get("Clinical Annotation ID", "")
            variant = row.get("Variant/Haplotypes", "")
            if variant.startswith("rs"):
                annotation_meta[ann_id] = {
                    "rsid": variant,
                    "gene": row.get("Gene", ""),
                    "drugs": row.get("Drug(s)", ""),
                    "phenotype": row.get("Phenotype(s)", ""),
                    "level": row.get("Level of Evidence", ""),
                    "category": row.get("Phenotype Category", ""),
                }

    # Step 2: Load genotype-specific allele annotations
    pharmgkb = {}
    with open(alleles_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            ann_id = row.get("Clinical Annotation ID", "")
            if ann_id not in annotation_meta:
                continue

            meta = annotation_meta[ann_id]
            rsid = meta["rsid"]
            genotype = row.get("Genotype/Allele", "")

            if rsid not in pharmgkb:
                pharmgkb[rsid] = {
                    "gene": meta["gene"],
                    "drugs": meta["drugs"],
                    "phenotype": meta["phenotype"],
                    "level": meta["level"],
                    "category": meta["category"],
                    "genotypes": {},
                }
            pharmgkb[rsid]["genotypes"][genotype] = row.get("Annotation Text", "")

    print(f"  {_t('pharmgkb_loaded', count=len(pharmgkb))}")
    return pharmgkb
