"""
Detect installation status of optional and required components.

Pure introspection — never executes installers. The settings page surfaces
the commands a user should run themselves.
"""
from __future__ import annotations

import importlib.util
import platform
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from config import (
    CLINVAR_TSV,
    PHARMGKB_ANNOTATIONS,
    PHARMGKB_ALLELES,
)


@dataclass
class ComponentStatus:
    key: str
    name: str
    required: bool
    installed: bool
    detail: str = ""
    install_commands: list[str] = field(default_factory=list)
    docs_url: str = ""


def _file_info(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, ""
    size_mb = path.stat().st_size / (1024 * 1024)
    mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
    return True, f"{size_mb:.1f} MB · updated {mtime}"


def check_clinvar() -> ComponentStatus:
    ok, detail = _file_info(CLINVAR_TSV)
    return ComponentStatus(
        key="clinvar",
        name="ClinVar database",
        required=True,
        installed=ok,
        detail=detail or f"missing at {CLINVAR_TSV.relative_to(CLINVAR_TSV.parent.parent)}",
        install_commands=["python download_databases.py --clinvar"],
        docs_url="https://www.ncbi.nlm.nih.gov/clinvar/",
    )


def check_pharmgkb() -> ComponentStatus:
    ann_ok = PHARMGKB_ANNOTATIONS.exists()
    all_ok = PHARMGKB_ALLELES.exists()
    if ann_ok and all_ok:
        size_mb = (
            PHARMGKB_ANNOTATIONS.stat().st_size + PHARMGKB_ALLELES.stat().st_size
        ) / (1024 * 1024)
        detail = f"{size_mb:.1f} MB · both files present"
    else:
        missing = []
        if not ann_ok:
            missing.append("clinical_annotations.tsv")
        if not all_ok:
            missing.append("clinical_ann_alleles.tsv")
        detail = f"missing: {', '.join(missing)}"
    return ComponentStatus(
        key="pharmgkb",
        name="PharmGKB database",
        required=False,
        installed=ann_ok and all_ok,
        detail=detail,
        install_commands=[
            "# Free account required at https://www.pharmgkb.org/",
            "# Download 'Clinical Annotations' ZIP and extract to data/",
            "python download_databases.py --pharmgkb  # prints instructions",
        ],
        docs_url="https://www.pharmgkb.org/downloads",
    )


def is_argos_model_installed() -> bool:
    """True only when both the package AND the en->pt model are usable.

    Settings shows two states: package-only (needs model) and fully ready.
    Analyses in PT mode should be gated on this returning True.
    """
    try:
        import argostranslate.translate  # type: ignore
        installed = argostranslate.translate.get_installed_languages()
        codes = {l.code for l in installed}
        return "en" in codes and "pt" in codes
    except Exception:
        return False


def check_argos_translate() -> ComponentStatus:
    spec = importlib.util.find_spec("argostranslate")
    pkg_installed = spec is not None
    model_installed = pkg_installed and is_argos_model_installed()
    version = ""
    if pkg_installed:
        try:
            import argostranslate  # type: ignore
            version = getattr(argostranslate, "__version__", "installed")
        except Exception:
            version = "installed"

    if model_installed:
        detail = f"version {version} · en->pt model ready"
    elif pkg_installed:
        detail = f"version {version} · model NOT installed (PT-BR analyses need it)"
    else:
        detail = "not installed in this Python environment"

    return ComponentStatus(
        key="argos",
        name="Argos Translate (PT-EN neural translation)",
        required=False,
        # Treat "installed" as fully usable, so the green checkmark in the
        # UI only appears when PT-BR analyses will actually get neural text.
        installed=model_installed,
        detail=detail,
        install_commands=["pip install argostranslate"],
        docs_url="https://www.argosopentech.com/",
    )


def check_ollama() -> ComponentStatus:
    binary = shutil.which("ollama")
    if not binary:
        return ComponentStatus(
            key="ollama",
            name="Ollama (local AI interpretation)",
            required=False,
            installed=False,
            detail="binary not found in PATH",
            install_commands=_ollama_install_commands(),
            docs_url="https://ollama.com/download",
        )

    # Detect installed models
    models = _list_ollama_models()
    if models:
        detail = f"running · models: {', '.join(models[:3])}"
        if len(models) > 3:
            detail += f" (+{len(models) - 3} more)"
    else:
        detail = "installed, no models pulled yet"

    return ComponentStatus(
        key="ollama",
        name="Ollama (local AI interpretation)",
        required=False,
        installed=True,
        detail=detail,
        install_commands=[
            "ollama pull llama3.1:8b   # recommended starter model (~5 GB)",
            "ollama pull gemma2:9b     # alternative",
        ],
        docs_url="https://ollama.com/library",
    )


def _ollama_install_commands() -> list[str]:
    system = platform.system().lower()
    if system == "darwin":
        if shutil.which("brew"):
            return ["brew install ollama", "# or download GUI: https://ollama.com/download/mac"]
        return ["# Download installer: https://ollama.com/download/mac"]
    if system == "linux":
        return [
            "# Official installer (requires sudo):",
            "curl -fsSL https://ollama.com/install.sh | sh",
        ]
    if system == "windows":
        return ["# Download installer: https://ollama.com/download/windows"]
    return ["# See https://ollama.com/download for your platform"]


def _list_ollama_models() -> list[str]:
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    lines = result.stdout.strip().splitlines()
    # First line is the header (NAME ID SIZE MODIFIED)
    return [line.split()[0] for line in lines[1:] if line.strip()]


def check_all() -> list[ComponentStatus]:
    """Return status of every known component."""
    return [
        check_clinvar(),
        check_pharmgkb(),
        check_argos_translate(),
        check_ollama(),
    ]
