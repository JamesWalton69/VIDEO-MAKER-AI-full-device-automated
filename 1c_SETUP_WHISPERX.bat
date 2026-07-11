@echo off
title VideoMaker - Setup WhisperX (Forced Alignment)
color 0A
echo.
echo ============================================
echo   Setup WhisperX - Forced Alignment
echo ============================================
echo.
echo This lets you provide your OWN script (script.txt)
echo and WhisperX will find the exact timestamp for
echo each line in your audio automatically.
echo.
pause

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Run 1_SETUP.bat first!
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo.
echo [1/2] Installing WhisperX...
uv pip install whisperx
echo [OK] WhisperX installed.

echo.
echo [2/2] Installing torchaudio (alignment models)...
uv pip install torchaudio
echo [OK] torchaudio installed.

echo.
echo ============================================
echo   DONE!
echo ============================================
echo.
echo Now use  2d_ALIGN.bat  to align your script to audio.
echo.
echo HOW TO USE:
echo   1. Put your audio file in  audio\
echo   2. Put your script file    audio\script.txt
echo      (one caption per line, plain text)
echo   3. Run 2d_ALIGN.bat
echo.
pause
