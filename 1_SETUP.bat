@echo off
title VideoMaker - First Time Setup
color 0A
echo.
echo ============================================
echo   VideoMaker - First Time Setup
echo ============================================
echo.
echo This will install everything INSIDE this folder only.
echo Nothing will be installed system-wide.
echo.
pause

:: Set working directory to this folder
cd /d "%~dp0"

:: Check uv is available
where uv >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 'uv' is not found. Please install uv first from https://docs.astral.sh/uv/
    echo Then re-run this setup.
    pause
    exit /b 1
)
echo [OK] uv found.

:: Create a local virtual environment inside this folder
echo.
echo [1/4] Creating local Python environment in this folder...
uv venv .venv
echo [OK] Virtual environment created.

:: Activate venv
call .venv\Scripts\activate.bat

:: Install Python dependencies inside the venv
echo.
echo [2/4] Installing Whisper, TTS, and video tools (this may take a few minutes)...
uv pip install openai-whisper moviepy pillow tqdm edge-tts
echo [OK] Python packages installed.

:: Download FFmpeg portable into tools folder (no system install)
echo.
echo [3/4] Downloading FFmpeg portable into tools folder...
powershell -Command "& { $url = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip'; $out = '%~dp0tools\ffmpeg.zip'; Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing }"
echo [OK] FFmpeg downloaded.

echo.
echo [4/4] Extracting FFmpeg...
powershell -Command "Expand-Archive -Path '%~dp0tools\ffmpeg.zip' -DestinationPath '%~dp0tools\ffmpeg_extracted' -Force"
:: Move ffmpeg.exe and ffprobe.exe into tools folder directly
for /r "%~dp0tools\ffmpeg_extracted" %%f in (ffmpeg.exe ffprobe.exe) do (
    copy /Y "%%f" "%~dp0tools\" >nul
)
rd /s /q "%~dp0tools\ffmpeg_extracted" >nul 2>&1
del "%~dp0tools\ffmpeg.zip" >nul 2>&1
echo [OK] FFmpeg ready.

echo.
echo ============================================
echo   SETUP COMPLETE!
echo ============================================
echo.
echo Next steps:
echo   1. Drop your AUDIO file into the  audio\  folder
echo   2. Drop your IMAGES into the      images\ folder
echo      (name them: 001.png, 002.png, 003.png ...)
echo   3. Double-click  2_RUN.bat  to make your video!
echo.
pause
