@echo off
REM Build the Windows Gene Lens desktop bundle and zip it for release.
REM
REM Usage (from the project root, inside the venv):
REM   .venv\Scripts\pip install -r requirements.txt -r requirements-dev.txt
REM   packaging\build_windows.bat
REM
REM Output: dist\GeneLens-<ver>-Windows.zip — a zip containing a single
REM self-contained GeneLens.exe (onefile). Zipped for consistency with the
REM macOS assets (which must be zipped because a .app is a folder); the user
REM unzips and double-clicks GeneLens.exe. A console window shows first-run
REM progress and the local address, then the browser opens on the dashboard.
REM
REM Unsigned by design (no paid code-signing cert). First run needs the one-time
REM SmartScreen bypass documented in the README ("First time opening").
setlocal
cd /d "%~dp0.."

if "%PYTHON%"=="" set PYTHON=.venv\Scripts\python.exe

for /f "delims=" %%v in ('"%PYTHON%" -c "import tomllib,pathlib;print(tomllib.loads(pathlib.Path('pyproject.toml').read_text())['project']['version'])"') do set VERSION=%%v
if "%VERSION%"=="" set VERSION=dev

echo ==^> Building Gene Lens Windows single-file exe (version %VERSION%)
"%PYTHON%" -m PyInstaller packaging\gene_lens.spec --noconfirm --distpath dist --workpath build
if errorlevel 1 exit /b 1

echo ==^> Zipping GeneLens.exe -^> dist\GeneLens-%VERSION%-Windows.zip
if exist "dist\GeneLens-%VERSION%-Windows.zip" del "dist\GeneLens-%VERSION%-Windows.zip"
powershell -NoProfile -Command "Compress-Archive -Path 'dist\GeneLens.exe' -DestinationPath 'dist\GeneLens-%VERSION%-Windows.zip' -Force"

echo ==^> Done: dist\GeneLens-%VERSION%-Windows.zip
endlocal
