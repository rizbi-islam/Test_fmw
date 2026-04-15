"""
Test Case Data Model.
Immutable dataclass — represents one test case from any source.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class TestStep:
    """A single executable step in a test case."""
    step_no: int
    keyword: str
    locator: str = ""
    strategy: str = "css"
    value: str = ""
    timeout: int = 10
    enabled: bool = True
    data_source: str = ""
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "step_no": self.step_no,
            "keyword": self.keyword.upper(),
            "locator": self.locator,
            "strategy": self.strategy,
            "value": self.value,
            "timeout": self.timeout,
            "enabled": self.enabled,
            "data_source": self.data_source,
            "description": self.description,
        }


@dataclass
class TestCase:
    """Represents one test case from any source (Excel, YAML, UI builder)."""
    test_id: str
    name: str
    enabled: bool = True
    steps: List[dict] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    data_source: str = "excel"
    description: str = ""
    priority: str = "medium"
    source_file: str = ""

    def add_step(self, step: TestStep) -> None:
        self.steps.append(step.to_dict())

    @property
    def step_count(self) -> int:
        return len(self.steps)

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "name": self.name,
            "enabled": self.enabled,
            "tags": self.tags,
            "data_source": self.data_source,
            "description": self.description,
            "priority": self.priority,
            "step_count": self.step_count,
            "steps": self.steps,
        }


@dataclass
class TestSuite:
    """A collection of test cases."""
    suite_id: str
    name: str
    test_cases: List[TestCase] = field(default_factory=list)
    description: str = ""

    def add_test_case(self, test_case: TestCase) -> None:
        self.test_cases.append(test_case)

    @property
    def enabled_tests(self) -> List[TestCase]:
        return [tc for tc in self.test_cases if tc.enabled]

    @property
    def total(self) -> int:
        return len(self.test_cases)

    @property
    def enabled_count(self) -> int:
        return len(self.enabled_tests)
