from core.keywords.base_keyword import BaseKeyword, KeywordResult


class AssertTextKeyword(BaseKeyword):
    keyword_name = "ASSERT_TEXT"
    description = "Assert element text equals expected value"
    required_params = ["locator", "value"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        locator = params["locator"]
        strategy = params.get("strategy", "css")
        expected = context.resolve(params["value"])
        try:
            actual = driver.get_text(locator, strategy)
            if expected.lower() in actual.lower():
                return self._pass(f"ASSERT_TEXT passed. Expected='{expected}' in Actual='{actual}'")
            return self._fail(f"ASSERT_TEXT failed. Expected='{expected}', Actual='{actual}'")
        except Exception as e:
            return self._fail(f"ASSERT_TEXT error: {e}")


class AssertVisibleKeyword(BaseKeyword):
    keyword_name = "ASSERT_VISIBLE"
    description = "Assert element is visible on page"
    required_params = ["locator"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        locator = params["locator"]
        strategy = params.get("strategy", "css")
        try:
            driver.wait_for_element(locator, timeout=5, strategy=strategy)
            return self._pass(f"Element visible: [{strategy}] {locator}")
        except Exception as e:
            return self._fail(f"Element NOT visible: [{strategy}] {locator}: {e}")


class AssertUrlContainsKeyword(BaseKeyword):
    keyword_name = "ASSERT_URL"
    description = "Assert current URL contains expected text"
    required_params = ["value"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        expected = context.resolve(params["value"])
        actual_url = driver.get_current_url()
        if expected.lower() in actual_url.lower():
            return self._pass(f"URL contains '{expected}'. Current: {actual_url}")
        return self._fail(f"URL assertion failed. Expected '{expected}' in '{actual_url}'")
