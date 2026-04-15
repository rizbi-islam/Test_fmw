from core.keywords.base_keyword import BaseKeyword, KeywordResult


class WaitKeyword(BaseKeyword):
    keyword_name = "WAIT_FOR"
    description = "Wait until an element is visible"
    required_params = ["locator"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        locator = params["locator"]
        strategy = params.get("strategy", "css")
        timeout = int(params.get("timeout", 10))
        try:
            driver.wait_for_element(locator, timeout, strategy)
            return self._pass(f"Element visible: [{strategy}] {locator}")
        except Exception as e:
            return self._fail(f"Wait timeout ({timeout}s) for [{strategy}] {locator}: {e}")
