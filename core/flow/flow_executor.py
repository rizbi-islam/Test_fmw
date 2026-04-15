"""
Flow Executor — orchestrates full test suite execution.
Manages driver lifecycle, context, and reporting per test case.
"""
from typing import List
from loguru import logger

from core.drivers.driver_factory import DriverFactory
from core.keywords.keyword_executor import KeywordExecutor, TestCaseResult
from core.flow.flow_context import FlowContext
from core.test_cases.test_case_model import TestCase


class SuiteResult:
    """Aggregate result of a full test suite run."""

    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.results: List[TestCaseResult] = []

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == "PASS")

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == "FAIL")

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == "SKIP")

    def to_dict(self) -> dict:
        return {
            "suite_name": self.suite_name,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "results": [r.to_dict() for r in self.results],
        }


class FlowExecutor:
    """
    Executes a list of test cases sequentially.
    Phase 4 wraps this with pytest-xdist for parallel execution.

    Usage:
        executor = FlowExecutor(config)
        result   = executor.run(test_cases)
    """

    def __init__(self, config: dict):
        self.config = config
        self.driver_config = config.get("driver", {})
        self.execution_config = config.get("execution", {})
        # Pass screenshot_dir and screenshot_on_failure into execution config
        fw_config = config.get("framework", {})
        self.execution_config["screenshot_on_failure"] = fw_config.get("screenshot_on_failure", True)
        self.execution_config["screenshot_dir"] = fw_config.get("screenshot_dir", "assets/screenshots")

    def run(self, test_cases: List[TestCase], suite_name: str = "Suite") -> SuiteResult:
        suite_result = SuiteResult(suite_name)
        enabled = [tc for tc in test_cases if tc.enabled]

        logger.info(f"\n{'#'*60}")
        logger.info(f"  Suite  : {suite_name}")
        logger.info(f"  Total  : {len(test_cases)} | Enabled: {len(enabled)}")
        logger.info(f"  Driver : {self.driver_config.get('default','selenium')}")
        logger.info(f"{'#'*60}\n")

        for tc in enabled:
            result = self._run_single(tc)
            suite_result.results.append(result)

        self._print_summary(suite_result)
        return suite_result

    def _run_single(self, test_case: TestCase) -> TestCaseResult:
        driver_type = self.driver_config.get("default", "selenium")
        driver = DriverFactory.get(driver_type, self.driver_config)
        context = FlowContext(config={
            **self.config.get("environment", {}),
            **self.execution_config,
        })

        try:
            driver.start()
            executor = KeywordExecutor(driver, context, self.execution_config)
            result = executor.run(test_case)
        except Exception as e:
            logger.exception(f"[FlowExecutor] Fatal error in {test_case.test_id}: {e}")
            result = TestCaseResult(test_case.test_id, test_case.name)
            result.status = "ERROR"
            result.error_message = str(e)
            from datetime import datetime
            result.finished_at = datetime.now()
        finally:
            try:
                driver.quit()
            except Exception:
                pass

        return result

    def _print_summary(self, r: SuiteResult) -> None:
        logger.info(f"\n{'#'*60}")
        logger.info(f"  SUITE RESULT : {r.suite_name}")
        logger.info(f"  Passed  : {r.passed}")
        logger.info(f"  Failed  : {r.failed}")
        logger.info(f"  Skipped : {r.skipped}")
        logger.info(f"  Total   : {r.total}")
        logger.info(f"{'#'*60}\n")
