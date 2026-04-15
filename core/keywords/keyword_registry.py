"""
Keyword Registry — auto-discovers and registers all keywords.
Adding a new keyword file = it auto-registers. Zero config change needed.
"""
import importlib
import pkgutil
import inspect
from loguru import logger

from core.keywords.base_keyword import BaseKeyword


class KeywordRegistry:
    """
    Central registry of all available keywords.
    Auto-scans core/keywords/actions/ on initialization.
    Singleton pattern — one registry per process.
    """

    _instance = None
    _keywords: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._keywords = {}
            cls._instance._auto_discover()
        return cls._instance

    def _auto_discover(self) -> None:
        import core.keywords.actions as actions_pkg
        package_path = actions_pkg.__path__

        for finder, module_name, is_pkg in pkgutil.walk_packages(package_path):
            full_module = f"core.keywords.actions.{module_name}"
            try:
                module = importlib.import_module(full_module)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, BaseKeyword)
                        and obj is not BaseKeyword
                        and obj.keyword_name
                    ):
                        self.register(obj.keyword_name, obj)
            except Exception as e:
                logger.warning(f"[KeywordRegistry] Could not load {full_module}: {e}")

        logger.info(
            f"[KeywordRegistry] Registered {len(self._keywords)} keywords: "
            f"{sorted(self._keywords.keys())}"
        )

    def register(self, name: str, keyword_class) -> None:
        self._keywords[name.upper()] = keyword_class
        logger.debug(f"[KeywordRegistry] Registered: '{name.upper()}'")

    def get(self, name: str) -> BaseKeyword:
        keyword_class = self._keywords.get(name.upper())
        if not keyword_class:
            available = sorted(self._keywords.keys())
            raise ValueError(
                f"[KeywordRegistry] Unknown keyword: '{name}'. "
                f"Available: {available}"
            )
        return keyword_class()

    def all_keywords(self) -> dict:
        return dict(self._keywords)

    def has_keyword(self, name: str) -> bool:
        return name.upper() in self._keywords
