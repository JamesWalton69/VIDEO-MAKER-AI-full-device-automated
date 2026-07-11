@echo off
title VideoMaker - Convert Text to CSV
color 0E
echo.
echo ============================================
echo   VideoMaker - Script to CSV Converter
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

:: Run the script
python txt_to_csv.py

echo.
pause
