"""
Statistics Tracker Module.
Tracks and displays bot performance metrics.
"""

import json
import os
from datetime import datetime
from utils import setup_logger
from utils.helpers import format_number

logger = setup_logger(__name__)

STATS_FILE = "stats.json"


class StatsTracker:
    """Tracks bot performance and engagement metrics."""

    def __init__(self):
        self.stats = self._load_stats()

    def _load_stats(self) -> dict:
        """Load stats from file or create new."""
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return {
            "total_views": 0,
            "total_likes": 0,
            "total_follows": 0,
            "sessions_completed": 0,
            "first_run": datetime.now().isoformat(),
            "last_run": None,
            "daily_stats": {},
        }

    def _save_stats(self):
        """Save stats to file."""
        try:
            with open(STATS_FILE, "w") as f:
                json.dump(self.stats, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save stats: {e}")

    def record_session(self, views: int = 0, likes: int = 0, follows: int = 0):
        """
        Record a session's results.

        Args:
            views: Number of views generated
            likes: Number of likes given
            follows: Number of follows given
        """
        today = datetime.now().strftime("%Y-%m-%d")

        self.stats["total_views"] += views
        self.stats["total_likes"] += likes
        self.stats["total_follows"] += follows
        self.stats["sessions_completed"] += 1
        self.stats["last_run"] = datetime.now().isoformat()

        # Daily breakdown
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = {
                "views": 0,
                "likes": 0,
                "follows": 0,
                "sessions": 0,
            }

        self.stats["daily_stats"][today]["views"] += views
        self.stats["daily_stats"][today]["likes"] += likes
        self.stats["daily_stats"][today]["follows"] += follows
        self.stats["daily_stats"][today]["sessions"] += 1

        self._save_stats()
        logger.info(
            f"Session recorded - Views: {views}, Likes: {likes}, Follows: {follows}"
        )

    def get_summary(self) -> str:
        """Get a formatted summary of all-time stats."""
        return (
            "\n"
            "====================================\n"
            "     TikTok Bot - Performance Stats\n"
            "====================================\n"
            f"  Total Views:    {format_number(self.stats['total_views'])}\n"
            f"  Total Likes:    {format_number(self.stats['total_likes'])}\n"
            f"  Total Follows:  {format_number(self.stats['total_follows'])}\n"
            f"  Sessions Run:   {self.stats['sessions_completed']}\n"
            f"  First Run:      {self.stats.get('first_run', 'N/A')[:10]}\n"
            f"  Last Run:       {(self.stats.get('last_run') or 'Never')[:10]}\n"
            "====================================\n"
        )

    def get_today_stats(self) -> str:
        """Get today's stats."""
        today = datetime.now().strftime("%Y-%m-%d")
        daily = self.stats["daily_stats"].get(
            today, {"views": 0, "likes": 0, "follows": 0, "sessions": 0}
        )
        return (
            f"Today ({today}): "
            f"Views: {daily['views']} | "
            f"Likes: {daily['likes']} | "
            f"Follows: {daily['follows']} | "
            f"Sessions: {daily['sessions']}"
        )
