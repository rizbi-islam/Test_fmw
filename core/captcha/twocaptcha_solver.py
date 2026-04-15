"""
2Captcha CAPTCHA Solver.
Uses the 2captcha.com API to solve reCAPTCHA v2/v3, hCaptcha, image CAPTCHAs.
Cost: ~$2.99 per 1000 solves. Avg solve time: 15-30 seconds.

Setup:
  1. Register at https://2captcha.com
  2. Get your API key from dashboard
  3. Add to config.yaml:

     captcha:
       default: twocaptcha
       twocaptcha:
         api_key: "your_api_key_here"
         captcha_type: "recaptchav2"   # recaptchav2 | recaptchav3 | hcaptcha | image
         site_key: ""                  # auto-detected if empty
         timeout: 120

Supported types:
  recaptchav2 — standard "I'm not a robot" checkbox
  recaptchav3 — invisible reCAPTCHA (score-based)
  hcaptcha    — hCaptcha image challenges
  image       — simple text/image CAPTCHA
"""
import time
from loguru import logger
from core.captcha.base_captcha import BaseCaptchaHandler


class TwoCaptchaSolver(BaseCaptchaHandler):
    """Solves CAPTCHA via 2captcha.com API."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key      = config.get("api_key", "")
        self.captcha_type = config.get("captcha_type", "recaptchav2").lower()
        self.site_key     = config.get("site_key", "")
        self.timeout      = int(config.get("timeout", 120))

        if not self.api_key:
            raise ValueError("[TwoCaptcha] api_key is required in config.")

    def solve(self, driver, context) -> bool:
        try:
            from twocaptcha import TwoCaptcha
            solver = TwoCaptcha(self.api_key)

            current_url = driver.get_current_url()
            site_key    = self.site_key or self._detect_site_key(driver)

            logger.info(
                f"[TwoCaptcha] Solving {self.captcha_type} | "
                f"URL: {current_url} | SiteKey: {site_key[:20] if site_key else 'N/A'}..."
            )

            result = self._solve_by_type(solver, current_url, site_key)

            if result and result.get("code"):
                token = result["code"]
                self._inject_token(driver, token)
                logger.success(f"[TwoCaptcha] Solved. Token injected.")
                return True

            logger.error("[TwoCaptcha] No token returned from solver.")
            return False

        except Exception as e:
            logger.error(f"[TwoCaptcha] Solve failed: {e}")
            return False

    def _solve_by_type(self, solver, url: str, site_key: str) -> dict:
        """Dispatch to correct 2captcha solver method."""
        if self.captcha_type == "recaptchav2":
            return solver.recaptcha(sitekey=site_key, url=url)
        elif self.captcha_type == "recaptchav3":
            return solver.recaptcha(sitekey=site_key, url=url, version="v3")
        elif self.captcha_type == "hcaptcha":
            return solver.hcaptcha(sitekey=site_key, url=url)
        elif self.captcha_type == "image":
            # For image CAPTCHA: screenshot the element and send to API
            img_path = "assets/screenshots/captcha_img.png"
            driver.screenshot(img_path)
            return solver.normal(img_path)
        else:
            raise ValueError(f"[TwoCaptcha] Unknown captcha_type: {self.captcha_type}")

    def _detect_site_key(self, driver) -> str:
        """Try to auto-detect reCAPTCHA/hCaptcha site key from page source."""
        try:
            js_recaptcha = """
                var el = document.querySelector('.g-recaptcha, [data-sitekey]');
                return el ? el.getAttribute('data-sitekey') : '';
            """
            key = driver.execute_script(js_recaptcha)
            if key:
                logger.debug(f"[TwoCaptcha] Auto-detected site key: {key[:20]}...")
                return key
        except Exception:
            pass
        return ""

    def _inject_token(self, driver, token: str) -> None:
        """Inject solved CAPTCHA token into page and trigger callback."""
        try:
            # reCAPTCHA v2 standard injection
            driver.execute_script(
                f"document.getElementById('g-recaptcha-response').innerHTML = '{token}';"
            )
            # Trigger callback if defined
            driver.execute_script(
                f"""
                if (typeof ___grecaptcha_cfg !== 'undefined') {{
                    Object.keys(___grecaptcha_cfg.clients).forEach(function(key) {{
                        var client = ___grecaptcha_cfg.clients[key];
                        if (client && client.callback) {{
                            client.callback('{token}');
                        }}
                    }});
                }}
                """
            )
        except Exception as e:
            logger.warning(f"[TwoCaptcha] Token injection warning: {e}")
