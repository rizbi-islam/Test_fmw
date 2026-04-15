"""
Keyword Executor — runs a sequence of steps from a test case.
This is the heart of the keyword-driven engine.
"""
import time
import os
from datetime import datetime
from typing import List
from loguru import logger

from core.keywords.keyword_registry import KeywordRegistry
from core.keywords.base_keyword import KeywordResult


class StepResult:
    def __init__(self, step_no: int, keyword: str, status: str,
                 message: str, screenshot: str = "", elapsed_ms: float = 0):
        self.step_no = step_no
        self.keyword = keyword
        self.status = status
        self.message = message
        self.screenshot = screenshot
        self.elapsed_ms = elapsed_ms

    def to_dict(self) -> dict:
        return {
            "step_no": self.step_no,
            "keyword": self.keyword,
            "status": self.status,
            "message": self.message,
            "screenshot": self.screenshot,
            "elapsed_ms": round(self.elapsed_ms, 2),
        }


class TestCaseResult:
    def __init__(self, test_id: str, test_name: str):
        self.test_id = test_id
        self.test_name = test_name
        self.status = "PASS"
        self.step_results: List[StepResult] = []
        self.started_at = datetime.now()
        self.finished_at = None
        self.error_message = ""

    @property
    def elapsed_seconds(self) -> float:
        if self.finished_at:
            return round((self.finished_at - self.started_at).total_seconds(), 2)
        return 0.0

    @property
    def total_steps(self) -> int:
        return len(self.step_results)

    @property
    def passed_steps(self) -> int:
        return sum(1 for s in self.step_results if s.status == "PASS")

    @property
    def failed_steps(self) -> int:
        return sum(1 for s in self.step_results if s.status == "FAIL")

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "status": self.status,
            "total_steps": self.total_steps,
            "passed_steps": self.passed_steps,
            "failed_steps": self.failed_steps,
            "elapsed_seconds": self.elapsed_seconds,
            "started_at": str(self.started_at),
            "steps": [s.to_dict() for s in self.step_results],
        }


class KeywordExecutor:
    """
    Executes a test case step-by-step using the keyword engine.
    Usage:
        executor = KeywordExecutor(driver, context, config)
        result   = executor.run(test_case)
    """

    def __init__(self, driver, context, config: dict):
        self.driver = driver
        self.context = context
        self.config = config
        self.registry = KeywordRegistry()
        self.screenshot_on_failure = config.get("screenshot_on_failure", True)
        self.screenshot_dir = config.get("screenshot_dir", "assets/screenshots")
        self.retry_on_failure = config.get("retry_on_failure", 1)

    def run(self, test_case) -> TestCaseResult:
        result = TestCaseResult(test_case.test_id, test_case.name)
        logger.info(f"\n{'='*60}")
        logger.info(f"  Running: {test_case.test_id} - {test_case.name}")
        logger.info(f"{'='*60}")

        for step in test_case.steps:
            if not step.get("enabled", True):
                result.step_results.append(StepResult(
                    step_no=step.get("step_no", 0),
                    keyword=step.get("keyword", ""),
                    status="SKIP",
                    message="Step disabled"
                ))
                continue

            step_result = self._execute_step(step)
            result.step_results.append(step_result)

            if step_result.status == "FAIL":
                result.status = "FAIL"
                result.error_message = step_result.message
                if self.config.get("stop_on_first_failure", False):
                    logger.warning("[KeywordExecutor] Stopping on first failure.")
                    break

        result.finished_at = datetime.now()

        if result.status == "PASS":
            logger.success(f"  PASSED: {test_case.test_id} ({result.elapsed_seconds}s)")
        else:
            logger.error(f"  FAILED: {test_case.test_id} ({result.elapsed_seconds}s)")

        return result

    def _execute_step(self, step: dict) -> StepResult:
        step_no = step.get("step_no", 0)
        keyword_name = step.get("keyword", "").upper()
        params = {k: v for k, v in step.items()
                  if k not in ("step_no", "keyword", "enabled")}

        logger.debug(f"  Step {step_no:02d} | {keyword_name} | params={params}")

        attempts = 0
        max_attempts = self.retry_on_failure + 1

        while attempts < max_attempts:
            attempts += 1
            start = time.time()
            try:
                keyword = self.registry.get(keyword_name)
                kw_result = keyword.execute(self.driver, self.context, params)
                elapsed = (time.time() - start) * 1000
                kw_result.elapsed_ms = elapsed

                if kw_result.status == "FAIL" and self.screenshot_on_failure:
                    kw_result.screenshot_path = self._capture_failure_screenshot(keyword_name, step_no)

                if kw_result.status == "FAIL" and attempts < max_attempts:
                    logger.warning(f"  Step {step_no} failed — retry {attempts}/{max_attempts - 1}")
                    continue

                icon = {"PASS": "OK", "FAIL": "FAIL", "SKIP": "SKIP"}.get(kw_result.status, "?")
                logger.info(f"  [{icon}] Step {step_no:02d} [{keyword_name}] - {kw_result.message}")

                return StepResult(
                    step_no=step_no,
                    keyword=keyword_name,
                    status=kw_result.status,
                    message=kw_result.message,
                    screenshot=kw_result.screenshot_path,
                    elapsed_ms=elapsed,
                )

            except Exception as e:
                elapsed = (time.time() - start) * 1000
                error_msg = f"Unexpected error in step {step_no} [{keyword_name}]: {e}"
                logger.exception(error_msg)
                if attempts >= max_attempts:
                    screenshot = self._capture_failure_screenshot(keyword_name, step_no)
                    return StepResult(
                        step_no=step_no, keyword=keyword_name,
                        status="FAIL", message=error_msg,
                        screenshot=screenshot, elapsed_ms=elapsed,
                    )

    def _capture_failure_screenshot(self, keyword_name: str, step_no: int) -> str:
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"FAIL_{step_no:02d}_{keyword_name}_{ts}.png"
            path = os.path.join(self.screenshot_dir, filename)
            os.makedirs(self.screenshot_dir, exist_ok=True)
            self.driver.screenshot(path)
            return path
        except Exception as e:
            logger.warning(f"[KeywordExecutor] Could not capture failure screenshot: {e}")
            return ""
