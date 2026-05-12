@echo off
REM ============================================================
REM AI Content Engine - AUTOPILOT Launcher
REM ============================================================
REM Double-click this to start fully autonomous content creation.
REM It will generate videos and upload to TikTok + YouTube
REM automatically every 60 minutes until you stop it.
REM
REM Press Ctrl+C to stop at any time.
REM ============================================================

echo.
echo ======================================================================
echo.
echo   ___  __  ________  ___  ___  ___  __    _______  _________
echo  ^|"  ^|/" \^|"      "\^|"  \/"  ^|^|"  ^|/" \  ^|   __ "\("       ")
echo  ^|.  ^|    (.  ___  :)\   \  / ^|.  ^|    \ ^|.  ^|__) :)       (
echo  ^|:  ^|    ^|: \   ) ^|^|\\  \/  ^|^|:  ^|.   \^|:  ____/^|:       ^|
echo   \  ^|___ (: (___/  ^|/\.    /  \  ^|_^|.   (: (     (________^)
echo  ( \_^|:  \\_:       /  \\   /  ( \_^|: \_ ^|_\__\
echo   \_______)_______/    \__/    \_______)
echo.
echo   AUTOPILOT MODE - Mini Building Construction
echo   Auto-generate + Auto-upload to TikTok ^& YouTube
echo.
echo ======================================================================
echo.
echo   Settings:
echo   - Generate 1 video every 60 minutes
echo   - Upload to YouTube Shorts + TikTok
echo   - Uses free stock footage (Pexels/Pixabay)
echo   - AI-generated hooks ^& captions
echo.
echo   Press Ctrl+C at any time to stop.
echo.
echo   Starting in 5 seconds...
timeout /t 5 >nul

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Run install_all.bat first.
    pause
    exit /b 1
)

REM Run autopilot
python main.py --autopilot --every 60

echo.
echo   Autopilot stopped.
pause
