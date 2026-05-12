"""
TikTok Bot - Main Entry Point
===============================
Automated bot for generating US-based views, followers, likes,
and engagements on TikTok.

Usage:
    python main.py              # Run all bots in scheduled mode
    python main.py --views      # Run only view bot
    python main.py --likes      # Run only engagement bot
    python main.py --follows    # Run only follower bot
    python main.py --stats      # Show performance stats
    python main.py --once       # Run all bots once (no scheduling)
"""

import argparse
import sys
import time
import schedule

from config import Config
from bot.viewer import ViewBot
from bot.engager import EngagementBot
from bot.follower import FollowerBot
from bot.stats import StatsTracker
from utils import setup_logger

logger = setup_logger("TikTokBot", Config.LOG_FILE, Config.LOG_LEVEL)


def run_view_bot():
    """Execute a view bot session."""
    logger.info("=" * 50)
    logger.info("Starting View Bot Session")
    logger.info("=" * 50)

    bot = ViewBot()
    bot.run()

    stats = StatsTracker()
    stats.record_session(views=bot.views_generated)
    return bot.views_generated


def run_engagement_bot():
    """Execute an engagement bot session."""
    logger.info("=" * 50)
    logger.info("Starting Engagement Bot Session")
    logger.info("=" * 50)

    bot = EngagementBot()
    bot.run()

    stats = StatsTracker()
    stats.record_session(likes=bot.likes_given)
    return bot.likes_given


def run_follower_bot():
    """Execute a follower bot session."""
    logger.info("=" * 50)
    logger.info("Starting Follower Bot Session")
    logger.info("=" * 50)

    bot = FollowerBot()
    bot.run()

    stats = StatsTracker()
    stats.record_session(follows=bot.follows_given)
    return bot.follows_given


def run_all_bots():
    """Run all bots in sequence with cooldowns."""
    logger.info("*" * 60)
    logger.info("  TikTok Bot - Full Session Starting")
    logger.info("  Target: @" + Config.TARGET_USERNAME)
    logger.info("*" * 60)

    total_views = run_view_bot()
    time.sleep(60)  # 1 min cooldown between bots

    total_likes = run_engagement_bot()
    time.sleep(60)

    total_follows = run_follower_bot()

    logger.info("*" * 60)
    logger.info("  Full Session Complete!")
    logger.info(f"  Views: {total_views} | Likes: {total_likes} | Follows: {total_follows}")
    logger.info("*" * 60)


def show_stats():
    """Display bot performance statistics."""
    stats = StatsTracker()
    print(stats.get_summary())
    print(stats.get_today_stats())


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="TikTok Bot - US Views, Followers & Engagement Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--views", action="store_true", help="Run only the view bot"
    )
    parser.add_argument(
        "--likes", action="store_true", help="Run only the engagement/likes bot"
    )
    parser.add_argument(
        "--follows", action="store_true", help="Run only the follower bot"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Show performance statistics"
    )
    parser.add_argument(
        "--once", action="store_true", help="Run once without scheduling"
    )

    args = parser.parse_args()

    # Show stats and exit
    if args.stats:
        show_stats()
        return

    # Validate config
    try:
        Config.validate()
    except ValueError as e:
        logger.error(str(e))
        print(f"\nConfiguration Error:\n{e}")
        print("\nPlease copy .env.example to .env and fill in your settings.")
        sys.exit(1)

    print(
        """
    ╔══════════════════════════════════════════════════╗
    ║          TikTok Bot - US Engagement              ║
    ║    Views | Followers | Likes | Engagement        ║
    ╚══════════════════════════════════════════════════╝
    """
    )
    logger.info(f"Target: @{Config.TARGET_USERNAME}")
    logger.info(f"Proxies configured: {len(Config.PROXY_LIST)}")
    logger.info(f"Headless mode: {Config.HEADLESS}")

    # Single run mode
    if args.once or args.views or args.likes or args.follows:
        if args.views:
            run_view_bot()
        elif args.likes:
            run_engagement_bot()
        elif args.follows:
            run_follower_bot()
        else:
            run_all_bots()
        show_stats()
        return

    # Scheduled mode - run periodically
    logger.info(
        f"Scheduling bot runs every {Config.SESSION_COOLDOWN_MINUTES} minutes"
    )

    schedule.every(Config.SESSION_COOLDOWN_MINUTES).minutes.do(run_all_bots)

    # Run immediately on start
    run_all_bots()

    # Keep running on schedule
    logger.info("Bot is running in scheduled mode. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
        show_stats()


if __name__ == "__main__":
    main()
