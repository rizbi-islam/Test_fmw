"""
Playwright Driver Implementation.
Faster, more reliable for modern web apps. Supports Chromium/Firefox/WebKit.
"""
import os
from loguru import logger
from core.drivers.base_driver import BaseDriver


class PlaywrightDriver(BaseDriver):
    """Playwright driver — Chromium/Firefox/WebKit."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.browser_type = config.get("browser", "chromium").lower()
        self.headless = config.get("headless", False)
        self.page_load_timeout = config.get("page_load_timeout", 30) * 1000
        self.window_size = config.get("window_size", "1920,1080")
        self._playwright = None
        self._browser = None
        self._context = None
        self.page = None

    def start(self) -> None:
        logger.info(f"[PlaywrightDriver] Starting {self.browser_type} | headless={self.headless}")
        from playwright.sync_api import sync_playwright
        self._playwright = sync_playwright().start()
        w, h = [int(x) for x in self.window_size.split(",")]
        browser_map = {
            "chromium": self._playwright.chromium,
            "chrome":   self._playwright.chromium,
            "firefox":  self._playwright.firefox,
            "webkit":   self._playwright.webkit,
        }
        launcher = browser_map.get(self.browser_type, self._playwright.chromium)
        self._browser = launcher.launch(headless=self.headless)
        self._context = self._browser.new_context(viewport={"width": w, "height": h})
        self.page = self._context.new_page()
        self.page.set_default_timeout(self.page_load_timeout)
        self._is_active = True
        logger.success("[PlaywrightDriver] Browser started.")

    def quit(self) -> None:
        if self.page:
            self.page.close()
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self._is_active = False
        logger.info("[PlaywrightDriver] Browser closed.")

    def _selector(self, locator: str, strategy: str) -> str:
        strategy = strategy.lower()
        if strategy == "id":
            return f"#{locator}"
        if strategy == "name":
            return f"[name='{locator}']"
        if strategy == "xpath":
            return f"xpath={locator}"
        return locator

    def navigate(self, url: str) -> None:
        logger.debug(f"[PlaywrightDriver] Navigate -> {url}")
        self.page.goto(url)

    def get_current_url(self) -> str:
        return self.page.url

    def get_title(self) -> str:
        return self.page.title()

    def go_back(self) -> None:
        self.page.go_back()

    def go_forward(self) -> None:
        self.page.go_forward()

    def refresh(self) -> None:
        self.page.reload()

    def find_element(self, locator: str, strategy: str = "css"):
        return self.page.locator(self._selector(locator, strategy)).first

    def find_elements(self, locator: str, strategy: str = "css") -> list:
        return self.page.locator(self._selector(locator, strategy)).all()

    def click(self, locator: str, strategy: str = "css") -> None:
        logger.debug(f"[PlaywrightDriver] Click -> {locator}")
        self.page.locator(self._selector(locator, strategy)).first.click()

    def type_text(self, locator: str, text: str, strategy: str = "css") -> None:
        el = self.page.locator(self._selector(locator, strategy)).first
        el.clear()
        el.fill(text)

    def clear(self, locator: str, strategy: str = "css") -> None:
        self.page.locator(self._selector(locator, strategy)).first.clear()

    def get_text(self, locator: str, strategy: str = "css") -> str:
        return self.page.locator(self._selector(locator, strategy)).first.inner_text()

    def get_attribute(self, locator: str, attribute: str, strategy: str = "css") -> str:
        return self.page.locator(self._selector(locator, strategy)).first.get_attribute(attribute)

    def select_by_text(self, locator: str, text: str, strategy: str = "css") -> None:
        self.page.locator(self._selector(locator, strategy)).first.select_option(label=text)

    def select_by_value(self, locator: str, value: str, strategy: str = "css") -> None:
        self.page.locator(self._selector(locator, strategy)).first.select_option(value=value)

    def wait_for_element(self, locator: str, timeout: int = 10, strategy: str = "css") -> None:
        self.page.locator(self._selector(locator, strategy)).first.wait_for(
            state="visible", timeout=timeout * 1000
        )

    def wait_for_element_clickable(self, locator: str, timeout: int = 10, strategy: str = "css") -> None:
        self.page.locator(self._selector(locator, strategy)).first.wait_for(
            state="visible", timeout=timeout * 1000
        )

    def wait_for_url_contains(self, text: str, timeout: int = 10) -> None:
        self.page.wait_for_url(f"**{text}**", timeout=timeout * 1000)

    def screenshot(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.page.screenshot(path=path)
        logger.info(f"[PlaywrightDriver] Screenshot -> {path}")

    def scroll_to_element(self, locator: str, strategy: str = "css") -> None:
        self.page.locator(self._selector(locator, strategy)).first.scroll_into_view_if_needed()

    def scroll_to_top(self) -> None:
        self.page.evaluate("window.scrollTo(0, 0)")

    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def hover(self, locator: str, strategy: str = "css") -> None:
        self.page.locator(self._selector(locator, strategy)).first.hover()

    def switch_to_frame(self, locator: str, strategy: str = "css") -> None:
        logger.warning("[PlaywrightDriver] Use frame_locator for iframe handling in Playwright.")

    def switch_to_default_content(self) -> None:
        pass

    def execute_script(self, script: str, *args) -> any:
        return self.page.evaluate(script, *args)

    def _resolve_strategy(self, strategy: str):
        return strategy
