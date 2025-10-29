@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo === LynkerAI Admin Dashboard Launcher ===
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
  echo [*] .env not found. Creating from .env.example ^(if present^)...
  if exist ".env.example" (
    copy /Y .env.example .env >nul
  ) else (
    echo OPENAI_API_KEY=>.env
    echo SUPABASE_URL=>>.env
    echo SUPABASE_KEY=>>.env
    echo DATABASE_URL=>>.env
    echo LYNKER_USER_ID=u_demo>>.env
  )
)

REM 2) Provide safe default key if missing (dotenv will also load .env inside app)
if not defined MASTER_VAULT_KEY set "MASTER_VAULT_KEY=dev-secret"
if not defined RELAY_API_KEY set "RELAY_API_KEY=lynker_relay_secret_2025"

REM 3) Show derived login password (robust computation without fragile quoting)
set "LOGIN_TOKEN="
if /I "%MASTER_VAULT_KEY%"=="dev-secret" (
  set "LOGIN_TOKEN=298754db2dbab6ec"
) else (
  "%PYEXE%" scripts\print_login_token.py > "%TEMP%\login_token.txt"
  if exist "%TEMP%\login_token.txt" (
    set /p LOGIN_TOKEN=<"%TEMP%\login_token.txt"
    del /q "%TEMP%\login_token.txt" >nul 2>&1
  )
)

echo.
echo MASTER_VAULT_KEY = [set]
echo Admin login password = %LOGIN_TOKEN%
echo.

REM 4) Minimal dependencies for the dashboard
echo [*] Ensuring minimal Python packages...
"%PYEXE%" -m pip install --disable-pip-version-check -q flask flask-socketio python-socketio >nul 2>&1
if errorlevel 1 (
  echo [!] Failed to install Flask/SocketIO. Trying verbose install...
  "%PYEXE%" -m pip install flask flask-socketio python-socketio || goto :fail
)

REM 5) Launch the dashboard
echo [*] Starting Admin Dashboard at http://localhost:5000/admin
echo     Press Ctrl+C to stop.
echo.
"%PYEXE%" admin_dashboard\app.py
goto :eof

:fail
echo.
echo [x] Launch failed. Please ensure Python and pip are available.
exit /b 1
