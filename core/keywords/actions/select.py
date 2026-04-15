from core.keywords.base_keyword import BaseKeyword, KeywordResult


class SelectKeyword(BaseKeyword):
    keyword_name = "SELECT"
    description = "Select dropdown option by text or value"
    required_params = ["locator", "value"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        locator = params["locator"]
        strategy = params.get("strategy", "css")
        value = context.resolve(params["value"])
        select_by = params.get("select_by", "text").lower()
        try:
            if select_by == "value":
                driver.select_by_value(locator, value, strategy)
            else:
                driver.select_by_text(locator, value, strategy)
            return self._pass(f"Selected '{value}' by {select_by} on {locator}")
        except Exception as e:
            return self._fail(f"Select failed: {e}")
