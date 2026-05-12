"""
AI Content Engine Configuration
"""

import os
import sys
from dotenv import load_dotenv

# Load .env from project directory
_project_root = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_project_root, ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)
else:
    load_dotenv()


class Config:
    """Content Engine configuration."""

    # === AI API Keys ===
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # === Free Stock Footage API Keys ===
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")

    # === YouTube API ===
    YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secrets.json")
    YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")

    # === Content Niche ===
    NICHE = "Mini Building Construction"
    NICHE_KEYWORDS = [
        "miniature construction", "mini building", "tiny house build",
        "mini bricklaying", "cement craft", "mini architecture",
        "satisfying construction", "miniature woodworking", "tiny construction",
        "mini DIY build", "small scale building", "miniature house",
        "construction timelapse", "mini concrete", "micro building",
    ]

    # === Video Settings ===
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920  # 9:16 vertical
    VIDEO_FPS = 30
    VIDEO_MAX_DURATION = 60  # seconds (Shorts limit)
    VIDEO_MIN_DURATION = 15

    # === Paths ===
    OUTPUT_DIR = os.path.join(_project_root, "output")
    FOOTAGE_DIR = os.path.join(_project_root, "footage")
    MUSIC_DIR = os.path.join(_project_root, "music")
    FONTS_DIR = os.path.join(_project_root, "fonts")

    # === Posting Schedule ===
    POSTS_PER_DAY = int(os.getenv("POSTS_PER_DAY", "3"))
    POST_TIMES = os.getenv("POST_TIMES", "09:00,13:00,18:00").split(",")

    @classmethod
    def ensure_dirs(cls):
        """Create required directories."""
        for d in [cls.OUTPUT_DIR, cls.FOOTAGE_DIR, cls.MUSIC_DIR, cls.FONTS_DIR]:
            os.makedirs(d, exist_ok=True)

    @classmethod
    def validate(cls):
        """Validate required config."""
        warnings = []
        if not cls.OPENAI_API_KEY and not cls.GEMINI_API_KEY:
            warnings.append("No AI API key set (OPENAI_API_KEY or GEMINI_API_KEY)")
        return warnings
