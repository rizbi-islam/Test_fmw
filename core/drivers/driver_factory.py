"""
Driver Factory — returns the correct driver based on config key.
This is the ONLY place in the framework that knows which driver to create.
"""
from loguru import logger
from core.drivers.base_driver import BaseDriver


class DriverFactory:
    """
    Factory that creates and returns driver instances.
    Usage:
        driver = DriverFactory.get("selenium", config)
        driver.start()
    """

    _registry: dict = {}

    @classmethod
    def register(cls, name: str, driver_class) -> None:
        cls._registry[name.lower()] = driver_class
        logger.debug(f"[DriverFactory] Registered driver: '{name}'")

    @classmethod
    def get(cls, driver_type: str, config: dict) -> BaseDriver:
        driver_type = driver_type.lower()
        if not cls._registry:
            cls._register_builtins()
        driver_class = cls._registry.get(driver_type)
        if not driver_class:
            available = list(cls._registry.keys())
            raise ValueError(
                f"[DriverFactory] Unknown driver: '{driver_type}'. Available: {available}"
            )
        logger.info(f"[DriverFactory] Creating driver: '{driver_type}'")
        return driver_class(config)

    @classmethod
    def _register_builtins(cls) -> None:
        from core.drivers.selenium_driver import SeleniumDriver
        from core.drivers.playwright_driver import PlaywrightDriver
        cls.register("selenium", SeleniumDriver)
        cls.register("playwright", PlaywrightDriver)

    @classmethod
    def available_drivers(cls) -> list:
        if not cls._registry:
            cls._register_builtins()
        return list(cls._registry.keys())
