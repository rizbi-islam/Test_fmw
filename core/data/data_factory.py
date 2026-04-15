"""
Data Factory — returns the correct data provider by config key.
Phase 1: Excel only.
Phase 2: Excel + SQLite + MySQL + JSON (all registered here).

Usage:
    provider = DataFactory.get("sqlite", {"db_path": "data/test.db"})
    provider.connect()
"""
from loguru import logger
from core.data.base_provider import BaseDataProvider


class DataFactory:
    _registry: dict = {}

    @classmethod
    def register(cls, name: str, provider_class) -> None:
        cls._registry[name.lower()] = provider_class

    @classmethod
    def get(cls, provider_type: str, config: dict) -> BaseDataProvider:
        provider_type = provider_type.lower()
        if not cls._registry:
            cls._register_builtins()
        provider_class = cls._registry.get(provider_type)
        if not provider_class:
            available = list(cls._registry.keys())
            raise ValueError(
                f"[DataFactory] Unknown provider: '{provider_type}'. Available: {available}"
            )
        logger.info(f"[DataFactory] Creating provider: '{provider_type}'")
        return provider_class(**config)

    @classmethod
    def _register_builtins(cls) -> None:
        from core.data.excel_provider import ExcelProvider
        from core.data.sqlite_provider import SQLiteProvider
        from core.data.mysql_provider import MySQLProvider
        from core.data.json_provider import JsonProvider
        cls.register("excel",  ExcelProvider)
        cls.register("sqlite", SQLiteProvider)
        cls.register("mysql",  MySQLProvider)
        cls.register("json",   JsonProvider)

    @classmethod
    def available_providers(cls) -> list:
        if not cls._registry:
            cls._register_builtins()
        return list(cls._registry.keys())
