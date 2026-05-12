"""
TikTok Bot Configuration Module
Loads settings from environment variables and provides defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Bot configuration loaded from .env file."""

    # Target TikTok account
    TARGET_USERNAME = os.getenv("TIKTOK_TARGET_USERNAME", "")

    # Proxy settings (US-based)
    PROXY_LIST = [
        p.strip()
        for p in os.getenv("PROXY_LIST", "").split(",")
        if p.strip()
    ]

    # Session limits
    MAX_VIEWS_PER_SESSION = int(os.getenv("MAX_VIEWS_PER_SESSION", "50"))
    MAX_LIKES_PER_SESSION = int(os.getenv("MAX_LIKES_PER_SESSION", "20"))
    MAX_FOLLOWS_PER_SESSION = int(os.getenv("MAX_FOLLOWS_PER_SESSION", "10"))

    # Watch time range (seconds)
    WATCH_TIME_MIN = int(os.getenv("WATCH_TIME_MIN_SECONDS", "15"))
    WATCH_TIME_MAX = int(os.getenv("WATCH_TIME_MAX_SECONDS", "60"))

    # Delays
    MIN_ACTION_DELAY = int(os.getenv("MIN_ACTION_DELAY", "3"))
    MAX_ACTION_DELAY = int(os.getenv("MAX_ACTION_DELAY", "10"))
    SESSION_COOLDOWN_MINUTES = int(os.getenv("SESSION_COOLDOWN_MINUTES", "30"))

    # Browser
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
    CHROME_BINARY_PATH = os.getenv("CHROME_BINARY_PATH", "")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "bot.log")

    # TikTok URLs
    BASE_URL = "https://www.tiktok.com"
    PROFILE_URL = f"https://www.tiktok.com/@{TARGET_USERNAME}"

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []
        if not cls.TARGET_USERNAME:
            errors.append("TIKTOK_TARGET_USERNAME is required")
        if not cls.PROXY_LIST:
            errors.append(
                "PROXY_LIST is required (US proxies needed for US engagement)"
            )
        if errors:
            raise ValueError(
                "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
            )
