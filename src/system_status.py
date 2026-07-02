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
    CLINVAR_MIN_VALID_BYTES,
    PHARMGKB_MIN_VALID_BYTES,
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


def _file_valid(path: Path, min_bytes: int) -> bool:
    """Present AND large enough to be a real database (not a corrupt/partial
    download). A tiny file is treated as absent so the UI offers a re-download."""
    try:
        return path.exists() and path.stat().st_size >= min_bytes
    except OSError:
        return False


def clinvar_present() -> bool:
    return _file_valid(CLINVAR_TSV, CLINVAR_MIN_VALID_BYTES)


def pharmgkb_present() -> bool:
    return (_file_valid(PHARMGKB_ANNOTATIONS, PHARMGKB_MIN_VALID_BYTES)
            and _file_valid(PHARMGKB_ALLELES, PHARMGKB_MIN_VALID_BYTES))


def _file_info(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, ""
    size_mb = path.stat().st_size / (1024 * 1024)
    mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
    return True, f"{size_mb:.1f} MB · updated {mtime}"


def check_clinvar() -> ComponentStatus:
    valid = clinvar_present()
    _, detail = _file_info(CLINVAR_TSV)
    if CLINVAR_TSV.exists() and not valid:
        # Present but too small — corrupt/incomplete. Flag it so the user knows
        # to re-download instead of trusting a near-empty database.
        detail = f"corrupt or incomplete ({detail}) — re-download"
    elif not detail:
        detail = f"missing at {CLINVAR_TSV.relative_to(CLINVAR_TSV.parent.parent)}"
    return ComponentStatus(
        key="clinvar",
        name="ClinVar database",
        required=True,
        installed=valid,
        detail=detail,
        install_commands=["python download_databases.py --clinvar"],
        docs_url="https://www.ncbi.nlm.nih.gov/clinvar/",
    )


def check_pharmgkb() -> ComponentStatus:
    valid = pharmgkb_present()
    ann_ok = PHARMGKB_ANNOTATIONS.exists()
    all_ok = PHARMGKB_ALLELES.exists()
    if valid:
        size_mb = (
            PHARMGKB_ANNOTATIONS.stat().st_size + PHARMGKB_ALLELES.stat().st_size
        ) / (1024 * 1024)
        detail = f"{size_mb:.1f} MB · both files present"
    elif ann_ok and all_ok:
        detail = "corrupt or incomplete — re-download"
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
        installed=valid,
        detail=detail,
        install_commands=[
            "# Downloads the public Clinical Annotations archive (no login)",
            "python download_databases.py --pharmgkb",
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
    import sys
    spec = importlib.util.find_spec("argostranslate")
    pkg_installed = spec is not None
    model_installed = pkg_installed and is_argos_model_installed()

    # In the packaged app there's no user-accessible Python: it runs a sealed,
    # embedded interpreter and the heavy Argos stack is excluded from the
    # bundle. So `pip install` / `python main.py ...` don't apply here — showing
    # them would just mislead a non-technical user. Present it honestly as a
    # source-install-only feature; PT-BR analyses fall back to English.
    if getattr(sys, "frozen", False) and not model_installed:
        return ComponentStatus(
            key="argos",
            name="Argos Translate (PT-BR neural translation)",
            required=False,
            installed=False,
            detail="not available in the app version — clinical text shows in English",
            # The commands install into a SYSTEM Python, so they only take effect
            # when running Gene Lens from source (the packaged app uses its own
            # sealed Python). Shown for reference; the leading note makes the
            # limitation explicit so a packaged user isn't misled.
            install_commands=[
                "# Only works when running Gene Lens from source, not the packaged app:",
                "pip install argostranslate",
                "python main.py install-translator-model   # downloads the en->pt model (~100 MB)",
            ],
            docs_url="https://github.com/argosopentech/argos-translate",
        )
    version = ""
    if pkg_installed:
        try:
            import argostranslate  # type: ignore
            version = getattr(argostranslate, "__version__", "installed")
        except Exception:
            version = "installed"

    if model_installed:
        detail = f"version {version} · en->pt model ready"
        cmds: list[str] = []
    elif pkg_installed:
        # Package is there but the ~100MB en->pt model isn't. Show only the
        # one command that's still missing — copying `pip install` again
        # would just be noise.
        detail = f"version {version} · model NOT installed (PT-BR analyses need it)"
        cmds = ["python main.py install-translator-model"]
    else:
        detail = "not installed in this Python environment"
        cmds = [
            "pip install argostranslate",
            "python main.py install-translator-model   # downloads the en->pt model (~100 MB)",
        ]

    return ComponentStatus(
        key="argos",
        name="Argos Translate (PT-EN neural translation)",
        required=False,
        # Treat "installed" as fully usable, so the green checkmark in the
        # UI only appears when PT-BR analyses will actually get neural text.
        installed=model_installed,
        detail=detail,
        install_commands=cmds,
        docs_url="https://www.argosopentech.com/",
    )


def check_ollama() -> ComponentStatus:
    # Detect via the HTTP daemon (127.0.0.1:11434), not shutil.which: a
    # Finder-launched .app doesn't inherit the shell PATH, so `which ollama`
    # fails even when Ollama is installed and running. The daemon check is
    # PATH-independent and is what the AI actually needs to be reachable.
    from src.local_ai import is_ollama_available, list_models
    if not is_ollama_available():
        return ComponentStatus(
            key="ollama",
            name="Ollama (local AI interpretation)",
            required=False,
            installed=False,
            detail="not detected — install Ollama and make sure it's running",
            install_commands=_ollama_install_commands(),
            docs_url="https://ollama.com/download",
        )

    models = list_models()
    if models:
        detail = f"running · models: {', '.join(models[:3])}"
        if len(models) > 3:
            detail += f" (+{len(models) - 3} more)"
    else:
        detail = "running, no models pulled yet"

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
