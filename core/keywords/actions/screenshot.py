import os
from datetime import datetime
from core.keywords.base_keyword import BaseKeyword, KeywordResult


class ScreenshotKeyword(BaseKeyword):
    keyword_name = "SCREENSHOT"
    description = "Take a screenshot and save it"

    def execute(self, driver, context, params: dict) -> KeywordResult:
        filename = params.get("value", f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        screenshot_dir = context.get("screenshot_dir", "assets/screenshots")
        path = os.path.join(screenshot_dir, filename)
        try:
            driver.screenshot(path)
            context.add_screenshot(path)
            return self._pass(f"Screenshot saved: {path}", output=path)
        except Exception as e:
            return self._fail(f"Screenshot failed: {e}")
