@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo === LynkerAI Orchestrator Launcher (verify -> match -> insights) ===
echo.

REM Choose Python interpreter (prefer dedicated venv if available)
set "PYEXE=python"
if exist "C:\lkk_venv\Scripts\python.exe" set "PYEXE=C:\lkk_venv\Scripts\python.exe"
echo [*] Using Python interpreter: %PYEXE%

REM Ensure UTF-8 console to avoid UnicodeEncodeError on Windows
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM 1) Ensure a .env exists
if not exist ".env" (
  echo [*] .env not found. Creating from .env.example (if present)...
  if exist ".env.example" (
    copy /Y .env.example .env >nul
  ) else (
    echo MASTER_VAULT_KEY=dev-secret>.env
    echo LYNKER_USER_ID=u_demo>>.env
  )
)

REM 2) Load .env variables (ignore empty lines and comments)
for /f "usebackq tokens=* delims=" %%A in (".env") do (
  set "line=%%A"
  if not "!line!"=="" if not "!line:~0,1!"=="#" (
    for /f "tokens=1,* delims==" %%B in ("!line!") do (
      if not "%%B"=="" set "%%B=%%C"
    )
  )
)

REM 3) Safe defaults
if not defined LYNKER_USER_ID set "LYNKER_USER_ID=u_demo"

REM 4) Ensure Python dependencies (CPU-only)
echo [*] Ensuring Python packages (this may take several minutes on first run)...
"%PYEXE%" -m pip install --disable-pip-version-check --prefer-binary -q ^
  sentence-transformers numpy requests supabase >nul 2>&1
if errorlevel 1 (
  echo [!] Silent install failed. Retrying with verbose output...
  "%PYEXE%" -m pip install --prefer-binary sentence-transformers numpy requests supabase || goto :fail
)

echo.
echo [i] If this is your first run, the model 'shibing624/text2vec-base-chinese' will download.
echo     That can take a few minutes depending on your network.
echo.

REM 5) Run orchestrator pipeline
"%PYEXE%" main.py
goto :eof

:fail
echo.
echo [x] Setup failed. Please check your internet connection and try again.
exit /b 1
