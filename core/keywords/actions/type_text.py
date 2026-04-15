from core.keywords.base_keyword import BaseKeyword, KeywordResult


class TypeTextKeyword(BaseKeyword):
    keyword_name = "TYPE"
    description = "Type text into an input field"
    required_params = ["locator", "value"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        locator = params["locator"]
        strategy = params.get("strategy", "css")
        text = context.resolve(params["value"])
        try:
            driver.type_text(locator, text, strategy)
            return self._pass(f"Typed '{text}' into [{strategy}] {locator}")
        except Exception as e:
            return self._fail(f"Type failed on [{strategy}] {locator}: {e}")
