from core.keywords.base_keyword import BaseKeyword, KeywordResult


class ClearKeyword(BaseKeyword):
    keyword_name = "CLEAR"
    description = "Clear an input field"
    required_params = ["locator"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        locator = params["locator"]
        strategy = params.get("strategy", "css")
        try:
            driver.clear(locator, strategy)
            return self._pass(f"Cleared: [{strategy}] {locator}")
        except Exception as e:
            return self._fail(f"Clear failed: {e}")
