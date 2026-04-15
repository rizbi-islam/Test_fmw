from core.keywords.base_keyword import BaseKeyword, KeywordResult


class ClickKeyword(BaseKeyword):
    keyword_name = "CLICK"
    description = "Click an element"
    required_params = ["locator"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        locator = params["locator"]
        strategy = params.get("strategy", "css")
        try:
            driver.click(locator, strategy)
            return self._pass(f"Clicked: [{strategy}] {locator}")
        except Exception as e:
            return self._fail(f"Click failed on [{strategy}] {locator}: {e}")
