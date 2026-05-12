"""
TikTok Bot - Main Entry Point
===============================
Automated bot for generating US-based views, followers, likes,
and engagements on TikTok.

Usage:
    python main.py              # Interactive menu mode
    python main.py --views      # Run only view bot
    python main.py --likes      # Run only engagement bot
    python main.py --follows    # Run only follower bot
    python main.py --stats      # Show performance stats
    python main.py --once       # Run all bots once (no scheduling)
    python main.py --menu       # Show interactive menu
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
from utils.display import (
    show_banner, show_config_panel, show_video_links,
    show_session_start, show_action, show_progress_bar,
    show_session_summary, show_stats_panel, show_menu,
    show_error, show_divider, clear_screen,
)

logger = setup_logger("TikTokBot", Config.LOG_FILE, Config.LOG_LEVEL)


def run_view_bot():
    """Execute a view bot session with themed display."""
    show_session_start("views", Config.MAX_VIEWS_PER_SESSION)

    bot = ViewBot()
    start_time = time.time()

    show_action("NAVIGATE", f"Opening @{Config.TARGET_USERNAME} profile...")
    bot.start_session()

    try:
        if not bot.navigate_to_profile():
            show_error("Could not access profile. Check proxy/connection.")
            bot.end_session()
            return 0

        # Get and DISPLAY video links
        video_links = bot.get_video_links()
        show_video_links(video_links, Config.TARGET_USERNAME)

        if not video_links:
            show_error("No videos found on profile.")
            bot.end_session()
            return 0

        show_divider()

        # Watch videos
        import random
        max_views = Config.MAX_VIEWS_PER_SESSION
        for i in range(max_views):
            video_url = random.choice(video_links[:10])
            short_url = video_url[:50] + "..." if len(video_url) > 50 else video_url

            show_action("WATCH", f"Watching: {short_url}", count=i + 1)
            bot.watch_video(video_url)
            show_progress_bar(i + 1, max_views, "Views")

            from utils import random_delay
            random_delay()

            # Proxy rotation
            if (i + 1) % 10 == 0 and (i + 1) < max_views:
                show_action("PROXY", "Rotating to fresh US proxy...")
                bot.end_session()
                random_delay(5, 15)
                bot.start_session()
                if not bot.navigate_to_profile():
                    break
                video_links = bot.get_video_links()

    except Exception as e:
        show_error(f"View bot error: {e}")
    finally:
        bot.end_session()

    duration = time.time() - start_time
    show_session_summary("views", bot.views_generated, duration)

    stats = StatsTracker()
    stats.record_session(views=bot.views_generated)
    return bot.views_generated


def run_engagement_bot():
    """Execute an engagement bot session with themed display."""
    show_session_start("likes", Config.MAX_LIKES_PER_SESSION)

    bot = EngagementBot()
    start_time = time.time()

    show_action("NAVIGATE", f"Opening @{Config.TARGET_USERNAME} profile...")
    bot.start_session()

    try:
        if not bot.navigate_to_profile():
            show_error("Could not access profile.")
            bot.end_session()
            return 0

        video_links = bot.get_video_links()
        show_video_links(video_links, Config.TARGET_USERNAME)

        if not video_links:
            show_error("No videos found.")
            bot.end_session()
            return 0

        show_divider()

        max_likes = Config.MAX_LIKES_PER_SESSION
        for i in range(min(max_likes, len(video_links))):
            video_url = video_links[i]
            short_url = video_url[:50] + "..." if len(video_url) > 50 else video_url

            show_action("LIKE", f"Engaging: {short_url}", count=i + 1)
            bot.engage_with_video(video_url)
            show_progress_bar(i + 1, max_likes, "Likes")

            from utils import random_delay
            random_delay()

            if bot.likes_given >= max_likes:
                break

            if (i + 1) % 8 == 0:
                show_action("PROXY", "Rotating proxy...")
                bot.end_session()
                from utils import random_delay
                random_delay(5, 15)
                bot.start_session()
                if not bot.navigate_to_profile():
                    break
                video_links = bot.get_video_links()

    except Exception as e:
        show_error(f"Engagement bot error: {e}")
    finally:
        bot.end_session()

    duration = time.time() - start_time
    show_session_summary("likes", bot.likes_given, duration)

    stats = StatsTracker()
    stats.record_session(likes=bot.likes_given)
    return bot.likes_given


def run_follower_bot():
    """Execute a follower bot session with themed display."""
    show_session_start("follows", Config.MAX_FOLLOWS_PER_SESSION)

    bot = FollowerBot()
    start_time = time.time()

    max_follows = Config.MAX_FOLLOWS_PER_SESSION
    for i in range(max_follows):
        show_action("FOLLOW", f"Follow attempt #{i + 1}", count=i + 1)
        bot.start_session()

        try:
            if not bot.navigate_to_profile():
                show_action("ERROR", "Could not access profile, retrying...")
                bot.end_session()
                from utils import random_delay
                random_delay(10, 20)
                continue

            bot.follow_account()
            show_progress_bar(i + 1, max_follows, "Follows")

        except Exception as e:
            show_action("ERROR", str(e))
        finally:
            bot.end_session()

        from utils import random_delay
        random_delay(15, 30)

    duration = time.time() - start_time
    show_session_summary("follows", bot.follows_given, duration)

    stats = StatsTracker()
    stats.record_session(follows=bot.follows_given)
    return bot.follows_given


def run_all_bots():
    """Run all bots in sequence with cooldowns."""
    show_divider("═")
    show_action("SUCCESS", "Starting FULL session (Views → Likes → Follows)")
    show_divider("═")

    total_views = run_view_bot()
    show_action("PROXY", "Cooldown 60s before next bot...")
    time.sleep(60)

    total_likes = run_engagement_bot()
    show_action("PROXY", "Cooldown 60s before next bot...")
    time.sleep(60)

    total_follows = run_follower_bot()

    show_divider("═")
    show_action("SUCCESS", f"FULL SESSION DONE! Views: {total_views} | Likes: {total_likes} | Follows: {total_follows}")
    show_divider("═")


def show_stats():
    """Display bot performance statistics with themed UI."""
    stats = StatsTracker()
    show_stats_panel(stats.stats)


def refresh_proxies():
    """Refresh US proxies from free sources."""
    show_action("PROXY", "Fetching fresh US proxies from 7+ sources...")
    try:
        from proxy_scraper import scrape_all, save_proxies, update_env_file
        proxies = scrape_all()
        save_proxies(proxies)
        update_env_file(proxies)
        show_action("SUCCESS", f"Loaded {len(proxies)} fresh US proxies!")
    except Exception as e:
        show_error(f"Proxy scrape failed: {e}")


def interactive_menu():
    """Run the bot in interactive menu mode."""
    while True:
        show_banner()
        show_config_panel(Config.TARGET_USERNAME, len(Config.PROXY_LIST), Config.HEADLESS)

        choice = show_menu()

        if choice == "1":
            run_all_bots()
            show_stats()
            input("\n  Press Enter to continue...")
        elif choice == "2":
            show_action("INFO", f"Scheduling runs every {Config.SESSION_COOLDOWN_MINUTES} min. Press Ctrl+C to stop.")
            schedule.every(Config.SESSION_COOLDOWN_MINUTES).minutes.do(run_all_bots)
            run_all_bots()
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)
            except KeyboardInterrupt:
                show_action("INFO", "Stopped by user.")
                show_stats()
                input("\n  Press Enter to continue...")
        elif choice == "3":
            run_view_bot()
            input("\n  Press Enter to continue...")
        elif choice == "4":
            run_engagement_bot()
            input("\n  Press Enter to continue...")
        elif choice == "5":
            run_follower_bot()
            input("\n  Press Enter to continue...")
        elif choice == "6":
            refresh_proxies()
            input("\n  Press Enter to continue...")
        elif choice == "7":
            show_stats()
            input("\n  Press Enter to continue...")
        elif choice == "8":
            import subprocess
            subprocess.run([sys.executable, "test_setup.py"])
            input("\n  Press Enter to continue...")
        elif choice == "0":
            clear_screen()
            print("\n  Goodbye! Bot stopped.\n")
            sys.exit(0)
        else:
            show_error("Invalid option. Try 0-8.")
            time.sleep(1)


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="TikTok Bot - US Views, Followers & Engagement Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--views", action="store_true", help="Run only the view bot")
    parser.add_argument("--likes", action="store_true", help="Run only the engagement/likes bot")
    parser.add_argument("--follows", action="store_true", help="Run only the follower bot")
    parser.add_argument("--stats", action="store_true", help="Show performance statistics")
    parser.add_argument("--once", action="store_true", help="Run once without scheduling")
    parser.add_argument("--menu", action="store_true", help="Show interactive menu")

    args = parser.parse_args()

    # Show stats and exit
    if args.stats:
        show_banner()
        show_stats()
        return

    # Validate config
    try:
        Config.validate()
    except ValueError as e:
        show_banner()
        show_error(str(e))
        print("\n  Please copy .env.example to .env and fill in your settings.\n")
        sys.exit(1)

    # Display banner
    show_banner()
    show_config_panel(Config.TARGET_USERNAME, len(Config.PROXY_LIST), Config.HEADLESS)

    # CLI mode
    if args.views or args.likes or args.follows or args.once:
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

    # Interactive menu mode (default)
    if args.menu or not any([args.views, args.likes, args.follows, args.once, args.stats]):
        try:
            interactive_menu()
        except KeyboardInterrupt:
            print("\n\n  Bot stopped. Goodbye!\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
