"""
OTP Factory — returns the correct OTP handler by config key.
Usage:
    handler = OTPFactory.get("firebase", config)
    otp     = handler.get_otp(timeout=30)
"""
from loguru import logger
from core.otp.base_otp import BaseOTPHandler


class OTPFactory:
    _registry: dict = {}

    @classmethod
    def register(cls, name: str, handler_class) -> None:
        cls._registry[name.lower()] = handler_class
        logger.debug(f"[OTPFactory] Registered: '{name}'")

    @classmethod
    def get(cls, otp_type: str, config: dict) -> BaseOTPHandler:
        otp_type = otp_type.lower()
        if not cls._registry:
            cls._register_builtins()
        handler_class = cls._registry.get(otp_type)
        if not handler_class:
            available = list(cls._registry.keys())
            raise ValueError(
                f"[OTPFactory] Unknown OTP type: '{otp_type}'. Available: {available}"
            )
        logger.info(f"[OTPFactory] Creating handler: '{otp_type}'")
        return handler_class(config)

    @classmethod
    def _register_builtins(cls) -> None:
        from core.otp.mock_otp import MockOTPHandler
        from core.otp.firebase_otp import FirebaseOTPHandler
        from core.otp.gmail_imap_otp import GmailIMAPOTPHandler
        cls.register("mock",     MockOTPHandler)
        cls.register("firebase", FirebaseOTPHandler)
        cls.register("gmail",    GmailIMAPOTPHandler)

    @classmethod
    def available(cls) -> list:
        if not cls._registry:
            cls._register_builtins()
        return list(cls._registry.keys())
