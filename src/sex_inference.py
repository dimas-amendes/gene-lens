"""
Chromosomal sex inference from raw DNA data.

We count chromosome Y vs X SNP calls and emit 'M' / 'F' / None. This is a
*chromosomal* heuristic only — it does NOT determine clinical sex, gender
identity, or phenotypic sex. Known cases where the chromosomal call
diverges from clinical reality include:

  - Klinefelter (XXY) — chromosomally male here, often female-typical
    phenotype with variations
  - Turner (X0) — chromosomally female here, monosomy
  - Complete androgen insensitivity (XY with female phenotype)
  - XX male syndrome (SRY translocation)
  - Various mosaicism (XX/XY)

For hereditary-condition routing we treat the inferred value as a hint;
the user can always override via their profile. Always honor an explicit
user-provided `sex` over an inferred one.

Consumer chips typically include ~2000-4000 Y SNPs for male samples and
near-zero for female samples, which is why the threshold-on-Y heuristic
is sufficient for the >99% non-edge-case path.
"""


def infer_sex(genome_by_rsid: dict, threshold: int = 50) -> str | None:
    """Infer chromosomal sex from chromosome Y presence.

    Args:
        genome_by_rsid: dict mapping rsid -> {chromosome, position, genotype}
        threshold: minimum Y chromosome SNPs to call male (default 50)

    Returns:
        'M' if Y chromosome SNPs >= threshold (chromosomally male)
        'F' if Y chromosome SNPs < threshold but X exists (chromosomally female)
        None if insufficient data to determine

    NOTE: This is a chromosomal call, not a clinical one. Edge cases like
    XXY, X0, XY females, and mosaics will be miscalled. Treat the result
    as a hint; honor user-provided `sex` over the inferred value.
    """
    y_count = 0
    x_count = 0

    for data in genome_by_rsid.values():
        chrom = str(data.get("chromosome", ""))
        if chrom in ("Y", "24"):
            y_count += 1
        elif chrom in ("X", "23"):
            x_count += 1

    if y_count >= threshold:
        return "M"
    elif x_count >= 10:
        # Has X but no Y -> likely female
        return "F"
    else:
        return None
