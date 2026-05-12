@echo off
REM ============================================================
REM TikTok Bot - Windows Installation Script
REM ============================================================
REM This script installs all dependencies and builds the .exe
REM Run this ONCE on your Windows machine to set everything up.
REM ============================================================

echo.
echo ======================================================
echo   TikTok Bot - Windows Installer
echo   Views ^| Followers ^| Likes ^| Engagement
echo ======================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please download Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/5] Python found:
python --version
echo.

REM Check pip
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo       Done.
echo.

REM Install dependencies
echo [3/5] Installing Python dependencies...
python -m pip install -r requirements.txt
python -m pip install pyinstaller setuptools
echo       Done.
echo.

REM Check for Chrome
echo [4/5] Checking for Google Chrome...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo       Google Chrome found at default location.
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo       Google Chrome found (x86^).
) else (
    echo [WARNING] Google Chrome not found at default location.
    echo Please install Chrome from: https://www.google.com/chrome/
    echo The bot requires Chrome to run.
)
echo.

REM Setup .env if not exists
echo [5/5] Setting up configuration...
if not exist ".env" (
    copy .env.example .env >nul
    echo       Created .env from template.
    echo       IMPORTANT: Edit .env and set your TikTok username!
) else (
    echo       .env already exists.
)
echo.

echo ======================================================
echo   Installation Complete!
echo ======================================================
echo.
echo   Next steps:
echo   1. Edit .env and set TIKTOK_TARGET_USERNAME
echo   2. Run "build_exe.bat" to create the .exe file
echo   3. Or run "start_bot.bat" to run directly
echo.
pause
