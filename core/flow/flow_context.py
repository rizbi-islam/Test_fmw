"""
Flow Context — shared state container across all steps in a test run.
Passed to every keyword during execution.
Variables set in one step are available in later steps.
"""
import re
from typing import Any, List
from loguru import logger


class FlowContext:
    """
    Test session state container.
    - Stores variables set by keywords (GET_TEXT, OTP, etc.)
    - Resolves {variable} placeholders in values
    - Tracks screenshots and metadata
    """

    def __init__(self, config: dict = None):
        self._store: dict = {}
        self._screenshots: List[str] = []
        self._config = config or {}
        self._inject_config()

    def _inject_config(self) -> None:
        self._store["base_url"] = self._config.get("base_url", "")
        self._store["screenshot_dir"] = self._config.get(
            "screenshot_dir", "assets/screenshots"
        )
        self._store["environment"] = self._config.get("environment", "local")

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value
        logger.debug(f"[FlowContext] Set '{key}' = '{value}'")

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def resolve(self, value: str) -> str:
        """
        Resolve {variable} placeholders in a string.
        Example: "{base_url}/login?user={username}" -> "https://example.com/login?user=john"
        """
        if not isinstance(value, str):
            return str(value) if value is not None else ""

        def replacer(match):
            var_name = match.group(1)
            resolved = self._store.get(var_name)
            if resolved is None:
                logger.warning(f"[FlowContext] Unresolved variable: '{{{var_name}}}'")
                return match.group(0)
            return str(resolved)

        return re.sub(r"\{(\w+)\}", replacer, value)

    def add_screenshot(self, path: str) -> None:
        self._screenshots.append(path)

    @property
    def screenshots(self) -> List[str]:
        return list(self._screenshots)

    def dump(self) -> dict:
        return dict(self._store)

    def reset(self) -> None:
        """Reset context between test cases (preserve config vars)."""
        self._screenshots.clear()
        self._store.clear()
        self._inject_config()
