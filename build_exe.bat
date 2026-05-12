@echo off
REM ============================================================
REM TikTok Bot - Build Windows .exe
REM ============================================================
REM Creates a standalone TikTokBot.exe in the dist/ folder
REM ============================================================

echo.
echo ======================================================
echo   TikTok Bot - Building .exe...
echo ======================================================
echo.

REM Check PyInstaller
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Installing PyInstaller...
    python -m pip install pyinstaller
)

echo [1/3] Cleaning previous build...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo       Done.
echo.

echo [2/3] Building TikTokBot.exe...
echo       This may take 1-3 minutes...
echo.
python -m PyInstaller tiktok_bot.spec --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed! Try running: python build_exe.py
    pause
    exit /b 1
)

echo.
echo [3/3] Copying configuration files to dist...
if not exist "dist" mkdir dist
copy .env.example dist\ >nul 2>&1
copy us_proxies.txt dist\ >nul 2>&1
if exist ".env" copy .env dist\ >nul 2>&1

echo.
echo ======================================================
echo   BUILD SUCCESSFUL!
echo ======================================================
echo.
echo   Your .exe is ready at:
echo   dist\TikTokBot.exe
echo.
echo   To distribute:
echo   1. Copy the entire "dist" folder
echo   2. Make sure .env is configured with your username
echo   3. Chrome must be installed on the target machine
echo.
echo   File size:
dir dist\TikTokBot.exe | findstr "TikTokBot"
echo.
pause
