@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo === LynkerAI Dependency Installer ===
echo.
echo [*] Using requirements.txt to install all needed packages.
echo     This can take several minutes the first time (models & wheels).
echo.

if not exist requirements.txt (
  echo [x] requirements.txt not found in current directory.
  exit /b 1
)

REM Upgrade pip tooling (quiet)
python -m pip install --upgrade --disable-pip-version-check pip setuptools wheel >nul 2>&1

REM Install all dependencies
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo [x] Installation failed. Please review errors above and retry.
  exit /b 1
)

echo.
echo ✅ All dependencies installed successfully.
echo    - To launch Admin Dashboard: run_app.bat
echo    - To run Orchestrator pipeline: run_orchestrator.bat
echo.
endlocal

