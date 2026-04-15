from core.keywords.base_keyword import BaseKeyword, KeywordResult


class SwitchFrameKeyword(BaseKeyword):
    keyword_name = "SWITCH_FRAME"
    description = "Switch driver context into an iframe"
    required_params = ["locator"]

    def execute(self, driver, context, params: dict) -> KeywordResult:
        self.validate_params(params)
        locator = params["locator"]
        strategy = params.get("strategy", "css")
        try:
            driver.switch_to_frame(locator, strategy)
            return self._pass(f"Switched to frame: {locator}")
        except Exception as e:
            return self._fail(f"Switch frame failed: {e}")


class SwitchDefaultKeyword(BaseKeyword):
    keyword_name = "SWITCH_DEFAULT"
    description = "Switch back to main page from frame"

    def execute(self, driver, context, params: dict) -> KeywordResult:
        try:
            driver.switch_to_default_content()
            return self._pass("Switched to default content.")
        except Exception as e:
            return self._fail(f"Switch default failed: {e}")
