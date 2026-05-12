"""
Helper utilities for the TikTok Bot.
Provides randomization functions to mimic human behavior.
"""

import random
import time
from config import Config


def random_delay(min_sec: int = None, max_sec: int = None):
    """
    Sleep for a random duration to mimic human behavior.

    Args:
        min_sec: Minimum sleep time in seconds (default from config)
        max_sec: Maximum sleep time in seconds (default from config)
    """
    min_sec = min_sec or Config.MIN_ACTION_DELAY
    max_sec = max_sec or Config.MAX_ACTION_DELAY
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay


def random_watch_time():
    """
    Get a random video watch time to simulate real viewing.

    Returns:
        Random watch duration in seconds
    """
    return random.uniform(Config.WATCH_TIME_MIN, Config.WATCH_TIME_MAX)


def get_random_proxy():
    """
    Select a random US proxy from the configured list.
    Returns None if proxies are disabled or list is empty.

    Returns:
        Proxy string or None if no proxies configured/enabled
    """
    if not Config.USE_PROXY:
        return None
    if not Config.PROXY_LIST:
        return None
    return random.choice(Config.PROXY_LIST)


def format_number(num: int) -> str:
    """Format a number with K/M suffix for display."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)
