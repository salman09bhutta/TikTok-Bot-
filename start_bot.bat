@echo off
REM ============================================================
REM TikTok Bot - Quick Start (runs without building .exe)
REM ============================================================

echo.
echo ======================================================
echo   TikTok Bot - Starting...
echo   Target: @xxmr.building
echo ======================================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Run install_windows.bat first.
    pause
    exit /b 1
)

REM Menu
echo   Select an option:
echo   [1] Run ALL bots (views + likes + follows) - once
echo   [2] Run ALL bots on schedule (auto-repeat)
echo   [3] Run View Bot only
echo   [4] Run Like/Engagement Bot only
echo   [5] Run Follower Bot only
echo   [6] Refresh US Proxies
echo   [7] Show Statistics
echo   [8] Test Setup
echo.
set /p choice="  Enter choice (1-8): "

if "%choice%"=="1" python main.py --once
if "%choice%"=="2" python main.py
if "%choice%"=="3" python main.py --views
if "%choice%"=="4" python main.py --likes
if "%choice%"=="5" python main.py --follows
if "%choice%"=="6" python proxy_scraper.py --test --update-env
if "%choice%"=="7" python main.py --stats
if "%choice%"=="8" python test_setup.py

echo.
pause
