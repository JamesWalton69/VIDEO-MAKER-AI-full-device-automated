@echo off
title VideoMaker - Setup Faster Whisper (Intel Arc GPU)
color 0A
echo.
echo ============================================
echo   Faster Whisper Setup (Intel Arc / OpenVINO)
echo ============================================
echo.
echo This installs faster-whisper with Intel OpenVINO support.
echo Uses your Intel Arc integrated GPU for ~10x faster transcription.
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
echo [1/3] Installing faster-whisper...
uv pip install faster-whisper
echo [OK] faster-whisper installed.

echo.
echo [2/3] Installing OpenVINO runtime (Intel Arc GPU support)...
uv pip install openvino
echo [OK] OpenVINO installed.

echo.
echo [3/3] Installing optimum-intel (bridges faster-whisper + OpenVINO)...
uv pip install optimum[openvino]
echo [OK] optimum-intel installed.

echo.
echo ============================================
echo   DONE! Faster Whisper is ready.
echo ============================================
echo.
echo Now use  2c_SRT_FAST.bat  instead of  2b_SRT_ONLY.bat
echo Transcription should take under 1 minute on your Arc GPU.
echo.
pause
