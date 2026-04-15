from core.keywords.base_keyword import BaseKeyword, KeywordResult


class VerifyUrlKeyword(BaseKeyword):
    keyword_name = "VERIFY_URL"
    description = "Verify page URL contains text, with wait"
    required_params = ["value"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        expected = context.resolve(params["value"])
        timeout = int(params.get("timeout", 10))
        try:
            driver.wait_for_url_contains(expected, timeout)
            return self._pass(f"URL verified. Contains: '{expected}'")
        except Exception as e:
            return self._fail(f"URL verify failed. Expected '{expected}': {e}")
