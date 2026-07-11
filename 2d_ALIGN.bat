@echo off
title VideoMaker - Align Script to Audio
color 0D
echo.
echo ============================================
echo   VideoMaker - Align Your Script to Audio
echo ============================================
echo.
echo Reads audio\ + audio\script.txt
echo Outputs captions\aligned.srt with exact timestamps
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Run 1_SETUP.bat first!
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
set PATH=%~dp0tools;%PATH%

python align.py

echo.
pause
