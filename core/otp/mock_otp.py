"""
Mock OTP Handler.
Returns a static OTP for test/dev environments.
No external service needed — use this for local testing.

Config:
    otp_value: "123456"   # the static OTP to return
"""
from loguru import logger
from core.otp.base_otp import BaseOTPHandler


class MockOTPHandler(BaseOTPHandler):
    """Returns a preconfigured static OTP. Perfect for CI/CD and dev environments."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.otp_value = str(config.get("otp_value", "123456"))

    def get_otp(self, timeout: int = 30) -> str:
        logger.info(f"[MockOTP] Returning static OTP: {self.otp_value}")
        return self.otp_value

    def clear(self) -> None:
        logger.debug("[MockOTP] Clear called (no-op for mock).")
