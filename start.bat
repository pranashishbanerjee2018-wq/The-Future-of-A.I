@echo off
title THE FUTURE OF ARTIFICIAL INTELLIGENCE - Academic Research Laboratory
color 0B

echo ==============================================================================
echo   THE FUTURE OF ARTIFICIAL INTELLIGENCE
echo   A Journey Through Innovation, Intelligence and Technology
echo ==============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python runtime...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ and add it to your system PATH.
    pause
    exit /b 1
)

echo [2/3] Verifying and generating scientific and visual assets...
python generate_assets.py

echo [3/3] Launching Flask Academic Presentation Service...
echo Presentation will be accessible at: http://127.0.0.1:5000
echo.

start "" "http://127.0.0.1:5000"

python app.py

pause
