import time
from core.keywords.base_keyword import BaseKeyword, KeywordResult


class SleepKeyword(BaseKeyword):
    keyword_name = "SLEEP"
    description = "Pause execution for N seconds (use sparingly)"
    required_params = ["value"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        seconds = float(params["value"])
        time.sleep(seconds)
        return self._pass(f"Slept for {seconds}s")
