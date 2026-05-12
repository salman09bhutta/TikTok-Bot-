"""
Browser driver module.
Creates Chrome instances with US proxy support.
Supports both desktop (undetected-chromedriver) and Termux/Android (selenium).
Auto-detects Chrome location on Windows/Mac/Linux.
"""

import platform
import sys
import os
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from config import Config
from utils import setup_logger

logger = setup_logger(__name__)


def _is_termux():
    """Check if running inside Termux on Android."""
    return os.path.exists("/data/data/com.termux") or "com.termux" in os.environ.get("PREFIX", "")


def _find_chrome_binary():
    """Auto-detect Chrome/Chromium binary path on any platform."""
    # If configured in .env, use that
    if Config.CHROME_BINARY_PATH and os.path.exists(Config.CHROME_BINARY_PATH):
        return Config.CHROME_BINARY_PATH

    if sys.platform == "win32":
        # Windows common Chrome locations
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
            # Edge as fallback (Chromium-based)
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found Chrome at: {path}")
                return path

    elif sys.platform == "darwin":
        # macOS
        mac_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
        for path in mac_paths:
            if os.path.exists(path):
                return path

    else:
        # Linux
        linux_paths = [
            "/usr/bin/google-chrome-stable",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
        ]
        for path in linux_paths:
            if os.path.exists(path):
                return path

    # Try to find via 'where' (Windows) or 'which' (Unix)
    try:
        cmd = "where" if sys.platform == "win32" else "which"
        result = subprocess.run(
            [cmd, "chrome" if sys.platform == "win32" else "google-chrome"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")[0]
    except Exception:
        pass

    return None


def _get_chromedriver_service():
    """Get ChromeDriver service, auto-downloading if needed."""
    try:
        # Try webdriver-manager first (auto-downloads matching chromedriver)
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service as ChromeService
        driver_path = ChromeDriverManager().install()
        return ChromeService(driver_path)
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"webdriver-manager failed: {e}")

    # Try system chromedriver
    try:
        cmd = "where" if sys.platform == "win32" else "which"
        result = subprocess.run([cmd, "chromedriver"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            return Service(result.stdout.strip().split("\n")[0])
    except Exception:
        pass

    # Return None - let Selenium try to find it
    return None


def _get_stealth_options(proxy: str = None):
    """Build Chrome options with anti-detection and US geo settings."""
    options = Options()

    # Anti-detection settings
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f"--user-agent={user_agent}")

    # Performance and stealth options
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")

    # Set timezone to US Eastern
    options.add_argument("--timezone=America/New_York")

    if Config.HEADLESS:
        options.add_argument("--headless=new")

    # Proxy configuration for US traffic
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
        logger.info(f"Using proxy: {proxy[:30]}...")

    # Set Chrome binary path
    chrome_path = _find_chrome_binary()
    if chrome_path:
        options.binary_location = chrome_path

    # Termux-specific options
    if _is_termux():
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--single-process")
        options.add_argument("--disable-features=VizDisplayCompositor")
        if "--headless=new" not in str(options.arguments):
            options.add_argument("--headless=new")

    return options


def _apply_stealth_scripts(driver):
    """Inject JavaScript to hide automation signals."""
    stealth_scripts = [
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
        "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
        "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
    ]
    for script in stealth_scripts:
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
        except Exception:
            try:
                driver.execute_script(script)
            except Exception:
                pass


def _create_driver_termux(proxy: str = None):
    """Create a Selenium Chrome driver for Termux/Android."""
    options = _get_stealth_options(proxy)

    chromedriver_paths = [
        "/data/data/com.termux/files/usr/bin/chromedriver",
        "/data/data/com.termux/files/usr/bin/chromium-chromedriver",
    ]

    service = None
    for path in chromedriver_paths:
        if os.path.exists(path):
            service = Service(path)
            break

    try:
        if service:
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)

        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        _apply_stealth_scripts(driver)

        try:
            driver.execute_cdp_cmd(
                "Emulation.setGeolocationOverride",
                {"latitude": 40.7128, "longitude": -74.0060, "accuracy": 100},
            )
        except Exception:
            pass

        logger.info("Browser driver created successfully (Termux mode)")
        return driver

    except Exception as e:
        logger.error(f"Failed to create browser driver (Termux): {e}")
        raise


def _create_driver_desktop(proxy: str = None):
    """Create an undetected Chrome driver for desktop (Windows/Linux/Mac)."""
    chrome_path = _find_chrome_binary()

    # Try undetected-chromedriver first
    try:
        import undetected_chromedriver as uc

        options = uc.ChromeOptions()

        ua = UserAgent()
        options.add_argument(f"--user-agent={ua.random}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--lang=en-US")
        options.add_argument("--timezone=America/New_York")

        if Config.HEADLESS:
            options.add_argument("--headless=new")

        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
            logger.info(f"Using proxy: {proxy[:30]}...")

        if chrome_path:
            options.binary_location = chrome_path

        driver = uc.Chrome(
            options=options,
            browser_executable_path=chrome_path,
        )
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)

        driver.execute_cdp_cmd(
            "Emulation.setGeolocationOverride",
            {"latitude": 40.7128, "longitude": -74.0060, "accuracy": 100},
        )
        driver.execute_cdp_cmd("Emulation.setLocaleOverride", {"locale": "en-US"})

        logger.info("Browser driver created successfully (desktop mode)")
        return driver

    except ImportError:
        logger.warning("undetected-chromedriver not available, using selenium")
    except Exception as e:
        logger.error(f"undetected-chromedriver failed: {e}")
        logger.info("Falling back to standard selenium...")

    # Fallback: standard Selenium
    return _create_driver_selenium_fallback(proxy)


def _create_driver_selenium_fallback(proxy: str = None):
    """Fallback: standard Selenium with stealth scripts."""
    options = _get_stealth_options(proxy)
    service = _get_chromedriver_service()

    try:
        if service:
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)

        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        _apply_stealth_scripts(driver)

        try:
            driver.execute_cdp_cmd(
                "Emulation.setGeolocationOverride",
                {"latitude": 40.7128, "longitude": -74.0060, "accuracy": 100},
            )
        except Exception:
            pass

        logger.info("Browser driver created successfully (selenium fallback)")
        return driver

    except Exception as e:
        logger.error(f"Failed to create browser driver: {e}")
        raise


def create_driver(proxy: str = None):
    """
    Create a Chrome WebDriver instance with anti-detection.
    Automatically picks the right method based on the platform.

    Args:
        proxy: Optional proxy URL (e.g., socks5://user:pass@host:port)

    Returns:
        Configured Chrome WebDriver instance
    """
    if _is_termux():
        return _create_driver_termux(proxy)
    else:
        return _create_driver_desktop(proxy)


def close_driver(driver):
    """Safely close and quit the WebDriver instance."""
    try:
        if driver:
            driver.quit()
            logger.info("Browser driver closed")
    except Exception as e:
        logger.warning(f"Error closing driver: {e}")
