#!/usr/bin/env bash
#
# Build the macOS Gene Lens desktop bundle and zip it for release.
#
# Usage (from the project root, inside the venv):
#   .venv/bin/pip install -r requirements.txt -r requirements-dev.txt
#   bash packaging/build_macos.sh
#
# Version-stamped release assets, flat in dist/ (differentiated by name/ext):
#   * dist/GeneLens-<ver>-macOS.zip           -> "Gene Lens.app" (double-click)
#   * dist/GeneLens-<ver>-Terminal-macOS.zip  -> console build (run in Terminal)
# (Running from a source checkout is the third way; see the README.)
#
# Unsigned by design (no paid Apple Developer cert). First open needs the
# one-time Gatekeeper bypass documented in the README ("First time opening").
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY="${PYTHON:-.venv/bin/python}"
VERSION="$("$PY" -c "import tomllib,pathlib;print(tomllib.loads(pathlib.Path('pyproject.toml').read_text())['project']['version'])" 2>/dev/null || echo dev)"

echo "==> Building Gene Lens macOS bundles (version ${VERSION})"
"$PY" -m PyInstaller packaging/gene_lens.spec --noconfirm --distpath dist --workpath build

APP_ZIP="dist/GeneLens-${VERSION}-macOS.zip"
TERM_ZIP="dist/GeneLens-${VERSION}-Terminal-macOS.zip"
echo "==> Zipping app bundle -> ${APP_ZIP}"
( cd dist && rm -f "GeneLens-${VERSION}-macOS.zip" && zip -qry "GeneLens-${VERSION}-macOS.zip" "Gene Lens.app" )
echo "==> Zipping console build -> ${TERM_ZIP}"
( cd dist && rm -f "GeneLens-${VERSION}-Terminal-macOS.zip" && zip -qry "GeneLens-${VERSION}-Terminal-macOS.zip" GeneLens )

# Tidy up PyInstaller's raw output. The two zips are the distributables and the
# .app is kept for local double-click testing; the console onedir folder and the
# intermediate COLLECT that BUNDLE wraps are build scratch already captured in
# the zips, so remove them to keep dist/ clean.
echo "==> Cleaning raw build folders (keeping zips + Gene Lens.app)"
rm -rf dist/GeneLens "dist/Gene Lens"

echo "==> Done:"
echo "    ${APP_ZIP}"
echo "    ${TERM_ZIP}"
echo "    dist/Gene Lens.app (for local testing)"
