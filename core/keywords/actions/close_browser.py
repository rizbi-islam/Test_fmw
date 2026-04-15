from core.keywords.base_keyword import BaseKeyword, KeywordResult


class CloseBrowserKeyword(BaseKeyword):
    keyword_name = "CLOSE_BROWSER"
    description = "Close the current browser"

    def execute(self, driver, context, params: dict) -> KeywordResult:
        try:
            driver.quit()
            return self._pass("Browser closed.")
        except Exception as e:
            return self._fail(f"Close browser failed: {e}")
