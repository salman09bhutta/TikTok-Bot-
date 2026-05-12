"""
TikTok Auto-Uploader Module
===============================
Uploads videos to TikTok using browser automation (Selenium).
TikTok has NO official public upload API, so we use the web interface.

Requirements:
- Google Chrome installed
- TikTok account logged in via cookies or manual first-time login
- selenium + undetected-chromedriver

Setup:
1. Run once manually - it will open TikTok login page
2. Log in to your TikTok account
3. Cookies are saved for future automated uploads

Usage:
    from tiktok_uploader import TikTokUploader
    tt = TikTokUploader()
    tt.upload("video.mp4", caption="Mini house build #shorts")
"""

import os
import sys
import time
import json
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from config import Config

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

try:
    from rich.console import Console
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def _log(msg, style="magenta"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if HAS_RICH:
        console.print(f"  [{style}][TIKTOK {timestamp}][/] {msg}")
    else:
        print(f"  [TIKTOK {timestamp}] {msg}")


COOKIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_cookies.json")
TIKTOK_UPLOAD_URL = "https://www.tiktok.com/upload"


class TikTokUploader:
    """
    Uploads videos to TikTok via browser automation.
    Saves login cookies so you only need to log in once.
    """

    def __init__(self):
        self.driver = None
        self.logged_in = False
        self.uploads_today = 0

        if not HAS_SELENIUM:
            _log("[red]Selenium not installed. Run: pip install selenium[/]", "red")

    def _create_driver(self, headless: bool = False):
        """Create a Chrome driver for TikTok."""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,900")
        options.add_argument("--lang=en-US")

        if headless:
            options.add_argument("--headless=new")

        # Auto-detect Chrome
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                options.binary_location = path
                break

        try:
            import undetected_chromedriver as uc
            self.driver = uc.Chrome(options=options, browser_executable_path=options.binary_location)
        except Exception:
            try:
                from selenium.webdriver.chrome.service import Service
                self.driver = webdriver.Chrome(options=options)
            except Exception as e:
                _log(f"[red]Failed to create browser: {e}[/]", "red")
                return False

        self.driver.set_page_load_timeout(60)
        self.driver.implicitly_wait(10)
        return True

    def _save_cookies(self):
        """Save browser cookies to file."""
        if self.driver:
            cookies = self.driver.get_cookies()
            with open(COOKIES_FILE, "w") as f:
                json.dump(cookies, f, indent=2)
            _log("Cookies saved for future sessions")

    def _load_cookies(self) -> bool:
        """Load saved cookies into browser."""
        if not os.path.exists(COOKIES_FILE):
            return False

        try:
            with open(COOKIES_FILE, "r") as f:
                cookies = json.load(f)

            # Navigate to TikTok first (cookies need matching domain)
            self.driver.get("https://www.tiktok.com")
            time.sleep(2)

            for cookie in cookies:
                try:
                    # Remove problematic fields
                    cookie.pop("sameSite", None)
                    cookie.pop("storeId", None)
                    if "expiry" in cookie:
                        cookie["expiry"] = int(cookie["expiry"])
                    self.driver.add_cookie(cookie)
                except Exception:
                    continue

            _log("Cookies loaded from previous session")
            return True

        except Exception as e:
            _log(f"[yellow]Cookie load failed: {e}[/]", "yellow")
            return False

    def _check_login(self) -> bool:
        """Check if we're logged in to TikTok."""
        try:
            self.driver.get("https://www.tiktok.com/upload")
            time.sleep(3)

            # If redirected to login page, not logged in
            current_url = self.driver.current_url
            if "login" in current_url.lower():
                return False

            # Check for upload form
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
                return True
            except TimeoutException:
                return False

        except Exception:
            return False

    def login(self, headless: bool = False) -> bool:
        """
        Log in to TikTok. First time opens browser for manual login.
        Subsequent times use saved cookies.

        Args:
            headless: Run without visible browser (only works after first login)

        Returns:
            True if login successful
        """
        if not HAS_SELENIUM:
            _log("[red]Selenium required for TikTok upload[/]", "red")
            return False

        # Create browser
        if not self._create_driver(headless=headless):
            return False

        # Try loading saved cookies
        if self._load_cookies():
            if self._check_login():
                self.logged_in = True
                _log("[green]Logged in with saved cookies![/]", "green")
                return True

        # Manual login required
        if headless:
            _log("[yellow]Cannot login in headless mode. Run once with headless=False[/]", "yellow")
            self.close()
            return False

        _log("Opening TikTok login page...")
        _log("[yellow]Please log in manually in the browser window[/]", "yellow")
        _log("[yellow]After logging in, the script will continue automatically[/]", "yellow")

        self.driver.get("https://www.tiktok.com/login")

        # Wait for user to log in (check every 5 seconds)
        _log("Waiting for login...")
        for _ in range(60):  # Wait up to 5 minutes
            time.sleep(5)
            try:
                current_url = self.driver.current_url
                if "login" not in current_url.lower() and "tiktok.com" in current_url:
                    # Check if we can access upload page
                    time.sleep(2)
                    self.driver.get("https://www.tiktok.com/upload")
                    time.sleep(3)
                    if "login" not in self.driver.current_url.lower():
                        self.logged_in = True
                        self._save_cookies()
                        _log("[green]Login successful! Cookies saved.[/]", "green")
                        return True
            except Exception:
                continue

        _log("[red]Login timed out (5 min)[/]", "red")
        return False

    def upload(self, video_path: str, caption: str = "",
               headless: bool = False) -> dict:
        """
        Upload a video to TikTok.

        Args:
            video_path: Path to the video file (.mp4)
            caption: Video caption with hashtags
            headless: Run without visible browser

        Returns:
            Dict with upload result, or None if failed
        """
        if not os.path.exists(video_path):
            _log(f"[red]Video not found: {video_path}[/]", "red")
            return None

        # Login if not already
        if not self.logged_in:
            if not self.login(headless=headless):
                return None

        _log(f"Uploading: {os.path.basename(video_path)}")

        try:
            # Navigate to upload page
            self.driver.get(TIKTOK_UPLOAD_URL)
            time.sleep(3)

            # Find the file input and upload
            file_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
            )

            # Upload the video file
            abs_path = os.path.abspath(video_path)
            file_input.send_keys(abs_path)
            _log("Video file selected, waiting for processing...")

            # Wait for video to process (up to 3 minutes)
            time.sleep(10)

            # Wait for the processing to complete
            for _ in range(36):  # 3 minutes max
                try:
                    # Check for upload progress/completion indicators
                    page_source = self.driver.page_source.lower()
                    if "uploaded" in page_source or "post" in page_source:
                        break
                except Exception:
                    pass
                time.sleep(5)

            _log("Video processed. Adding caption...")

            # Find caption input and type caption
            try:
                # Try multiple selectors for the caption field
                caption_selectors = [
                    '[data-e2e="caption-input"]',
                    'div[contenteditable="true"]',
                    '.public-DraftEditor-content',
                    '[role="textbox"]',
                    'div[class*="caption"] [contenteditable]',
                ]

                caption_input = None
                for selector in caption_selectors:
                    try:
                        caption_input = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        if caption_input:
                            break
                    except TimeoutException:
                        continue

                if caption_input:
                    caption_input.click()
                    time.sleep(0.5)

                    # Clear existing text
                    caption_input.send_keys(Keys.CONTROL + "a")
                    caption_input.send_keys(Keys.DELETE)
                    time.sleep(0.3)

                    # Type caption (character by character for special chars)
                    for char in caption[:2200]:  # TikTok caption limit
                        caption_input.send_keys(char)
                        time.sleep(random.uniform(0.01, 0.05))

                    _log(f"Caption added: {caption[:50]}...")
                else:
                    _log("[yellow]Caption field not found[/]", "yellow")

            except Exception as e:
                _log(f"[yellow]Caption input error: {e}[/]", "yellow")

            time.sleep(2)

            # Click Post/Upload button
            _log("Clicking Post button...")
            post_selectors = [
                '[data-e2e="post-button"]',
                'button[class*="post"]',
                'button[class*="submit"]',
                '//button[contains(text(), "Post")]',
                '//button[contains(text(), "Upload")]',
            ]

            posted = False
            for selector in post_selectors:
                try:
                    if selector.startswith("//"):
                        btn = self.driver.find_element(By.XPATH, selector)
                    else:
                        btn = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if btn and btn.is_enabled():
                        btn.click()
                        posted = True
                        _log("Post button clicked!", "green")
                        break
                except Exception:
                    continue

            if not posted:
                _log("[yellow]Could not find Post button. Video may need manual posting.[/]", "yellow")

            # Wait for upload to complete
            time.sleep(10)

            # Check for success
            try:
                page_source = self.driver.page_source.lower()
                if "uploaded" in page_source or "manage" in page_source or "your video" in page_source:
                    self.uploads_today += 1
                    _log("[green]TikTok upload successful![/]", "green")

                    result = {
                        "success": True,
                        "platform": "tiktok",
                        "video": os.path.basename(video_path),
                        "caption": caption[:100],
                        "uploaded_at": datetime.now().isoformat(),
                        "url": f"https://www.tiktok.com/@{Config.TIKTOK_USERNAME}" if hasattr(Config, 'TIKTOK_USERNAME') else None,
                    }

                    self._save_cookies()
                    return result
            except Exception:
                pass

            _log("[yellow]Upload status unclear. Check TikTok manually.[/]", "yellow")
            return {"success": True, "platform": "tiktok", "status": "pending_verification"}

        except Exception as e:
            _log(f"[red]Upload error: {e}[/]", "red")
            return None

    def close(self):
        """Close the browser."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.logged_in = False
        except Exception:
            pass

    def __del__(self):
        self.close()


# ═══════════════════════════════════════════════════════════
# Standalone usage
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TikTok Video Uploader")
    parser.add_argument("--video", type=str, help="Path to video file")
    parser.add_argument("--caption", type=str, default="", help="Video caption")
    parser.add_argument("--login", action="store_true", help="Just login and save cookies")
    args = parser.parse_args()

    tt = TikTokUploader()

    if args.login:
        print("\n  TikTok Login - Opening browser...")
        print("  Log in manually, cookies will be saved.\n")
        tt.login(headless=False)
    elif args.video:
        result = tt.upload(args.video, caption=args.caption)
        if result:
            print(f"\n  Upload result: {result}")
    else:
        print("\n  TikTok Uploader - Mini Building Construction")
        print("  " + "=" * 50)
        print(f"  Selenium: {'Installed' if HAS_SELENIUM else 'Missing'}")
        print(f"  Cookies: {'Found' if os.path.exists(COOKIES_FILE) else 'Not saved (login needed)'}")
        print(f"\n  Usage:")
        print(f"    python tiktok_uploader.py --login")
        print(f'    python tiktok_uploader.py --video "output/short.mp4" --caption "Mini build"')
        print()

    tt.close()
