"""
Browser driver module.
Creates undetected Chrome instances with US proxy support.
"""

import undetected_chromedriver as uc
from fake_useragent import UserAgent
from config import Config
from utils import setup_logger

logger = setup_logger(__name__)


def create_driver(proxy: str = None):
    """
    Create an undetected Chrome WebDriver instance.

    Args:
        proxy: Optional proxy URL (e.g., socks5://user:pass@host:port)

    Returns:
        Configured Chrome WebDriver instance
    """
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

        logger.info("Browser driver created successfully")
        return driver

    except Exception as e:
        logger.error(f"Failed to create browser driver: {e}")
        raise


def close_driver(driver):
    """Safely close and quit the WebDriver instance."""
    try:
        if driver:
            driver.quit()
            logger.info("Browser driver closed")
    except Exception as e:
        logger.warning(f"Error closing driver: {e}")
