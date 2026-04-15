"""
Bypass CAPTCHA Handler.
Sets cookies/flags that mark the session as trusted, bypassing CAPTCHA.
Works only when the test environment is configured to accept bypass flags.

Config:
    captcha:
      bypass:
        cookie_name: "bypass_captcha"
        cookie_value: "true"
        local_storage_key: ""        # optional JS localStorage key
        local_storage_value: ""
"""
from loguru import logger
from core.captcha.base_captcha import BaseCaptchaHandler


class BypassCaptchaHandler(BaseCaptchaHandler):
    """
    Bypasses CAPTCHA by injecting cookies or localStorage flags.
    Use in test environments where the app checks for a bypass token.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.cookie_name         = config.get("cookie_name", "bypass_captcha")
        self.cookie_value        = config.get("cookie_value", "true")
        self.local_storage_key   = config.get("local_storage_key", "")
        self.local_storage_value = config.get("local_storage_value", "")

    def solve(self, driver, context) -> bool:
        try:
            if self.cookie_name:
                driver.execute_script(
                    f"document.cookie = '{self.cookie_name}={self.cookie_value}; path=/';"
                )
                logger.info(f"[BypassCaptcha] Set cookie: {self.cookie_name}={self.cookie_value}")

            if self.local_storage_key:
                driver.execute_script(
                    f"localStorage.setItem('{self.local_storage_key}', "
                    f"'{self.local_storage_value}');"
                )
                logger.info(
                    f"[BypassCaptcha] Set localStorage: "
                    f"{self.local_storage_key}={self.local_storage_value}"
                )

            # Reload page to apply bypass
            driver.refresh()
            logger.success("[BypassCaptcha] Bypass applied and page refreshed.")
            return True

        except Exception as e:
            logger.error(f"[BypassCaptcha] Failed: {e}")
            return False
