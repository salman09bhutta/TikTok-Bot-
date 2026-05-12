@echo off
REM ============================================================
REM AI Content Engine - Complete Windows Installer
REM ============================================================
REM Installs EVERYTHING needed for fully autonomous content
REM generation and upload for Mini Building Construction niche.
REM
REM Just double-click this file and wait!
REM ============================================================

echo.
echo ======================================================================
echo   AI Content Engine - Complete Installer
echo   Mini Building Construction - TikTok ^& YouTube Shorts
echo ======================================================================
echo.
echo   This will install:
echo   - Python dependencies (33 packages)
echo   - FFmpeg (video processing)
echo   - Chrome/ChromeDriver (browser automation)
echo   - MoviePy, Pillow, NumPy (video editing)
echo   - OpenAI, Google AI (content generation)
echo   - YouTube API + TikTok uploader
echo.
echo   Press any key to start or Ctrl+C to cancel...
pause >nul
echo.

REM ═══════════════════════════════════════
REM Step 1: Check Python
REM ═══════════════════════════════════════
echo [1/7] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Download from: https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during install!
    pause
    exit /b 1
)
python --version
echo       OK!
echo.

REM ═══════════════════════════════════════
REM Step 2: Upgrade pip
REM ═══════════════════════════════════════
echo [2/7] Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo       Done.
echo.

REM ═══════════════════════════════════════
REM Step 3: Install Python packages
REM ═══════════════════════════════════════
echo [3/7] Installing Python packages (this may take 2-3 minutes)...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some packages may have failed. Trying individually...
    python -m pip install selenium undetected-chromedriver webdriver-manager
    python -m pip install moviepy Pillow numpy imageio imageio-ffmpeg
    python -m pip install openai google-generativeai
    python -m pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
    python -m pip install requests python-dotenv fake-useragent schedule
    python -m pip install rich pyfiglet tabulate colorama
    python -m pip install pysocks aiohttp aiohttp-socks pyyaml
)
echo       Done.
echo.

REM ═══════════════════════════════════════
REM Step 4: Install FFmpeg
REM ═══════════════════════════════════════
echo [4/7] Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo       FFmpeg not found. Downloading...
    echo.
    echo       MANUAL STEP REQUIRED:
    echo       1. Go to: https://www.gyan.dev/ffmpeg/builds/
    echo       2. Download "ffmpeg-release-essentials.zip"
    echo       3. Extract to C:\ffmpeg
    echo       4. Add C:\ffmpeg\bin to your PATH:
    echo          - Search "Environment Variables" in Start Menu
    echo          - Edit PATH variable
    echo          - Add: C:\ffmpeg\bin
    echo       5. Restart this terminal and run installer again
    echo.
    echo       OR use winget (Windows 11):
    echo       winget install Gyan.FFmpeg
    echo.
    
    REM Try winget first
    winget install Gyan.FFmpeg >nul 2>&1
    if %errorlevel% equ 0 (
        echo       FFmpeg installed via winget!
    ) else (
        echo       [WARNING] Please install FFmpeg manually (see above)
    )
) else (
    echo       FFmpeg already installed!
    ffmpeg -version 2>&1 | findstr "version"
)
echo.

REM ═══════════════════════════════════════
REM Step 5: Check Chrome
REM ═══════════════════════════════════════
echo [5/7] Checking Google Chrome...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo       Chrome found!
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo       Chrome found (x86)!
) else (
    echo       [WARNING] Chrome not found at default location.
    echo       Download from: https://www.google.com/chrome/
    echo       The bot needs Chrome for TikTok upload.
)
echo.

REM ═══════════════════════════════════════
REM Step 6: Setup .env file
REM ═══════════════════════════════════════
echo [6/7] Setting up configuration...
if not exist ".env" (
    copy .env.example .env >nul
    echo       Created .env from template.
    echo       IMPORTANT: Edit .env with your API keys!
) else (
    echo       .env already exists.
)
echo.

REM ═══════════════════════════════════════
REM Step 7: Create directories
REM ═══════════════════════════════════════
echo [7/7] Creating required directories...
if not exist "footage" mkdir footage
if not exist "music" mkdir music
if not exist "output" mkdir output
if not exist "fonts" mkdir fonts
echo       Directories created.
echo.

REM ═══════════════════════════════════════
REM Verification
REM ═══════════════════════════════════════
echo ======================================================================
echo   VERIFICATION
echo ======================================================================
echo.
python -c "import selenium; print(f'  Selenium: {selenium.__version__}')"
python -c "import moviepy; print(f'  MoviePy: OK')" 2>nul || echo   MoviePy: Missing
python -c "import openai; print(f'  OpenAI: {openai.__version__}')" 2>nul || echo   OpenAI: Missing
python -c "import rich; print(f'  Rich: {rich.__version__}')"
ffmpeg -version 2>&1 | findstr "version" || echo   FFmpeg: Not in PATH
echo.

echo ======================================================================
echo   INSTALLATION COMPLETE!
echo ======================================================================
echo.
echo   Next steps:
echo   1. Edit .env and add your FREE API keys:
echo      - PEXELS_API_KEY (get free: https://www.pexels.com/api/)
echo      - PIXABAY_API_KEY (get free: https://pixabay.com/api/docs/)
echo      - GEMINI_API_KEY (get free: https://ai.google.dev/)
echo.
echo   2. For YouTube upload:
echo      - Get client_secrets.json from Google Cloud Console
echo      - Place in content_engine/ folder
echo.
echo   3. For TikTok upload:
echo      - Run: python main.py (select option 9 to login)
echo.
echo   4. Download music:
echo      - Run: python download_music.py
echo.
echo   5. Start the engine:
echo      - Double-click auto_start.bat
echo      - OR run: python main.py --autopilot
echo.
pause
