from core.keywords.base_keyword import BaseKeyword, KeywordResult


class ScrollToElementKeyword(BaseKeyword):
    keyword_name = "SCROLL_TO"
    description = "Scroll to an element or direction"

    def execute(self, driver, context, params: dict) -> KeywordResult:
        try:
            if "locator" in params and params["locator"]:
                strategy = params.get("strategy", "css")
                driver.scroll_to_element(params["locator"], strategy)
                return self._pass(f"Scrolled to element: {params['locator']}")
            direction = params.get("value", "bottom").lower()
            if direction == "top":
                driver.scroll_to_top()
            else:
                driver.scroll_to_bottom()
            return self._pass(f"Scrolled to: {direction}")
        except Exception as e:
            return self._fail(f"Scroll failed: {e}")
