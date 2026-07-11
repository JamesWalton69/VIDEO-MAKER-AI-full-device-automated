@echo off
title VideoMaker - Make Video
color 0B
echo.
echo ============================================
echo   VideoMaker - Auto Video Generator
echo ============================================
echo.

:: Set working directory to this folder
cd /d "%~dp0"

:: Check venv exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Setup not complete. Please run 1_SETUP.bat first!
    pause
    exit /b 1
)

:: Activate local venv
call .venv\Scripts\activate.bat

:: Add local FFmpeg to PATH (only for this session)
set PATH=%~dp0tools;%PATH%

:: Run the main Python script
python make_video.py

echo.
pause
