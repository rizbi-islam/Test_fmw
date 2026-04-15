"""
Abstract Base Keyword — every keyword MUST inherit this.
Adding a new keyword = create new file + inherit BaseKeyword.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from loguru import logger


@dataclass
class KeywordResult:
    """Structured result returned by every keyword execution."""
    keyword: str
    status: str              # PASS | FAIL | SKIP
    message: str = ""
    screenshot_path: str = ""
    elapsed_ms: float = 0.0
    output: Any = None


class BaseKeyword(ABC):
    """
    Contract for all keyword implementations.
    Each keyword receives driver, context, params and returns KeywordResult.
    """

    keyword_name: str = ""
    description: str = ""
    required_params: list = field(default_factory=list)

    @abstractmethod
    def execute(self, driver, context, params: dict) -> KeywordResult:
        """Execute the keyword action."""

    def validate_params(self, params: dict) -> None:
        for key in self.required_params:
            if key not in params or params[key] in (None, ""):
                raise ValueError(
                    f"[{self.keyword_name}] Missing required param: '{key}'. "
                    f"Provided: {list(params.keys())}"
                )

    def _pass(self, message: str = "Step passed", output: Any = None) -> KeywordResult:
        return KeywordResult(keyword=self.keyword_name, status="PASS",
                             message=message, output=output)

    def _fail(self, message: str, screenshot_path: str = "") -> KeywordResult:
        logger.error(f"[{self.keyword_name}] FAIL - {message}")
        return KeywordResult(keyword=self.keyword_name, status="FAIL",
                             message=message, screenshot_path=screenshot_path)

    def _skip(self, message: str = "Step skipped") -> KeywordResult:
        return KeywordResult(keyword=self.keyword_name, status="SKIP", message=message)
