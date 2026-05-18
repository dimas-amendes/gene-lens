"""
Per-panel coverage report.

Consumer chips genotype only a subset of human variants. When a chip happens
to miss key markers (e.g. only one of the two APOE SNPs), Gene Lens can still
produce a result but with degraded confidence. This module makes that explicit
so users can see *why* a finding might be unreliable instead of trusting an
answer that was silently extrapolated from partial data.

Coverage is computed by asking each panel: "of the rsids you depend on, how
many actually appear in this user's genome?" — then bucketing the ratio into
a qualitative confidence band.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.ancestry import AIMS
from src.phenotype import (
    BALDNESS_SNPS,
    EYE_SNPS,
    FRECKLE_SNPS,
    HAIR_SNPS,
    TEXTURE_SNPS,
)
from src.snp_database import CURATED_SNPS
from src.wellness_panels import ALL_PANELS
from src.wellness_i18n import PANEL_NAMES_EN


# APOE only resolves to an isoform when BOTH SNPs are called.
APOE_SNPS = ["rs429358", "rs7412"]


@dataclass
class PanelCoverage:
    """Coverage of a single analytical panel against a user's genome."""
    key: str
    name_pt: str
    name_en: str
    group: str  # 'core' | 'ancestry' | 'wellness' | 'pharmaco'
    present: int
    total: int
    missing: list[str] = field(default_factory=list)

    @property
    def ratio(self) -> float:
        return self.present / self.total if self.total else 0.0

    @property
    def confidence(self) -> str:
        """Three-band confidence: high / partial / low.

        Bands are intentionally coarse — users don't need a percentage,
        they need to know whether to trust the result downstream.
        """
        r = self.ratio
        if r >= 0.8:
            return "high"
        if r >= 0.4:
            return "partial"
        return "low"


def _coverage_for(key: str, name_pt: str, name_en: str, group: str,
                  required_rsids, genome_by_rsid: dict) -> PanelCoverage:
    rsids = list(required_rsids)
    missing = [r for r in rsids if r not in genome_by_rsid]
    return PanelCoverage(
        key=key,
        name_pt=name_pt,
        name_en=name_en,
        group=group,
        present=len(rsids) - len(missing),
        total=len(rsids),
        # Cap the displayed missing list — long arrays just clutter the UI
        # and the count alone is what drives the confidence band.
        missing=missing[:10],
    )


def compute_coverage(genome_by_rsid: dict) -> dict:
    """Return per-panel coverage plus an overall summary.

    `genome_by_rsid` is the same dict the analyzers consume — rsid -> dict
    with at least a 'genotype' key. Only rsid membership matters here, so we
    treat it as a plain set lookup.
    """
    panels: list[PanelCoverage] = []

    # ── Core identity panels ──────────────────────────────────────────────
    panels.append(_coverage_for(
        "apoe", "APOE (isoforma)", "APOE (isoform)", "core",
        APOE_SNPS, genome_by_rsid,
    ))
    panels.append(_coverage_for(
        "eye_color", "Cor dos olhos (IrisPlex)", "Eye color (IrisPlex)", "core",
        EYE_SNPS.keys(), genome_by_rsid,
    ))
    panels.append(_coverage_for(
        "hair_color", "Cor do cabelo", "Hair color", "core",
        HAIR_SNPS.keys(), genome_by_rsid,
    ))
    panels.append(_coverage_for(
        "hair_texture", "Textura do cabelo", "Hair texture", "core",
        TEXTURE_SNPS.keys(), genome_by_rsid,
    ))
    panels.append(_coverage_for(
        "freckles", "Sardas", "Freckles", "core",
        FRECKLE_SNPS.keys(), genome_by_rsid,
    ))
    panels.append(_coverage_for(
        "baldness", "Calvicie", "Baldness", "core",
        BALDNESS_SNPS.keys(), genome_by_rsid,
    ))

    # ── Ancestry ──────────────────────────────────────────────────────────
    panels.append(_coverage_for(
        "ancestry_aims", "Ancestralidade (AIMs)", "Ancestry (AIMs)", "ancestry",
        AIMS.keys(), genome_by_rsid,
    ))

    # ── Pharmacogenomics (curated) ────────────────────────────────────────
    panels.append(_coverage_for(
        "pharmaco_curated",
        "Farmacogenomica curada", "Curated pharmacogenomics", "pharmaco",
        CURATED_SNPS.keys(), genome_by_rsid,
    ))

    # ── Wellness panels (14) ──────────────────────────────────────────────
    for key, info in ALL_PANELS.items():
        panels.append(_coverage_for(
            f"wellness_{key}",
            info["name_full"],
            PANEL_NAMES_EN.get(key, info["name_full"]),
            "wellness",
            info["snps"].keys(),
            genome_by_rsid,
        ))

    # ── Aggregate summary ─────────────────────────────────────────────────
    total = sum(p.total for p in panels)
    present = sum(p.present for p in panels)
    by_confidence = {"high": 0, "partial": 0, "low": 0}
    for p in panels:
        by_confidence[p.confidence] += 1

    # Serialize to plain dicts so the result survives JSON round-trips
    # (history persistence saves the full result as JSON).
    panels_serialized = [
        {
            "key": p.key,
            "name_pt": p.name_pt,
            "name_en": p.name_en,
            "group": p.group,
            "present": p.present,
            "total": p.total,
            "missing": p.missing,
            "ratio": p.ratio,
            "confidence": p.confidence,
        }
        for p in panels
    ]

    return {
        "panels": panels_serialized,
        "summary": {
            "panels_total": len(panels),
            "panels_high": by_confidence["high"],
            "panels_partial": by_confidence["partial"],
            "panels_low": by_confidence["low"],
            "markers_present": present,
            "markers_total": total,
            "overall_ratio": (present / total) if total else 0.0,
        },
    }
