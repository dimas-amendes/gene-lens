"""
Composite Risk Index (CRI) — a transparent, honest alternative to a calibrated
Polygenic Risk Score.

Why not a "real" PRS?
---------------------
True PRS implementations require:
  - Hundreds-to-thousands of SNPs with effect-size betas
  - Ancestry-matched reference distributions for percentile calibration
  - Quality control (LD pruning, imputation, allele alignment)

Without those pieces, a "PRS" is misleading at best and harmful at worst (the
user trusts a calibrated number that is in fact pseudo-calibrated). Consumer
chips also miss the bulk of PRS-relevant variants.

What this module does instead
-----------------------------
For a handful of conditions where multiple well-replicated risk variants exist
in consumer-chip coverage, it counts how many *risk-allele copies* the user
carries across the panel:

    score = sum over SNPs of (#copies of the risk allele)

That's a tally, not a probability. It's framed in the UI as "you carry N of K
known risk-allele copies for condition X" — directional, not diagnostic.
A percentile is intentionally NOT computed.

Each panel is small (5-10 SNPs) and uses only variants with magnitude ≥ 2.5
in published replications. The intent is to surface aggregate signal that the
existing per-SNP view hides.
"""
from __future__ import annotations

from dataclasses import dataclass, field


# Each panel lists (rsid, risk_allele, gene, brief_effect).
# Risk allele = the allele associated with INCREASED risk in published studies.
# Sources: GWAS Catalog (https://www.ebi.ac.uk/gwas/), well-replicated hits only.
PRS_PANELS = {
    "type2_diabetes": {
        "name_pt": "Diabetes Tipo 2",
        "name_en": "Type 2 Diabetes",
        "snps": [
            ("rs7903146", "T", "TCF7L2", "transcription factor — strongest common T2D variant"),
            ("rs9939609", "A", "FTO", "obesity/T2D risk via adiposity"),
            ("rs1801282", "C", "PPARG", "Pro12Ala — C allele higher risk"),
            ("rs5219",    "T", "KCNJ11", "K+ channel — beta-cell insulin secretion"),
            ("rs13266634","C", "SLC30A8", "zinc transporter in beta cells"),
            ("rs10811661","T", "CDKN2A/B", "near 9p21 — beta-cell proliferation"),
            ("rs7754840", "C", "CDKAL1", "beta-cell function"),
        ],
    },
    "coronary_heart_disease": {
        "name_pt": "Doença Coronariana",
        "name_en": "Coronary Heart Disease",
        "snps": [
            ("rs10757278", "G", "CDKN2BAS (9p21)", "strongest non-lipid CHD locus"),
            ("rs1333049",  "C", "CDKN2BAS (9p21)", "9p21 region — myocardial infarction"),
            ("rs10455872", "G", "LPA", "lipoprotein(a) — independent CHD risk"),
            ("rs6725887",  "C", "WDR12", "early-onset MI"),
            ("rs17465637", "C", "MIA3", "CHD susceptibility"),
            ("rs429358",   "C", "APOE", "APOE4 allele — lipid/CHD risk"),
        ],
    },
    "alzheimers": {
        "name_pt": "Alzheimer (início tardio)",
        "name_en": "Alzheimer's (late-onset)",
        "snps": [
            ("rs429358",   "C", "APOE", "APOE4 — strongest common AD risk allele"),
            ("rs11136000", "T", "CLU", "clusterin — amyloid clearance"),
            ("rs744373",   "G", "BIN1", "second-strongest AD locus after APOE"),
            ("rs3851179",  "T", "PICALM", "synaptic vesicle / amyloid pathway"),
            ("rs9331896",  "C", "CLU", "clusterin secondary signal"),
        ],
    },
    "obesity": {
        "name_pt": "Obesidade (IMC)",
        "name_en": "Obesity (BMI)",
        "snps": [
            ("rs9939609",  "A", "FTO", "strongest common BMI variant"),
            ("rs17782313", "C", "MC4R", "near MC4R — melanocortin signaling"),
            ("rs6548238",  "C", "TMEM18", "BMI in adults and children"),
            ("rs10938397", "G", "GNPDA2", "BMI replication hit"),
            ("rs2867125",  "C", "TMEM18", "TMEM18 secondary"),
        ],
    },
}


@dataclass
class PRSResult:
    """Composite risk index for a single condition."""
    key: str
    name_pt: str
    name_en: str
    score: int           # total risk-allele copies carried
    max_score: int       # 2 × number of SNPs *available in user's chip*
    snps_used: int       # SNPs from the panel actually genotyped
    snps_total: int      # SNPs in the panel
    details: list[dict] = field(default_factory=list)

    @property
    def coverage(self) -> float:
        return self.snps_used / self.snps_total if self.snps_total else 0.0

    @property
    def ratio(self) -> float:
        """Risk-allele copies divided by max possible *given coverage*."""
        return self.score / self.max_score if self.max_score else 0.0

    @property
    def band(self) -> str:
        """Three-band qualitative label.

        Bands are intentionally based on the *ratio* of risk alleles carried
        relative to the panel ceiling — not a population percentile, which
        would require ancestry-matched calibration we don't have.
        """
        if self.snps_used < 3:
            return "insufficient"
        r = self.ratio
        if r >= 0.6:
            return "elevated"
        if r >= 0.35:
            return "average"
        return "below_average"


def _count_risk_alleles(genotype: str, risk_allele: str) -> int:
    """Return how many copies of `risk_allele` appear in a 2-letter genotype.

    Consumer chips can occasionally report indels ('DD', 'II') or single
    characters — anything not a 2-letter base call returns 0 to avoid
    polluting the count with garbage.
    """
    if not genotype or len(genotype) != 2:
        return 0
    if not all(c in "ACGT" for c in genotype.upper()):
        return 0
    return sum(1 for c in genotype.upper() if c == risk_allele.upper())


def compute_prs(genome_by_rsid: dict) -> dict:
    """Run every panel against the user's genome.

    Returns a list of PRSResult-as-dict (JSON-safe for history persistence).
    """
    results = []
    for key, panel in PRS_PANELS.items():
        snps = panel["snps"]
        details = []
        score = 0
        snps_used = 0
        for rsid, risk_allele, gene, effect in snps:
            entry = {
                "rsid": rsid,
                "gene": gene,
                "risk_allele": risk_allele,
                "effect": effect,
                "genotype": None,
                "copies": 0,
                "present": False,
            }
            if rsid in genome_by_rsid:
                gt = genome_by_rsid[rsid].get("genotype", "")
                entry["genotype"] = gt
                entry["copies"] = _count_risk_alleles(gt, risk_allele)
                entry["present"] = True
                snps_used += 1
                score += entry["copies"]
            details.append(entry)

        res = PRSResult(
            key=key,
            name_pt=panel["name_pt"],
            name_en=panel["name_en"],
            score=score,
            max_score=snps_used * 2,
            snps_used=snps_used,
            snps_total=len(snps),
            details=details,
        )
        results.append({
            "key": res.key,
            "name_pt": res.name_pt,
            "name_en": res.name_en,
            "score": res.score,
            "max_score": res.max_score,
            "snps_used": res.snps_used,
            "snps_total": res.snps_total,
            "coverage": res.coverage,
            "ratio": res.ratio,
            "band": res.band,
            "details": res.details,
        })
    return {"panels": results}
