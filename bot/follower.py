"""
Follower Bot Module.
Automatically follows the target TikTok account from US-based accounts.
"""

import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

from browser import create_driver, close_driver
from config import Config
from utils import setup_logger, random_delay, get_random_proxy

logger = setup_logger(__name__)


class FollowerBot:
    """Bot for generating followers from US-based IPs."""

    def __init__(self):
        self.driver = None
        self.follows_given = 0
        self.session_active = False

    def start_session(self):
        """Start a new follower session."""
        proxy = get_random_proxy()
        self.driver = create_driver(proxy=proxy)
        self.session_active = True
        logger.info("Follower bot session started")

    def end_session(self):
        """End the current session and clean up."""
        self.session_active = False
        close_driver(self.driver)
        self.driver = None
        logger.info(
            f"Follower session ended. Follows given: {self.follows_given}"
        )

    def navigate_to_profile(self):
        """Navigate to the target TikTok profile."""
        try:
            self.driver.get(Config.PROFILE_URL)
            random_delay(3, 6)

            # Wait for the follow button to appear
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[data-e2e="follow-button"]')
                )
            )
            logger.info(f"Navigated to @{Config.TARGET_USERNAME} profile")
            return True

        except TimeoutException:
            logger.warning("Profile page timed out")
            return False
        except Exception as e:
            logger.error(f"Error navigating to profile: {e}")
            return False

    def follow_account(self):
        """
        Click the follow button on the target profile.

        Returns:
            True if follow was successful
        """
        try:
            follow_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[data-e2e="follow-button"]')
                )
            )

            # Check if already following
            button_text = follow_button.text.lower()
            if "following" in button_text:
                logger.info("Already following this account")
                return False

            # Human-like click
            actions = ActionChains(self.driver)
            actions.move_to_element(follow_button).pause(
                random.uniform(0.5, 1.5)
            ).click().perform()

            self.follows_given += 1
            logger.info(
                f"Follow #{self.follows_given} - Followed @{Config.TARGET_USERNAME}"
            )
            random_delay(2, 5)
            return True

        except TimeoutException:
            logger.warning("Follow button not found or not clickable")
            return False
        except Exception as e:
            logger.error(f"Error following account: {e}")
            return False

    def follow_from_suggested(self):
        """
        Also follow from the 'suggested accounts' to appear natural.
        This helps the follow appear organic.
        """
        try:
            # Scroll down to find suggested accounts
            self.driver.execute_script("window.scrollBy(0, 500)")
            random_delay(2, 4)

            suggested_follows = self.driver.find_elements(
                By.CSS_SELECTOR, '[data-e2e="suggest-follow-button"]'
            )

            if suggested_follows:
                # Follow 1-2 suggested accounts to appear natural
                count = min(random.randint(1, 2), len(suggested_follows))
                for btn in random.sample(suggested_follows, count):
                    try:
                        actions = ActionChains(self.driver)
                        actions.move_to_element(btn).pause(
                            random.uniform(0.3, 1.0)
                        ).click().perform()
                        random_delay(1, 3)
                    except Exception:
                        pass

        except Exception as e:
            logger.debug(f"Suggested follow interaction failed: {e}")

    def run(self, max_follows: int = None):
        """
        Run the follower bot session.

        Args:
            max_follows: Maximum follows to generate (default from config)
        """
        max_follows = max_follows or Config.MAX_FOLLOWS_PER_SESSION
        self.follows_given = 0

        logger.info(f"Starting follower session (target: {max_follows} follows)")

        for i in range(max_follows):
            self.start_session()

            try:
                if not self.navigate_to_profile():
                    logger.warning("Could not access profile, retrying...")
                    self.end_session()
                    random_delay(10, 20)
                    continue

                # Follow the target account
                success = self.follow_account()

                if success:
                    # Occasionally interact with suggested accounts
                    if random.random() < 0.3:
                        self.follow_from_suggested()

                random_delay(3, 8)

            except Exception as e:
                logger.error(f"Follower bot error: {e}")
            finally:
                self.end_session()

            # Longer delay between follows to avoid detection
            random_delay(15, 30)

        logger.info(
            f"Follower session complete. Total follows: {self.follows_given}"
        )
