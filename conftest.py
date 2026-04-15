"""
Pytest configuration for KWAF.
Loads config, sets up logging, provides shared fixtures.
"""
import os
import pytest
import yaml
from loguru import logger


def load_config(config_path: str = "config/config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def kwaf_config():
    return load_config()


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    logger.remove()
    os.makedirs("logs", exist_ok=True)
    os.makedirs("assets/screenshots", exist_ok=True)
    os.makedirs("reports/output", exist_ok=True)
    logger.add(
        "logs/kwaf_{time}.log",
        rotation="10 MB",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )
    logger.add(
        lambda msg: print(msg, end=""),
        level="INFO",
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    )
