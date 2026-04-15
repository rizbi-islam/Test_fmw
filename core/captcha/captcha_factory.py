"""
CAPTCHA Factory — returns correct handler by config key.
Usage:
    handler = CaptchaFactory.get("bypass", config)
    handler.solve(driver, context)
"""
from loguru import logger
from core.captcha.base_captcha import BaseCaptchaHandler


class CaptchaFactory:
    _registry: dict = {}

    @classmethod
    def register(cls, name: str, handler_class) -> None:
        cls._registry[name.lower()] = handler_class

    @classmethod
    def get(cls, captcha_type: str, config: dict) -> BaseCaptchaHandler:
        captcha_type = captcha_type.lower()
        if not cls._registry:
            cls._register_builtins()
        handler_class = cls._registry.get(captcha_type)
        if not handler_class:
            available = list(cls._registry.keys())
            raise ValueError(
                f"[CaptchaFactory] Unknown type: '{captcha_type}'. Available: {available}"
            )
        logger.info(f"[CaptchaFactory] Creating handler: '{captcha_type}'")
        return handler_class(config)

    @classmethod
    def _register_builtins(cls) -> None:
        from core.captcha.bypass_captcha import BypassCaptchaHandler
        from core.captcha.twocaptcha_solver import TwoCaptchaSolver
        from core.captcha.manual_pause_captcha import ManualPauseCaptchaHandler
        cls.register("bypass",     BypassCaptchaHandler)
        cls.register("twocaptcha", TwoCaptchaSolver)
        cls.register("manual",     ManualPauseCaptchaHandler)

    @classmethod
    def available(cls) -> list:
        if not cls._registry:
            cls._register_builtins()
        return list(cls._registry.keys())
