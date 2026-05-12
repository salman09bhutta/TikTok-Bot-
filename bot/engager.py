"""
Engagement Bot Module.
Automatically likes and comments on TikTok videos to boost engagement.
"""

import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from browser import create_driver, close_driver
from config import Config
from utils import setup_logger, random_delay, random_watch_time, get_random_proxy

logger = setup_logger(__name__)


class EngagementBot:
    """Bot for generating likes and engagement from US-based IPs."""

    def __init__(self):
        self.driver = None
        self.likes_given = 0
        self.session_active = False

    def start_session(self):
        """Start a new engagement session."""
        proxy = get_random_proxy()
        self.driver = create_driver(proxy=proxy)
        self.session_active = True
        logger.info("Engagement bot session started")

    def end_session(self):
        """End the current session and clean up."""
        self.session_active = False
        close_driver(self.driver)
        self.driver = None
        logger.info(
            f"Engagement session ended. Likes given: {self.likes_given}"
        )

    def navigate_to_profile(self):
        """Navigate to the target TikTok profile."""
        try:
            self.driver.get(Config.PROFILE_URL)
            random_delay(2, 5)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[data-e2e="user-post-item"]')
                )
            )
            logger.info(f"Navigated to @{Config.TARGET_USERNAME}")
            return True
        except Exception as e:
            logger.error(f"Error navigating to profile: {e}")
            return False

    def get_video_links(self):
        """Get video links from the profile."""
        try:
            elements = self.driver.find_elements(
                By.CSS_SELECTOR, '[data-e2e="user-post-item"] a'
            )
            links = [el.get_attribute("href") for el in elements if el.get_attribute("href")]
            return links
        except Exception as e:
            logger.error(f"Error getting video links: {e}")
            return []

    def like_video(self, video_url: str):
        """
        Navigate to a video and like it.

        Args:
            video_url: Direct URL to the TikTok video

        Returns:
            True if the like was successful
        """
        try:
            self.driver.get(video_url)
            random_delay(2, 4)

            # Wait for video to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
            )

            # Watch for a bit before liking (appear natural)
            watch_time = random_watch_time()
            import time
            time.sleep(min(watch_time, 10))

            # Find and click the like button
            like_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[data-e2e="like-icon"]')
                )
            )

            # Human-like: move to element then click
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.move_to_element(like_button).pause(
                random.uniform(0.3, 1.0)
            ).click().perform()

            self.likes_given += 1
            logger.info(f"Like #{self.likes_given} on: {video_url[:60]}...")
            random_delay(1, 3)
            return True

        except TimeoutException:
            logger.warning(f"Timeout liking video: {video_url[:60]}...")
            return False
        except Exception as e:
            logger.error(f"Error liking video: {e}")
            return False

    def engage_with_video(self, video_url: str):
        """
        Full engagement on a video: watch + like + optional share interaction.

        Args:
            video_url: Direct URL to the TikTok video
        """
        try:
            self.driver.get(video_url)
            random_delay(2, 4)

            # Watch the video first
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
            )

            import time
            watch_time = random_watch_time()
            time.sleep(watch_time)

            # Like the video
            try:
                like_btn = self.driver.find_element(
                    By.CSS_SELECTOR, '[data-e2e="like-icon"]'
                )
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.move_to_element(like_btn).pause(
                    random.uniform(0.5, 1.5)
                ).click().perform()
                self.likes_given += 1
                logger.info(f"Engaged (like) on: {video_url[:50]}...")
            except Exception:
                logger.debug("Like button not clickable or already liked")

            random_delay(1, 3)

            # Simulate share button hover (boosts engagement signal)
            if random.random() < 0.2:
                try:
                    share_btn = self.driver.find_element(
                        By.CSS_SELECTOR, '[data-e2e="share-icon"]'
                    )
                    actions = ActionChains(self.driver)
                    actions.move_to_element(share_btn).pause(1.0).perform()
                    logger.debug("Hovered share button")
                except Exception:
                    pass

            return True

        except Exception as e:
            logger.error(f"Error engaging with video: {e}")
            return False

    def run(self, max_likes: int = None):
        """
        Run the engagement bot for a full session.

        Args:
            max_likes: Maximum likes to give (default from config)
        """
        max_likes = max_likes or Config.MAX_LIKES_PER_SESSION
        self.likes_given = 0

        logger.info(f"Starting engagement session (target: {max_likes} likes)")
        self.start_session()

        try:
            if not self.navigate_to_profile():
                logger.error("Could not access profile. Ending session.")
                return

            video_links = self.get_video_links()
            if not video_links:
                logger.error("No videos found. Ending session.")
                return

            for i in range(min(max_likes, len(video_links))):
                video_url = video_links[i]
                self.engage_with_video(video_url)
                random_delay()

                if self.likes_given >= max_likes:
                    break

                # Rotate proxy periodically
                if (i + 1) % 8 == 0:
                    logger.info("Rotating proxy for engagement...")
                    self.end_session()
                    random_delay(5, 15)
                    self.start_session()
                    if not self.navigate_to_profile():
                        break
                    video_links = self.get_video_links()

            logger.info(
                f"Engagement session complete. Total likes: {self.likes_given}"
            )

        except Exception as e:
            logger.error(f"Engagement bot error: {e}")
        finally:
            self.end_session()
