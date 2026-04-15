"""Abstract Base CAPTCHA Handler."""
from abc import ABC, abstractmethod


class BaseCaptchaHandler(ABC):

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def solve(self, driver, context) -> bool:
        """
        Attempt to solve/bypass CAPTCHA on the current page.
        Args:
            driver:  active BaseDriver instance
            context: FlowContext
        Returns:
            True if CAPTCHA resolved, False if failed
        """
