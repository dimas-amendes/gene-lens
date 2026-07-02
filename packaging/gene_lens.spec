# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the Gene Lens desktop bundle.

Build (from the project root, inside the venv):
    pyinstaller packaging/gene_lens.spec --noconfirm

Outputs (three ways to run Gene Lens, source checkout being the third):
  * dist/GeneLens/       — one-folder CONSOLE build. Double-click the binary or
                           run it from a terminal; first-run download progress
                           and the local URL print to the console.
  * dist/Gene Lens.app   — macOS only. Double-click app bundle with no terminal;
                           first-run setup is surfaced via a native dialog and
                           the browser opens automatically.

Cross-platform: run this same spec on a macOS runner (console build + .app) and
on a Windows runner (console GeneLens.exe — Windows has no .app concept, the exe
IS the double-click form).

We do NOT bundle the databases (data/): they're large and downloaded at first
run into a per-user writable dir (see config._user_data_root). We DO bundle the
read-only resources Flask serves: templates/, static/, and the synthetic sample.
"""
import os
import sys
from PyInstaller.utils.hooks import collect_submodules

# SPECPATH is injected by PyInstaller and points at this file's directory.
ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))

datas = [
    (os.path.join(ROOT, "templates"), "templates"),
    (os.path.join(ROOT, "static"), "static"),
    (os.path.join(ROOT, "sample"), "sample"),
    # Bundled so the running app can read its own version (shown in the UI).
    (os.path.join(ROOT, "pyproject.toml"), "."),
]

# dashboard.py imports the src.* modules directly so PyInstaller's static
# analysis finds them, but a few are imported lazily inside functions
# (download_databases, src.translator). Collect the whole src package plus
# Flask/Jinja to be safe.
hiddenimports = (
    collect_submodules("src")
    + collect_submodules("flask")
    + collect_submodules("jinja2")
    + ["download_databases", "config", "dashboard", "run"]
)

# Optional heavyweight neural-translation stack. If installed in the build venv
# it would balloon the bundle by hundreds of MB; the app degrades gracefully to
# English source text without it, so keep it out of the shipped binary.
excludes = [
    "argostranslate",
    "ctranslate2",
    "sentencepiece",
    "torch",
    "stanza",
    "tkinter",
    "matplotlib",
]

block_cipher = None

# App version (from pyproject) drives the macOS Info.plist version fields.
try:
    import tomllib
    with open(os.path.join(ROOT, "pyproject.toml"), "rb") as _f:
        VERSION = tomllib.load(_f)["project"]["version"]
except Exception:
    VERSION = "0.0.0"

_ICNS = os.path.join(SPECPATH, "icon.icns")
_ICO = os.path.join(SPECPATH, "icon.ico")
ICON_MAC = _ICNS if os.path.exists(_ICNS) else None
ICON_WIN = _ICO if os.path.exists(_ICO) else None

a = Analysis(
    [os.path.join(ROOT, "app_launcher.py")],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if sys.platform == "win32":
    # ── Windows: single-file GeneLens.exe (clean release asset) ──────────────
    # onefile bundles everything into one .exe (self-extracts to temp at launch).
    # A few seconds slower to start than onedir, but a single downloadable file
    # is far nicer to present on a GitHub Release than a zipped folder.
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name="GeneLens",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        runtime_tmpdir=None,
        console=True,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=ICON_WIN,
    )
else:
    # ── macOS: console onedir (Terminal) + windowed .app (double-click) ───────
    exe_console = EXE(
        pyz, a.scripts, [], exclude_binaries=True, name="GeneLens",
        debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
        console=True, disable_windowed_traceback=False, argv_emulation=False,
        target_arch=None, codesign_identity=None, entitlements_file=None,
        icon=ICON_MAC,
    )
    coll_console = COLLECT(
        exe_console, a.binaries, a.zipfiles, a.datas,
        strip=False, upx=False, upx_exclude=[], name="GeneLens",
    )

    # A separate console=False EXE so PyInstaller sets up windowed mode:
    # sys.stdout becomes None, which app_launcher detects (WINDOWED) to ask the
    # language via a native dialog instead of a terminal prompt.
    exe_app = EXE(
        pyz, a.scripts, [], exclude_binaries=True, name="Gene Lens",
        debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
        console=False, disable_windowed_traceback=False, argv_emulation=False,
        target_arch=None, codesign_identity=None, entitlements_file=None,
        icon=ICON_MAC,
    )
    coll_app = COLLECT(
        exe_app, a.binaries, a.zipfiles, a.datas,
        strip=False, upx=False, upx_exclude=[], name="Gene Lens",
    )
    app = BUNDLE(
        coll_app,
        name="Gene Lens.app",
        icon=ICON_MAC,
        bundle_identifier="tech.codebay.genelens",
        version=VERSION,
        info_plist={
            "CFBundleName": "Gene Lens",
            "CFBundleDisplayName": "Gene Lens",
            "CFBundleShortVersionString": VERSION,
            "CFBundleVersion": VERSION,
            "NSHighResolutionCapable": True,
            # Not a background agent — show in the Dock and open the browser
            # like a normal app.
            "LSBackgroundOnly": False,
        },
    )
