"""
HANDLE_OTP Keyword.
Retrieves OTP via configured handler and types it into a field.

Excel usage:
  Keyword      | Locator        | Strategy | Value    | Timeout
  HANDLE_OTP   | #otp_input     | css      | firebase | 30

Parameters:
  locator    : element to type OTP into
  strategy   : locator strategy (default: css)
  value      : OTP handler type — firebase | gmail | mock (default: mock)
  timeout    : seconds to wait for OTP (default: 30)
"""
from loguru import logger
from core.keywords.base_keyword import BaseKeyword, KeywordResult


class HandleOTPKeyword(BaseKeyword):
    keyword_name    = "HANDLE_OTP"
    description     = "Get OTP from configured source and type into field"
    required_params = ["locator"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        locator     = params["locator"]
        strategy    = params.get("strategy", "css")
        otp_type    = params.get("value", "mock").lower()
        timeout     = int(params.get("timeout", 30))

        try:
            from core.otp.otp_factory import OTPFactory

            # Load OTP config from context (set from config.yaml via FlowContext)
            otp_config = context.get("otp_config", {}).get(otp_type, {})

            handler = OTPFactory.get(otp_type, otp_config)
            logger.info(f"[HANDLE_OTP] Getting OTP via '{otp_type}' (timeout={timeout}s)")

            otp_code = handler.get_otp(timeout=timeout)

            # Store in context for later use
            context.set("last_otp", otp_code)

            # Type into field
            driver.type_text(locator, otp_code, strategy)
            logger.success(f"[HANDLE_OTP] OTP typed into [{strategy}] {locator}")

            handler.clear()
            return self._pass(f"OTP '{otp_code}' typed into [{strategy}] {locator}", output=otp_code)

        except TimeoutError as e:
            return self._fail(f"OTP timeout: {e}")
        except Exception as e:
            return self._fail(f"OTP handling failed: {e}")
