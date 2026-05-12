"""
View Bot Module.
Automatically generates views on TikTok videos from US-based traffic.
"""

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from browser import create_driver, close_driver
from config import Config
from utils import setup_logger, random_delay, random_watch_time, get_random_proxy

logger = setup_logger(__name__)


class ViewBot:
    """Bot for generating video views from US-based IPs."""

    def __init__(self):
        self.driver = None
        self.views_generated = 0
        self.session_active = False

    def start_session(self, use_proxy=True):
        """Start a new viewing session with a fresh browser and proxy."""
        proxy = get_random_proxy() if use_proxy else None
        self.driver = create_driver(proxy=proxy)
        self.session_active = True
        logger.info(f"View bot session started {'with proxy' if proxy else 'direct connection'}")

    def end_session(self):
        """End the current session and clean up."""
        self.session_active = False
        close_driver(self.driver)
        self.driver = None
        logger.info(
            f"View session ended. Views generated this session: {self.views_generated}"
        )

    def navigate_to_profile(self):
        """Navigate to the target TikTok profile page."""
        try:
            self.driver.get(Config.PROFILE_URL)
            random_delay(3, 7)

            # Try multiple selectors (TikTok changes their HTML frequently)
            selectors = [
                '[data-e2e="user-post-item"]',
                '[data-e2e="user-post-item-list"]',
                'div[class*="DivItemContainer"]',
                'div[class*="video-feed"]',
                'a[href*="/video/"]',
            ]

            for selector in selectors:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Navigated to profile: @{Config.TARGET_USERNAME}")
                    return True
                except TimeoutException:
                    continue

            # If no video selectors found, check if page loaded at all
            if Config.TARGET_USERNAME.lower() in self.driver.page_source.lower():
                logger.info(f"Profile loaded (no videos yet): @{Config.TARGET_USERNAME}")
                return True

            logger.warning("Profile page timed out or videos not found")
            return False

        except TimeoutException:
            logger.warning("Profile page timed out or videos not found")
            return False
        except Exception as e:
            logger.error(f"Error navigating to profile: {e}")
            return False

    def get_video_links(self):
        """Extract video links from the profile page."""
        try:
            links = []

            # Try multiple CSS selectors
            selectors = [
                '[data-e2e="user-post-item"] a',
                '[data-e2e="user-post-item-list"] a',
                'a[href*="/video/"]',
                'div[class*="DivItemContainer"] a',
            ]

            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    href = el.get_attribute("href")
                    if href and "/video/" in href and href not in links:
                        links.append(href)
                if links:
                    break

            # Scroll down to load more videos
            if not links:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                random_delay(2, 4)
                elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')
                for el in elements:
                    href = el.get_attribute("href")
                    if href and "/video/" in href and href not in links:
                        links.append(href)

            logger.info(f"Found {len(links)} videos on profile")
            return links
        except Exception as e:
            logger.error(f"Error extracting video links: {e}")
            return []

    def watch_video(self, video_url: str):
        """
        Navigate to a video and watch it for a random duration.

        Args:
            video_url: Direct URL to the TikTok video

        Returns:
            True if the video was watched successfully
        """
        try:
            self.driver.get(video_url)
            random_delay(2, 4)

            # Wait for video player to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "video")
                )
            )

            # Watch the video for a random duration
            watch_time = random_watch_time()
            logger.info(f"Watching video for {watch_time:.1f}s: {video_url[:60]}...")

            # Simulate human behavior - occasional scrolling
            elapsed = 0
            while elapsed < watch_time:
                chunk = min(random.uniform(3, 8), watch_time - elapsed)
                time.sleep(chunk)
                elapsed += chunk

                # Random scroll to simulate engagement
                if random.random() < 0.3:
                    scroll_amount = random.randint(-100, 200)
                    self.driver.execute_script(
                        f"window.scrollBy(0, {scroll_amount})"
                    )

            self.views_generated += 1
            logger.info(
                f"View #{self.views_generated} completed on video"
            )
            return True

        except TimeoutException:
            logger.warning(f"Video timed out: {video_url[:60]}...")
            return False
        except Exception as e:
            logger.error(f"Error watching video: {e}")
            return False

    def run(self, max_views: int = None):
        """
        Run the view bot for a full session.

        Args:
            max_views: Maximum views to generate (default from config)
        """
        max_views = max_views or Config.MAX_VIEWS_PER_SESSION
        self.views_generated = 0

        logger.info(f"Starting view bot session (target: {max_views} views)")

        # Try direct connection first, then with proxy (retry up to 3 times)
        connected = False
        for attempt in range(3):
            use_proxy = attempt > 0  # First try: no proxy; then with proxy
            logger.info(f"Connection attempt {attempt + 1}/3 ({'proxy' if use_proxy else 'direct'})")
            self.start_session(use_proxy=use_proxy)

            if self.navigate_to_profile():
                connected = True
                break
            else:
                logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                self.end_session()
                random_delay(3, 8)

        if not connected:
            logger.error("Could not access profile after 3 attempts.")
            return

        try:

            video_links = self.get_video_links()
            if not video_links:
                logger.error("No videos found. Ending session.")
                return

            for i in range(max_views):
                # Pick a random video (weighted toward recent/top videos)
                video_url = random.choice(video_links[:10])
                self.watch_video(video_url)
                random_delay()

                # Rotate proxy periodically
                if (i + 1) % 10 == 0:
                    logger.info("Rotating proxy...")
                    self.end_session()
                    random_delay(5, 15)
                    self.start_session()
                    if not self.navigate_to_profile():
                        break
                    video_links = self.get_video_links()

            logger.info(
                f"View session complete. Total views: {self.views_generated}"
            )

        except Exception as e:
            logger.error(f"View bot error: {e}")
        finally:
            self.end_session()
