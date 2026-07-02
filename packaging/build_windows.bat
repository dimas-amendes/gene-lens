@echo off
REM Build the Windows Gene Lens desktop bundle and zip it for release.
REM
REM Usage (from the project root, inside the venv):
REM   .venv\Scripts\pip install -r requirements.txt -r requirements-dev.txt
REM   packaging\build_windows.bat
REM
REM Output: dist\GeneLens-<ver>-Windows.exe — a single self-contained .exe
REM (onefile). The user double-clicks it; a console window shows first-run
REM progress and the local address, then the browser opens on the dashboard.
REM One clean file, differentiated by the .exe extension — nice as a Release
REM asset (no folder to zip).
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

echo ==^> Naming asset -^> dist\GeneLens-%VERSION%-Windows.exe
if exist "dist\GeneLens-%VERSION%-Windows.exe" del "dist\GeneLens-%VERSION%-Windows.exe"
move /y "dist\GeneLens.exe" "dist\GeneLens-%VERSION%-Windows.exe"

echo ==^> Done: dist\GeneLens-%VERSION%-Windows.exe
endlocal
