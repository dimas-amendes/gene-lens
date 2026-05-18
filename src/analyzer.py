"""
Core analysis engine — matches user genome against all databases.

Produces structured results that feed into report generators.
No network access. No disk writes except final reports.
"""
from collections import defaultdict

from config import PHARMGKB_MIN_EVIDENCE
from src.snp_database import CURATED_SNPS


# ─── APOE Isoform Determination ──────────────────────────────────────────────

APOE_ISOFORMS = {
    # (rs429358, rs7412) -> (isoform, description, magnitude)
    ("TT", "TT"): ("E2/E2", "REDUCED Alzheimer risk. Possible risk of type III hyperlipoproteinemia. Cholesterol tends to run lower.", 1),
    ("TT", "CT"): ("E2/E3", "Reduced Alzheimer risk. Protective isoform.", 0),
    ("TT", "TC"): ("E2/E3", "Reduced Alzheimer risk. Protective isoform.", 0),
    ("TT", "CC"): ("E3/E3", "Most common genotype (~60% of the population). Baseline Alzheimer risk.", 0),
    ("CT", "CC"): ("E3/E4", "~3x risk of late-onset Alzheimer's. Regular exercise, Mediterranean diet, quality sleep, and cardiovascular control are the best preventive strategies.", 3),
    ("TC", "CC"): ("E3/E4", "~3x risk of late-onset Alzheimer's. Prevention: exercise, diet, sleep, cardiovascular health.", 3),
    ("CC", "CC"): ("E4/E4", "~12-15x risk of late-onset Alzheimer's. Aggressive prevention: daily exercise, strict Mediterranean diet, 7-8h sleep, cholesterol/blood pressure control, sustained cognitive and social engagement. Consult a neurologist.", 4),
    ("CT", "CT"): ("E2/E4", "Mixed risks — protective E2 + risk-conferring E4. Net effect uncertain, depends on other factors.", 2),
    ("CT", "TC"): ("E2/E4", "Mixed risks — protective E2 + risk-conferring E4.", 2),
    ("TC", "CT"): ("E2/E4", "Mixed risks — protective E2 + risk-conferring E4.", 2),
    ("TC", "TC"): ("E2/E4", "Mixed risks — protective E2 + risk-conferring E4.", 2),
}


def determine_apoe(genome_by_rsid: dict) -> dict | None:
    """Determine APOE isoform from rs429358 + rs7412."""
    rs429358 = genome_by_rsid.get("rs429358", {}).get("genotype")
    rs7412 = genome_by_rsid.get("rs7412", {}).get("genotype")

    if not rs429358 or not rs7412:
        return None

    key = (rs429358, rs7412)
    result = APOE_ISOFORMS.get(key)
    if not result:
        return None

    isoform, desc, magnitude = result
    return {
        "isoform": isoform,
        "description": desc,
        "magnitude": magnitude,
        "rs429358": rs429358,
        "rs7412": rs7412,
    }


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _match_genotype(variants: dict, genotype: str) -> dict | None:
    """Try to match a genotype against variant definitions, including reverse complement."""
    result = variants.get(genotype)
    if result:
        return result
    if len(genotype) == 2:
        return variants.get(genotype[::-1])
    return None


def _classify_zygosity(finding: dict) -> tuple[str, str]:
    """Determine clinical impact based on zygosity and inheritance pattern."""
    inheritance = (finding.get("inheritance") or "").lower()
    is_hom = finding["is_homozygous"]
    is_het = finding["is_heterozygous"]

    if is_hom:
        return "AFFECTED", "Homozygous for variant allele"
    if is_het:
        if "recessive" in inheritance:
            return "CARRIER", "Heterozygous carrier (autosomal recessive)"
        if "dominant" in inheritance:
            return "AFFECTED", "Heterozygous (autosomal dominant — one copy sufficient)"
        if "x-linked" in inheritance:
            return "CARRIER/AT_RISK", "X-linked variant (impact depends on sex)"
        return "HETEROZYGOUS", "Heterozygous (inheritance pattern not specified)"
    return "UNKNOWN", "Zygosity unclear"


# ─── Lifestyle / Health Analysis ──────────────────────────────────────────────

