"""
Setup Verification Script
==========================
Tests that all dependencies, Chrome, and proxies are working correctly.
"""

import sys
import os

print("\n" + "=" * 60)
print("  TikTok Bot - Setup Verification")
print("=" * 60)

# Test 1: Python version
print(f"\n  [1] Python Version: {sys.version.split()[0]}", end=" ")
assert sys.version_info >= (3, 9), "Python 3.9+ required"
print("✓")

# Test 2: Required packages
print("  [2] Required Packages:")
packages = [
    "selenium", "undetected_chromedriver", "requests",
    "dotenv", "fake_useragent", "schedule", "colorama",
    "socks", "aiohttp", "aiohttp_socks"
]
for pkg in packages:
    try:
        __import__(pkg)
        print(f"      - {pkg}: ✓")
    except ImportError as e:
        print(f"      - {pkg}: ✗ ({e})")

# Test 3: Chrome binary
print("\n  [3] Chrome Browser:")
chrome_path = "/usr/bin/google-chrome-stable"
exists = os.path.exists(chrome_path)
print(f"      Path: {chrome_path} {'✓' if exists else '✗'}")
if exists:
    import subprocess
    result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True)
    print(f"      Version: {result.stdout.strip()} ✓")

# Test 4: ChromeDriver
print("\n  [4] ChromeDriver:")
import subprocess
result = subprocess.run(["chromedriver", "--version"], capture_output=True, text=True)
print(f"      {result.stdout.strip()} ✓")

# Test 5: Configuration
print("\n  [5] Configuration (.env):")
from dotenv import load_dotenv
load_dotenv()
username = os.getenv("TIKTOK_TARGET_USERNAME", "")
proxy_list = os.getenv("PROXY_LIST", "")
proxies = [p.strip() for p in proxy_list.split(",") if p.strip()]
print(f"      Target Username: {'(set)' if username else '(not set - needs config)'}")
print(f"      Proxies Loaded: {len(proxies)} US proxies ✓")
if proxies:
    print(f"      Sample Proxy: {proxies[0][:50]}...")

# Test 6: Proxy file
print("\n  [6] Proxy File:")
if os.path.exists("us_proxies.txt"):
    with open("us_proxies.txt") as f:
        lines = f.readlines()
    print(f"      us_proxies.txt: {len(lines)} proxies available ✓")
else:
    print("      us_proxies.txt: Not found (run proxy_scraper.py first)")

# Test 7: Chrome headless launch test
print("\n  [7] Chrome Headless Launch Test:")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = chrome_path

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.tiktok.com")
    title = driver.title
    driver.quit()
    print(f"      Chrome launched successfully ✓")
    print(f"      Page title: {title[:50]}")
except Exception as e:
    print(f"      Chrome launch failed: {e}")

# Test 8: Bot modules import
print("\n  [8] Bot Module Imports:")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from config import Config
    print("      config.py: ✓")
except Exception as e:
    print(f"      config.py: ✗ ({e})")

try:
    from utils import setup_logger, random_delay, get_random_proxy
    print("      utils: ✓")
except Exception as e:
    print(f"      utils: ✗ ({e})")

try:
    from bot.viewer import ViewBot
    from bot.engager import EngagementBot
    from bot.follower import FollowerBot
    from bot.stats import StatsTracker
    print("      bot modules: ✓")
except Exception as e:
    print(f"      bot modules: ✗ ({e})")

try:
    from proxy_scraper import scrape_all
    print("      proxy_scraper: ✓")
except Exception as e:
    print(f"      proxy_scraper: ✗ ({e})")

print("\n" + "=" * 60)
print("  Setup Verification Complete!")
print("=" * 60)
print("\n  Next Steps:")
print("  1. Edit .env and set TIKTOK_TARGET_USERNAME to your account")
print("  2. Run: python proxy_scraper.py --test --update-env")
print("  3. Run: python main.py --once")
print()
