from core.keywords.base_keyword import BaseKeyword, KeywordResult


class GetTextKeyword(BaseKeyword):
    keyword_name = "GET_TEXT"
    description = "Get element text and store in context variable"
    required_params = ["locator"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        locator = params["locator"]
        strategy = params.get("strategy", "css")
        store_as = params.get("value", "last_text")
        try:
            text = driver.get_text(locator, strategy)
            context.set(store_as, text)
            return self._pass(f"Got text='{text}', stored as '{store_as}'", output=text)
        except Exception as e:
            return self._fail(f"GET_TEXT failed: {e}")
