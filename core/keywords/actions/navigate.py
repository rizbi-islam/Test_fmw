from core.keywords.base_keyword import BaseKeyword, KeywordResult


class NavigateKeyword(BaseKeyword):
    keyword_name = "NAVIGATE"
    description = "Navigate browser to a URL"
    required_params = ["value"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        url = context.resolve(params["value"])
        try:
            driver.navigate(url)
            context.set("current_url", driver.get_current_url())
            return self._pass(f"Navigated to: {url}")
        except Exception as e:
            return self._fail(f"Navigation failed: {e}")
