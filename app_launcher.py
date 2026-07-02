#!/usr/bin/env python3
"""
Gene Lens — double-click launcher for the packaged desktop build.

This is the PyInstaller entry point. Unlike `run.py` (which assumes a dev
checkout with a venv), this launcher is what a non-technical user runs after
downloading the release: it starts the local server and opens the dashboard in
the default browser.

Flow on launch:
  1. Ask the language (native dialog in .app mode, terminal prompt otherwise).
  2. Pick a free port, start the local Flask server, open the browser.
  3. Stay running until the user closes the window.

Database download is NOT done here: the browser /setup page lets the user
choose which reference databases to fetch (with explanations), and the Flask
`index` route redirects there on first run. So all three entry points — source
checkout, console binary, .app — share the exact same browser onboarding. That
download is the only network step; analysis runs behind NetworkBlocker.

Everything stays on localhost. No genetic data ever leaves the machine.

Environment overrides (advanced):
  GENE_LENS_DATA_HOME  Where databases/input/output are written.
  GENE_LENS_PORT       Preferred port (default 5000, auto-bumps if taken).
  GENE_LENS_LANG       Startup language: en (default) or pt (skips the prompt).
"""
import os
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

# In a frozen bundle sys.path is already correct; in dev, anchor to this file
# so `import config`, `import dashboard`, etc. resolve from the project root.
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).parent))

# Windowed builds (the macOS .app, which has no attached terminal) start with
# sys.stdout/stderr set to None. Any downstream print() — our banner, Flask's
# own logging — would then raise. Redirect to devnull so the app never crashes
# on output it can't show, and remember we're windowed so we ask for the
# language through a native dialog instead of a terminal prompt.
WINDOWED = bool(getattr(sys, "frozen", False)) and sys.stdout is None
if WINDOWED:
    _devnull = open(os.devnull, "w")
    sys.stdout = _devnull
    sys.stderr = _devnull

from config import DATA_DIR, INPUT_DIR, OUTPUT_DIR


def _mac_choose_language() -> str:
    """Ask the user to pick a language via a native macOS button dialog.
    Returns 'pt' or 'en' (default 'en' on any failure)."""
    if sys.platform != "darwin":
        return "en"
    try:
        result = subprocess.run(
            ["osascript", "-e",
             'button returned of (display dialog '
             '"Choose your language\\nEscolha seu idioma" with title "Gene Lens" '
             'buttons {"Portugues", "English"} default button "English" with icon note)'],
            capture_output=True, text=True, timeout=120,
        )
        return "pt" if (result.stdout or "").strip().startswith("Portugues") else "en"
    except (OSError, subprocess.SubprocessError):
        return "en"


def _choose_language() -> str:
    """Resolve the startup language: EN or PT-BR.

    Precedence: GENE_LENS_LANG override (automation/tests) > interactive prompt.
    Windowed (.app) mode asks via a native dialog; console mode asks on the
    terminal. Defaults to EN when there's no answer (EN-first, per project i18n).
    """
    override = os.environ.get("GENE_LENS_LANG")
    if override:
        return "pt" if override.lower().startswith("pt") else "en"
    if WINDOWED:
        return _mac_choose_language()
    try:
        print("Language / Idioma:")
        print("  [1] English")
        print("  [2] Portugues (pt-BR)")
        choice = input("Select / Selecione [1]: ").strip()
    except (EOFError, KeyboardInterrupt):
        return "en"
    return "pt" if choice == "2" else "en"


def _banner(lang: str) -> None:
    print("=" * 60)
    print("  Gene Lens — Local Genome Analysis")
    print("=" * 60)
    if lang == "pt":
        print("  Tudo roda no seu computador. Nenhum dado sai da maquina.")
        print(f"  Seus dados ficam em: {DATA_DIR.parent}")
    else:
        print("  Everything runs on your computer. No data leaves the machine.")
        print(f"  Your data lives in: {DATA_DIR.parent}")
    print("=" * 60)
    print()


def _ensure_dirs() -> None:
    for d in (DATA_DIR, INPUT_DIR, OUTPUT_DIR):
        d.mkdir(parents=True, exist_ok=True)


def _open_browser_when_ready(url: str, delay: float = 1.5) -> None:
    """Open the default browser shortly after the server starts.

    run_dashboard() blocks, so we schedule the browser open on a timer thread.
    A short delay lets Flask bind the socket first; if it's slightly early the
    browser retries on its own.
    """
    threading.Timer(delay, lambda: webbrowser.open(url)).start()


def main() -> None:
    lang = _choose_language()

    _banner(lang)
    _ensure_dirs()

    # Reuse run.py's battle-tested port picker (handles macOS AirPlay squatting
    # on 5000 and auto-bumps to a free port).
    from run import _pick_port
    preferred = int(os.environ.get("GENE_LENS_PORT", "5000"))
    port = _pick_port(preferred, auto=True)

    url = f"http://127.0.0.1:{port}"
    if lang == "pt":
        print(f"  Abrindo o Gene Lens em {url}")
        print("  Mantenha esta janela aberta. Feche-a para encerrar o Gene Lens.\n")
    else:
        print(f"  Opening Gene Lens at {url}")
        print("  Keep this window open. Close it to stop Gene Lens.\n")

    _open_browser_when_ready(url)

    from dashboard import run_dashboard
    run_dashboard(port=port, debug=False, lang=lang)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Gene Lens stopped. Your data is untouched. Goodbye.")
        sys.exit(0)
