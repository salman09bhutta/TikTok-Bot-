"""
Browser driver module.
Creates Chrome instances with US proxy support.
Supports both desktop (undetected-chromedriver) and Termux/Android (selenium).
"""

import platform
import sys
import os

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

    # Chrome binary path
    if Config.CHROME_BINARY_PATH:
        options.binary_location = Config.CHROME_BINARY_PATH

    # Termux-specific options
    if _is_termux():
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--single-process")
        options.add_argument("--disable-features=VizDisplayCompositor")
        # Force headless on Termux (no display)
        if "--headless=new" not in str(options.arguments):
            options.add_argument("--headless=new")

    return options


def _apply_stealth_scripts(driver):
    """Inject JavaScript to hide automation signals."""
    stealth_scripts = [
        # Remove navigator.webdriver flag
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
        # Fake plugins
        "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
        # Fake languages
        "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
        # Override permissions
        """
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
        );
        """,
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

    # Find chromedriver in Termux
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

        # Apply stealth scripts
        _apply_stealth_scripts(driver)

        # Set US geolocation (New York City)
        try:
            driver.execute_cdp_cmd(
                "Emulation.setGeolocationOverride",
                {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "accuracy": 100,
                },
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
    try:
        import undetected_chromedriver as uc
    except ImportError:
        logger.warning("undetected-chromedriver not available, falling back to selenium")
        return _create_driver_selenium_fallback(proxy)

    options = uc.ChromeOptions()

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
    options.add_argument("--timezone=America/New_York")

    if Config.HEADLESS:
        options.add_argument("--headless=new")

    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
        logger.info(f"Using proxy: {proxy[:30]}...")

    if Config.CHROME_BINARY_PATH:
        options.binary_location = Config.CHROME_BINARY_PATH

    try:
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)

        # Set US geolocation (New York City)
        driver.execute_cdp_cmd(
            "Emulation.setGeolocationOverride",
            {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "accuracy": 100,
            },
        )

        # Set US locale
        driver.execute_cdp_cmd(
            "Emulation.setLocaleOverride", {"locale": "en-US"}
        )

        logger.info("Browser driver created successfully (desktop mode)")
        return driver

    except Exception as e:
        logger.error(f"undetected-chromedriver failed: {e}")
        logger.info("Falling back to standard selenium...")
        return _create_driver_selenium_fallback(proxy)


def _create_driver_selenium_fallback(proxy: str = None):
    """Fallback: standard Selenium with stealth scripts."""
    options = _get_stealth_options(proxy)

    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)

        # Apply stealth scripts
        _apply_stealth_scripts(driver)

        # Set US geolocation
        try:
            driver.execute_cdp_cmd(
                "Emulation.setGeolocationOverride",
                {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "accuracy": 100,
                },
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
