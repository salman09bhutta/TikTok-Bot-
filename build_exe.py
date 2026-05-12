"""
TikTok Bot - Windows .exe Builder
===================================
This script builds a standalone Windows .exe using PyInstaller.
It handles all dependencies, data files, and creates a distributable package.

Usage:
    python build_exe.py              # Build the .exe
    python build_exe.py --clean      # Clean previous builds then build
    python build_exe.py --onedir     # Build as a folder (faster startup)

Requirements:
    - Python 3.10+
    - PyInstaller (auto-installed if missing)
    - All bot dependencies installed (run install_windows.bat first)
"""

import subprocess
import sys
import os
import shutil
import argparse
import platform


def check_python_version():
    """Ensure Python 3.10+ is being used."""
    version = sys.version_info
    if version < (3, 10):
        print(f"[ERROR] Python 3.10+ required. You have {version.major}.{version.minor}")
        print("Download from: https://www.python.org/downloads/")
        sys.exit(1)
    print(f"  [✓] Python {version.major}.{version.minor}.{version.micro}")


def check_platform():
    """Warn if not running on Windows."""
    if platform.system() != "Windows":
        print(f"  [!] WARNING: Running on {platform.system()}")
        print("      The .exe will only run on Windows.")
        print("      You should build this on a Windows machine.")
        print()
        response = input("      Continue anyway? (y/n): ").strip().lower()
        if response != "y":
            sys.exit(0)
    else:
        print(f"  [✓] Platform: Windows {platform.release()}")


