"""
TikTok Bot Configuration Module
Loads settings from environment variables and provides defaults.
"""

import os
import sys
from dotenv import load_dotenv

# Find and load .env from the project directory (handles VS running from different cwd)
_project_root = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_project_root, ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)
else:
    load_dotenv()

# Default US proxy list (fallback if .env not found)
_DEFAULT_PROXIES = (
    "socks5://104.200.135.46:4145,socks5://104.200.152.30:4145,"
    "socks5://107.152.98.5:4145,socks5://107.181.161.81:4145,"
    "socks5://107.181.168.145:4145,socks5://104.37.135.145:4145,"
    "socks5://104.219.236.127:1080,socks5://107.174.183.177:1080,"
    "socks5://104.233.195.149:1080,socks5://129.150.55.165:1080,"
    "socks5://107.219.228.250:7777,socks5://104.248.197.67:1080,"
    "socks5://104.248.203.234:1080,socks5://128.90.145.211:8118,"
    "socks5://131.153.163.164:8080,socks5://131.153.163.166:53281,"
    "socks5://131.153.163.166:8001,socks5://104.37.175.200:22292,"
    "socks5://104.236.171.128:41047,socks5://104.248.158.27:25100"
)


class Config:
    """Bot configuration loaded from .env file."""

    # Target TikTok account
    TARGET_USERNAME = os.getenv("TIKTOK_TARGET_USERNAME", "xxmr.building")

    # Proxy settings (US-based)
    PROXY_LIST = [
        p.strip()
        for p in os.getenv("PROXY_LIST", _DEFAULT_PROXIES).split(",")
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

    # Auto-detect Chrome on Windows
    if not CHROME_BINARY_PATH and sys.platform == "win32":
        _chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ]
        for _path in _chrome_paths:
            if os.path.exists(_path):
                CHROME_BINARY_PATH = _path
                break

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
