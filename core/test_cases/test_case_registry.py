"""
Test Case Registry — merges test cases from all sources.
Phase 1: Excel only. Phase 3 adds UI builder + YAML.
"""
from typing import List, Optional
from loguru import logger

from core.test_cases.test_case_model import TestCase, TestSuite


class TestCaseRegistry:
    """
    Central registry that holds all test cases regardless of source.
    Supports filtering by tag, ID, enabled status.
    Singleton pattern.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._suites = []
            cls._instance._all_cases = []
        return cls._instance

    def register_suite(self, suite: TestSuite) -> None:
        self._suites.append(suite)
        self._all_cases.extend(suite.test_cases)
        logger.info(
            f"[TestCaseRegistry] Registered suite '{suite.name}' "
            f"with {suite.total} test cases."
        )

    def get_all(self) -> List[TestCase]:
        return list(self._all_cases)

    def get_enabled(self) -> List[TestCase]:
        return [tc for tc in self._all_cases if tc.enabled]

    def get_by_id(self, test_id: str) -> Optional[TestCase]:
        for tc in self._all_cases:
            if tc.test_id == test_id:
                return tc
        return None

    def get_by_tag(self, tag: str) -> List[TestCase]:
        return [tc for tc in self._all_cases if tag.lower() in [t.lower() for t in tc.tags]]

    def enable(self, test_id: str) -> None:
        tc = self.get_by_id(test_id)
        if tc:
            tc.enabled = True

    def disable(self, test_id: str) -> None:
        tc = self.get_by_id(test_id)
        if tc:
            tc.enabled = False

    def clear(self) -> None:
        self._suites.clear()
        self._all_cases.clear()

    @property
    def total(self) -> int:
        return len(self._all_cases)

    @property
    def enabled_count(self) -> int:
        return len(self.get_enabled())
