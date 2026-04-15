from core.keywords.base_keyword import BaseKeyword, KeywordResult


class HoverKeyword(BaseKeyword):
    keyword_name = "HOVER"
    description = "Hover the mouse over an element"
    required_params = ["locator"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        locator = params["locator"]
        strategy = params.get("strategy", "css")
        try:
            driver.hover(locator, strategy)
            return self._pass(f"Hovered over: [{strategy}] {locator}")
        except Exception as e:
            return self._fail(f"Hover failed: {e}")