def analyze_lifestyle(genome_by_rsid: dict, pharmgkb: dict) -> dict:
    """Analyze genome against curated SNP database + PharmGKB."""
    results = {
        "findings": [],
        "pharmgkb_findings": [],
        "by_category": defaultdict(list),
        "summary": {
            "total_snps": len(genome_by_rsid),
            "analyzed_snps": 0,
            "high_impact": 0,
            "moderate_impact": 0,
            "low_impact": 0,
        },
    }

    # 1. Curated SNP database
    for rsid, info in CURATED_SNPS.items():
        if rsid not in genome_by_rsid:
            continue
        genotype = genome_by_rsid[rsid]["genotype"]
        variant_info = _match_genotype(info["variants"], genotype)
        if not variant_info:
            continue

        finding = {
            "rsid": rsid,
            "gene": info["gene"],
            "category": info["category"],
            "genotype": genotype,
            "status": variant_info["status"],
            "description": variant_info["desc"],
            "magnitude": variant_info["magnitude"],
        }
        results["findings"].append(finding)
        results["by_category"][info["category"]].append(finding)
        results["summary"]["analyzed_snps"] += 1

        mag = variant_info["magnitude"]
        if mag >= 3:
            results["summary"]["high_impact"] += 1
        elif mag >= 2:
            results["summary"]["moderate_impact"] += 1
        elif mag >= 1:
            results["summary"]["low_impact"] += 1

    # 2. PharmGKB drug-gene interactions
    for rsid, info in pharmgkb.items():
        if rsid not in genome_by_rsid:
            continue
        if info["level"] not in PHARMGKB_MIN_EVIDENCE:
            continue

        genotype = genome_by_rsid[rsid]["genotype"]
        annotation = info["genotypes"].get(genotype)
        if not annotation and len(genotype) == 2:
            annotation = info["genotypes"].get(genotype[::-1])
        if not annotation:
            continue

        results["pharmgkb_findings"].append({
            "rsid": rsid,
            "gene": info["gene"],
            "drugs": info["drugs"],
            "genotype": genotype,
            "annotation": annotation,
            "level": info["level"],
            "category": info["category"],
        })

    # 3. APOE isoform (combined rs429358 + rs7412)
    apoe = determine_apoe(genome_by_rsid)
    if apoe:
        results["apoe"] = apoe
        # Replace rs429358 finding description with combined isoform
        for f in results["findings"]:
            if f["rsid"] == "rs429358":
                f["description"] = f"APOE {apoe['isoform']} (rs429358={apoe['rs429358']}, rs7412={apoe['rs7412']}): {apoe['description']}"
                f["magnitude"] = apoe["magnitude"]
                break

    # Sort by impact
    results["findings"].sort(key=lambda x: -x["magnitude"])
    results["pharmgkb_findings"].sort(key=lambda x: x["level"])

    return results


# ─── Disease Risk Analysis ────────────────────────────────────────────────────

def analyze_disease_risk(genome_by_position: dict, clinvar: dict) -> tuple[dict, dict]:
    """Analyze genome against ClinVar for pathogenic variants.

    Returns (findings_by_category, stats).
    """
    if not clinvar:
        return None, None

    findings = {
        "pathogenic": [],
        "likely_pathogenic": [],
        "risk_factor": [],
        "drug_response": [],
        "protective": [],
        "other_significant": [],
    }
    stats = {
        "total_clinvar_positions": len(clinvar),
        "matched": 0,
        "pathogenic_count": 0,
        "likely_pathogenic_count": 0,
    }

    for pos_key, entries in clinvar.items():
        if pos_key not in genome_by_position:
            continue

        user = genome_by_position[pos_key]
        user_genotype = user["genotype"]

        for entry in entries:
            ref = entry["ref"]
            alt = entry["alt"]

            # Check if user has the variant allele
            has_ref_only = user_genotype == ref + ref
            if has_ref_only:
                continue

            has_variant = alt in user_genotype
            if not has_variant:
                continue

            stats["matched"] += 1
            is_homozygous = user_genotype == alt + alt
            is_heterozygous = has_variant and not is_homozygous

            finding = {
                **entry,
                "rsid": user["rsid"],
                "user_genotype": user_genotype,
                "is_homozygous": is_homozygous,
                "is_heterozygous": is_heterozygous,
            }

            # Add zygosity classification
            status, desc = _classify_zygosity(finding)
            finding["zygosity_status"] = status
            finding["zygosity_description"] = desc

            # Categorize
            sig = entry["clinical_significance"].lower()
            if "pathogenic" in sig and "likely" not in sig and "conflict" not in sig:
                findings["pathogenic"].append(finding)
                stats["pathogenic_count"] += 1
            elif "likely pathogenic" in sig or "likely_pathogenic" in sig:
                findings["likely_pathogenic"].append(finding)
                stats["likely_pathogenic_count"] += 1
            elif "risk factor" in sig or "risk_factor" in sig:
                findings["risk_factor"].append(finding)
            elif "drug response" in sig or "drug_response" in sig:
                findings["drug_response"].append(finding)
            elif "protective" in sig:
                findings["protective"].append(finding)
            elif "association" in sig or "affects" in sig:
                findings["other_significant"].append(finding)

    # Sort by confidence
    for category in findings.values():
        category.sort(key=lambda x: (-x.get("gold_stars", 0), x.get("gene", "")))

    return findings, stats
