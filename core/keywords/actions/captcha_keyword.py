"""
HANDLE_CAPTCHA Keyword.
Solves or bypasses CAPTCHA using configured strategy.

Excel usage:
  Keyword          | Locator | Strategy | Value      | Timeout
  HANDLE_CAPTCHA   |         | css      | bypass     |
  HANDLE_CAPTCHA   |         | css      | twocaptcha | 120
  HANDLE_CAPTCHA   |         | css      | manual     | 300

Parameters:
  value   : captcha strategy — bypass | twocaptcha | manual (default: bypass)
  timeout : max seconds to wait (for manual mode)
"""
from loguru import logger
from core.keywords.base_keyword import BaseKeyword, KeywordResult


class HandleCaptchaKeyword(BaseKeyword):
    keyword_name = "HANDLE_CAPTCHA"
    description  = "Solve or bypass CAPTCHA using configured strategy"

    def execute(self, driver, context, params: dict) -> KeywordResult:
        captcha_type = params.get("value", "bypass").lower()

        try:
            from core.captcha.captcha_factory import CaptchaFactory

            captcha_config = context.get("captcha_config", {}).get(captcha_type, {})
            handler = CaptchaFactory.get(captcha_type, captcha_config)

            logger.info(f"[HANDLE_CAPTCHA] Using strategy: '{captcha_type}'")
            success = handler.solve(driver, context)

            if success:
                return self._pass(f"CAPTCHA handled via '{captcha_type}'")
            return self._fail(f"CAPTCHA solve failed via '{captcha_type}'")

        except Exception as e:
            return self._fail(f"CAPTCHA handling error: {e}")