def install_pyinstaller():
    """Install PyInstaller if not available."""
    try:
        import PyInstaller
        print(f"  [✓] PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("  [!] PyInstaller not found. Installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("  [✓] PyInstaller installed")


def install_dependencies():
    """Install all required dependencies."""
    print("\n  Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Also need setuptools for distutils on Python 3.12+
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "setuptools"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("  [✓] All dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"  [!] Warning: Some dependencies may have failed: {e}")


def clean_build():
    """Remove previous build artifacts."""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for d in dirs_to_clean:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  [✓] Removed {d}/")

    # Clean .pyc files
    for root, dirs, files in os.walk("."):
        for f in files:
            if f.endswith(".pyc"):
                os.remove(os.path.join(root, f))


def build_onefile():
    """Build a single .exe file using PyInstaller (--onefile mode)."""
    print("\n  Building TikTokBot.exe (single file)...")
    print("  This may take 2-5 minutes...\n")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--console",
        "--name", "TikTokBot",
        # Add data files
        "--add-data", f".env.example{os.pathsep}.",
        "--add-data", f"us_proxies.txt{os.pathsep}.",
        # Hidden imports for all bot modules
        "--hidden-import", "selenium",
        "--hidden-import", "selenium.webdriver",
        "--hidden-import", "selenium.webdriver.chrome",
        "--hidden-import", "selenium.webdriver.chrome.service",
        "--hidden-import", "selenium.webdriver.chrome.options",
        "--hidden-import", "selenium.webdriver.common.by",
        "--hidden-import", "selenium.webdriver.common.keys",
        "--hidden-import", "selenium.webdriver.common.action_chains",
        "--hidden-import", "selenium.webdriver.support",
        "--hidden-import", "selenium.webdriver.support.ui",
        "--hidden-import", "selenium.webdriver.support.expected_conditions",
        "--hidden-import", "undetected_chromedriver",
        "--hidden-import", "requests",
        "--hidden-import", "dotenv",
        "--hidden-import", "fake_useragent",
        "--hidden-import", "schedule",
        "--hidden-import", "colorama",
        "--hidden-import", "socks",
        "--hidden-import", "aiohttp",
        "--hidden-import", "aiohttp_socks",
        "--hidden-import", "bot",
        "--hidden-import", "bot.viewer",
        "--hidden-import", "bot.engager",
        "--hidden-import", "bot.follower",
        "--hidden-import", "bot.stats",
        "--hidden-import", "browser",
        "--hidden-import", "browser.driver",
        "--hidden-import", "utils",
        "--hidden-import", "utils.logger",
        "--hidden-import", "utils.helpers",
        "--hidden-import", "config",
        "--hidden-import", "proxy_scraper",
        # Collect all submodules
        "--collect-all", "undetected_chromedriver",
        "--collect-all", "fake_useragent",
        # Main script
        "main.py",
    ]

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def build_onedir():
    """Build as a directory (faster startup, multiple files)."""
    print("\n  Building TikTokBot/ folder distribution...")
    print("  This may take 2-5 minutes...\n")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--console",
        "--name", "TikTokBot",
        "--add-data", f".env.example{os.pathsep}.",
        "--add-data", f"us_proxies.txt{os.pathsep}.",
        "--hidden-import", "selenium",
        "--hidden-import", "undetected_chromedriver",
        "--hidden-import", "requests",
        "--hidden-import", "dotenv",
        "--hidden-import", "fake_useragent",
        "--hidden-import", "schedule",
        "--hidden-import", "colorama",
        "--hidden-import", "socks",
        "--hidden-import", "bot",
        "--hidden-import", "bot.viewer",
        "--hidden-import", "bot.engager",
        "--hidden-import", "bot.follower",
        "--hidden-import", "bot.stats",
        "--hidden-import", "browser",
        "--hidden-import", "browser.driver",
        "--hidden-import", "utils",
        "--hidden-import", "utils.logger",
        "--hidden-import", "utils.helpers",
        "--hidden-import", "config",
        "--hidden-import", "proxy_scraper",
        "--collect-all", "undetected_chromedriver",
        "--collect-all", "fake_useragent",
        "main.py",
    ]

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def copy_config_files():
    """Copy necessary config files to dist folder."""
    dist_path = "dist"
    if not os.path.exists(dist_path):
        os.makedirs(dist_path)

    files_to_copy = [
        (".env.example", "dist/.env.example"),
        ("us_proxies.txt", "dist/us_proxies.txt"),
        ("proxy_scraper.py", "dist/proxy_scraper.py"),
    ]

    # Copy .env if it exists (for pre-configured distribution)
    if os.path.exists(".env"):
        files_to_copy.append((".env", "dist/.env"))

    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  [✓] Copied {src} → {dst}")

    # Create a Windows launcher batch file in dist
    launcher_content = """@echo off
echo.
echo ======================================================
echo   TikTok Bot - @xxmr.building
echo   US Views ^| Followers ^| Likes ^| Engagement
echo ======================================================
echo.
echo   [1] Run ALL bots once
echo   [2] Run on schedule (auto-repeat every 30 min)
echo   [3] Views only
echo   [4] Likes only
echo   [5] Follows only
echo   [6] Show Stats
echo.
set /p choice="  Select (1-6): "

if "%choice%"=="1" TikTokBot.exe --once
if "%choice%"=="2" TikTokBot.exe
if "%choice%"=="3" TikTokBot.exe --views
if "%choice%"=="4" TikTokBot.exe --likes
if "%choice%"=="5" TikTokBot.exe --follows
if "%choice%"=="6" TikTokBot.exe --stats

pause
"""
    with open("dist/Launch_TikTokBot.bat", "w") as f:
        f.write(launcher_content)
    print("  [✓] Created dist/Launch_TikTokBot.bat")


def create_readme_dist():
    """Create a simple README for the dist folder."""
    readme = """# TikTok Bot - Windows Edition
# ==============================
#
# Quick Start:
# 1. Make sure Google Chrome is installed
# 2. Edit .env file and set your TikTok username
# 3. Double-click "Launch_TikTokBot.bat" to start
#
# Or run from Command Prompt:
#   TikTokBot.exe --once      (run all bots once)
#   TikTokBot.exe --views     (views only)
#   TikTokBot.exe --likes     (likes only)
#   TikTokBot.exe --follows   (follows only)
#   TikTokBot.exe --stats     (show statistics)
#   TikTokBot.exe             (run on schedule)
#
# Requirements:
# - Windows 10/11
# - Google Chrome installed
# - Internet connection
# - US proxy list (included in us_proxies.txt)
#
# Configuration (.env file):
# - TIKTOK_TARGET_USERNAME = your TikTok username (without @)
# - PROXY_LIST = comma-separated US proxies
# - MAX_VIEWS_PER_SESSION = views per run (default: 50)
# - MAX_LIKES_PER_SESSION = likes per run (default: 20)
# - MAX_FOLLOWS_PER_SESSION = follows per run (default: 10)
#
# To refresh proxies, run: python proxy_scraper.py --update-env
"""
    os.makedirs("dist", exist_ok=True)
    with open("dist/README.txt", "w") as f:
        f.write(readme)
    print("  [✓] Created dist/README.txt")


def show_result():
    """Display build results."""
    exe_path = os.path.join("dist", "TikTokBot.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("\n" + "=" * 60)
        print("  BUILD SUCCESSFUL!")
        print("=" * 60)
        print(f"\n  Output: dist/TikTokBot.exe")
        print(f"  Size:   {size_mb:.1f} MB")
        print(f"\n  Distribution folder contents:")
        for f in sorted(os.listdir("dist")):
            fpath = os.path.join("dist", f)
            fsize = os.path.getsize(fpath) / 1024
            print(f"    - {f} ({fsize:.0f} KB)")
        print(f"\n  To run:")
        print(f"    dist\\TikTokBot.exe --once")
        print(f"    OR double-click dist\\Launch_TikTokBot.bat")
        print("\n" + "=" * 60)
    else:
        # Check onedir build
        onedir_path = os.path.join("dist", "TikTokBot")
        if os.path.exists(onedir_path):
            print("\n" + "=" * 60)
            print("  BUILD SUCCESSFUL (folder mode)!")
            print("=" * 60)
            print(f"\n  Output: dist/TikTokBot/TikTokBot.exe")
            print(f"\n  To distribute, copy the entire dist/TikTokBot/ folder.")
        else:
            print("\n  [ERROR] Build failed. Check the output above for errors.")
            print("  Common fixes:")
            print("    - Run: pip install pyinstaller setuptools")
            print("    - Run: pip install -r requirements.txt")
            print("    - Make sure antivirus isn't blocking PyInstaller")


def main():
    parser = argparse.ArgumentParser(description="Build TikTok Bot Windows .exe")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts before building")
    parser.add_argument("--onedir", action="store_true", help="Build as folder instead of single .exe")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  TikTok Bot - Windows .exe Builder")
    print("=" * 60)

    # Pre-checks
    print("\n  Checking requirements...\n")
    check_python_version()
    check_platform()
    install_pyinstaller()

    if not args.skip_deps:
        install_dependencies()

    if args.clean:
        print("\n  Cleaning previous builds...")
        clean_build()

    # Build
    if args.onedir:
        success = build_onedir()
    else:
        success = build_onefile()

    if success:
        # Post-build
        print("\n  Copying configuration files...")
        copy_config_files()
        create_readme_dist()

    # Results
    show_result()


if __name__ == "__main__":
    main()
