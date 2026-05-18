"""
DNA raw data parsers — supports 23andMe, AncestryDNA, MyHeritage, and generic formats.

All parsers produce a unified dict: {rsid: {chromosome, position, genotype}}
where genotype is always a 2-char string like "AG", "CC", "--".
"""
from pathlib import Path


def _open_file(path: Path):
    """Open a file, handling .gz transparently."""
    import gzip
    if str(path).endswith(".gz"):
        return gzip.open(str(path), "rt", encoding="utf-8", errors="replace")
    return open(path, "r", encoding="utf-8", errors="replace")


def detect_format(path: Path) -> str:
    """Auto-detect raw DNA file format by reading the header."""
    with _open_file(path) as f:
        header_lines = []
        first_data_line = None
        for line in f:
            if line.startswith("#"):
                header_lines.append(line)
            elif line.strip():
                first_data_line = line.strip()
                break

    header_text = "".join(header_lines).lower()

    if "23andme" in header_text:
        return "23andme"
    if "ancestrydna" in header_text or "ancestry" in header_text:
        return "ancestry"
    if "myheritage" in header_text:
        return "myheritage"

    # Detect CSV with RSID header (Genera, MeuDNA, MyHeritage)
    if first_data_line and "," in first_data_line:
        upper = first_data_line.upper()
        if "RSID" in upper or "RS" in upper.split(",")[0]:
            return "genera_csv"

    # Detect by column count (tab-separated)
    if first_data_line:
        parts = first_data_line.split("\t")
        if len(parts) == 5:
            return "ancestry"  # 5 columns = rsid, chr, pos, allele1, allele2
        if len(parts) == 4:
            return "23andme"   # 4 columns = rsid, chr, pos, genotype

    return "generic"


def parse_genera_csv(path: Path) -> dict:
    """Parse Genera/MeuDNA CSV format (Brazilian DTC services).
    Format: RSID,CHROMOSOME,POSITION,RESULT (comma-separated with header)
    Also handles .csv.gz files.

    Y / MT / male-X SNPs come HEMIZYGOUS — a single letter (e.g. "G")
    rather than a pair ("GG"). The old `len(result) < 2` filter dropped
    every one of those, which made `infer_sex()` miscall males as F
    (Y count fell below threshold because the parser had silently nuked
    them). We now accept any non-empty, non-no-call genotype regardless
    of length.
    """
    import csv
    genome = {}
    with _open_file(path) as f:
        lines = (line for line in f if not line.startswith("#"))
        reader = csv.DictReader(lines)
        for row in reader:
            rsid = row.get("RSID", row.get("rsid", ""))
            chrom = row.get("CHROMOSOME", row.get("chromosome", ""))
            pos = row.get("POSITION", row.get("position", ""))
            result = row.get("RESULT", row.get("result", ""))
            if not rsid.startswith("rs") or not result or result in ("--", "-", "0", "00"):
                continue
            genome[rsid] = {
                "chromosome": chrom,
                "position": pos,
                "genotype": result,
            }
    return genome


def parse_23andme(path: Path) -> dict:
    """Parse 23andMe raw data format.
    Format: rsid<TAB>chromosome<TAB>position<TAB>genotype
    """
    genome = {}
    with _open_file(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) < 4:
                continue
            rsid, chrom, pos, genotype = parts[0], parts[1], parts[2], parts[3]
            # Skip no-calls and internal IDs
            if genotype == "--" or not rsid.startswith("rs"):
                continue
            genome[rsid] = {
                "chromosome": chrom,
                "position": pos,
                "genotype": genotype,
            }
    return genome


def parse_ancestry(path: Path) -> dict:
    """Parse AncestryDNA raw data format.
    Format: rsid<TAB>chromosome<TAB>position<TAB>allele1<TAB>allele2
    """
    genome = {}
    with _open_file(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) < 5:
                continue
            rsid, chrom, pos, a1, a2 = parts[0], parts[1], parts[2], parts[3], parts[4]
            if a1 == "0" or a2 == "0" or not rsid.startswith("rs"):
                continue
            genome[rsid] = {
                "chromosome": chrom,
                "position": pos,
                "genotype": a1 + a2,
            }
    return genome


def parse_myheritage(path: Path) -> dict:
    """Parse MyHeritage DNA format (CSV with header row)."""
    import csv
    genome = {}
    with _open_file(path) as f:
        # Skip comment lines
        lines = (line for line in f if not line.startswith("#"))
        reader = csv.DictReader(lines)
        for row in reader:
            rsid = row.get("RSID", row.get("rsid", ""))
            chrom = row.get("CHROMOSOME", row.get("chromosome", ""))
            pos = row.get("POSITION", row.get("position", ""))
            result = row.get("RESULT", row.get("result", ""))
            # Same hemizygous-Y caveat as parse_genera_csv — don't filter
            # single-letter results, they're real calls on Y/MT/male-X.
            if not rsid.startswith("rs") or not result or result in ("--", "-", "0", "00"):
                continue
            genome[rsid] = {
                "chromosome": chrom,
                "position": pos,
                "genotype": result,
            }
    return genome


def parse_generic(path: Path) -> dict:
    """Fallback parser — tries tab-separated with 4+ columns."""
    genome = {}
    with _open_file(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                rsid = parts[0]
                if not rsid.startswith("rs"):
                    continue
                chrom, pos = parts[1], parts[2]
                genotype = parts[3] if len(parts) == 4 else parts[3] + parts[4]
                if genotype in ("--", "00", "0"):
                    continue
                genome[rsid] = {
                    "chromosome": chrom,
                    "position": pos,
                    "genotype": genotype,
                }
    return genome


# Parser dispatch
_PARSERS = {
    "23andme": parse_23andme,
    "ancestry": parse_ancestry,
    "myheritage": parse_myheritage,
    "genera_csv": parse_genera_csv,
    "generic": parse_generic,
}


def load_genome(path: Path, force_format: str = None) -> tuple[dict, dict, str]:
    """Load genome file and return (by_rsid, by_position, detected_format).

    by_rsid:     {rsid: {chromosome, position, genotype}}
    by_position: {"chr:pos": {rsid, genotype}}
    """
    fmt = force_format or detect_format(path)
    parser = _PARSERS.get(fmt, parse_generic)

    genome_by_rsid = parser(path)

    # Build position index for ClinVar matching
    genome_by_position = {}
    for rsid, info in genome_by_rsid.items():
        pos_key = f"{info['chromosome']}:{info['position']}"
        genome_by_position[pos_key] = {
            "rsid": rsid,
            "genotype": info["genotype"],
        }

    return genome_by_rsid, genome_by_position, fmt
