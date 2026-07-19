@echo off
title VideoMaker AI - Central Launcher
color 0E
echo.
echo ============================================
echo   VideoMaker AI - Control Panel
echo ============================================
echo.

:: Set working directory to this folder
cd /d "%~dp0"

:: Check if venv exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Setup not complete. Please run 1_SETUP.bat first!
    pause
    exit /b 1
)

:: Activate local venv
call .venv\Scripts\activate.bat

:: Add local FFmpeg to PATH (only for this session)
set PATH=%~dp0tools;%PATH%

:: Sync codebase with git
echo [INFO] Fetching latest updates from Git...
git pull
echo.

:: Run launcher.py
python launcher.py

echo.
pause
