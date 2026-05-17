"""
Inferencia de sexo biologico a partir de dados brutos de DNA.

Se o arquivo contém calls consistentes no cromossomo Y, o individuo
é biologicamente masculino (XY). Caso contrário, feminino (XX).

Chips de consumo tipicamente incluem ~2000-4000 SNPs no cromossomo Y
para amostras masculinas e zero para femininas.
"""


def infer_sex(genome_by_rsid: dict, threshold: int = 50) -> str | None:
    """Infer biological sex from chromosome Y presence.

    Args:
        genome_by_rsid: dict mapping rsid -> {chromosome, position, genotype}
        threshold: minimum Y chromosome SNPs to call male (default 50)

    Returns:
        'M' if Y chromosome SNPs >= threshold
        'F' if Y chromosome SNPs < threshold but X exists
        None if insufficient data to determine
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
