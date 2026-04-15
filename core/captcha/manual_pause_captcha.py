"""
Manual Pause CAPTCHA Handler.
Pauses test execution and waits for a human to solve the CAPTCHA.
Useful for development, debugging, or one-off manual runs.

Config:
    captcha:
      manual:
        pause_message: "Please solve the CAPTCHA then press ENTER"
        timeout: 300    # 5 minutes max wait
"""
import time
import threading
from loguru import logger
from core.captcha.base_captcha import BaseCaptchaHandler


class ManualPauseCaptchaHandler(BaseCaptchaHandler):
    """
    Pauses execution and waits for human to solve CAPTCHA.
    Shows a message in the terminal and waits for ENTER key press.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.pause_message = config.get(
            "pause_message",
            "CAPTCHA detected — please solve it manually in the browser, then press ENTER..."
        )
        self.timeout = int(config.get("timeout", 300))

    def solve(self, driver, context) -> bool:
        logger.warning(f"\n{'='*60}")
        logger.warning(f"  [ManualPauseCaptcha] CAPTCHA DETECTED")
        logger.warning(f"  {self.pause_message}")
        logger.warning(f"  Timeout: {self.timeout}s")
        logger.warning(f"{'='*60}\n")

        # Take screenshot to show current state
        try:
            screenshot_path = "assets/screenshots/captcha_pause.png"
            driver.screenshot(screenshot_path)
            logger.info(f"[ManualPauseCaptcha] Screenshot saved: {screenshot_path}")
        except Exception:
            pass

        # Wait for user input with timeout
        result = self._wait_for_input(self.timeout)

        if result:
            logger.success("[ManualPauseCaptcha] User confirmed CAPTCHA solved. Resuming.")
            return True
        else:
            logger.error(f"[ManualPauseCaptcha] Timed out after {self.timeout}s.")
            return False

    def _wait_for_input(self, timeout: int) -> bool:
        """Wait for ENTER key press with timeout."""
        answered = threading.Event()
        result = [False]

        def input_thread():
            try:
                input("\n  >>> Press ENTER after solving CAPTCHA: ")
                result[0] = True
            except Exception:
                pass
            finally:
                answered.set()

        t = threading.Thread(target=input_thread, daemon=True)
        t.start()
        answered.wait(timeout=timeout)
        return result[0]
