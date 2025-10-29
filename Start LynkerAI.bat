@echo off
title LynkerAI Auto-Start
cd /d "%~dp0"
echo ========================================
echo    LynkerAI Auto-Start Launcher
echo ========================================
echo.
echo This will:
echo 1. Check and setup database automatically
echo 2. Start the LynkerAI application
echo 3. Open your browser automatically
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.
python auto_start_lynkerai.py
echo.
echo LynkerAI has been stopped.
pause