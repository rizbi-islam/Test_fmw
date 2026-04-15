"""
Selenium WebDriver Implementation.
Supports Chrome, Firefox, Edge with automatic driver management.
"""
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from loguru import logger

from core.drivers.base_driver import BaseDriver

STRATEGY_MAP = {
    "css":          By.CSS_SELECTOR,
    "xpath":        By.XPATH,
    "id":           By.ID,
    "name":         By.NAME,
    "class":        By.CLASS_NAME,
    "tag":          By.TAG_NAME,
    "link_text":    By.LINK_TEXT,
    "partial_link": By.PARTIAL_LINK_TEXT,
}


class SeleniumDriver(BaseDriver):
    """Selenium 4 WebDriver — Chrome/Firefox/Edge."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.browser = config.get("browser", "chrome").lower()
        self.headless = config.get("headless", False)
        self.implicit_wait = config.get("implicit_wait", 10)
        self.page_load_timeout = config.get("page_load_timeout", 30)
        self.window_size = config.get("window_size", "1920,1080")
        self.remote_url = config.get("remote_url", None)

    def start(self) -> None:
        logger.info(f"[SeleniumDriver] Starting {self.browser} | headless={self.headless}")
        self.driver = self._build_driver()
        self.driver.implicitly_wait(self.implicit_wait)
        self.driver.set_page_load_timeout(self.page_load_timeout)
        w, h = self.window_size.split(",")
        self.driver.set_window_size(int(w), int(h))
        self._is_active = True
        logger.success("[SeleniumDriver] Browser started.")

    def quit(self) -> None:
        if self.driver:
            self.driver.quit()
            self._is_active = False
            logger.info("[SeleniumDriver] Browser closed.")

    def _build_driver(self):
        if self.remote_url:
            options = webdriver.ChromeOptions()
            return webdriver.Remote(command_executor=self.remote_url, options=options)
        builders = {
            "chrome":  self._build_chrome,
            "firefox": self._build_firefox,
            "edge":    self._build_edge,
        }
        build_fn = builders.get(self.browser)
        if not build_fn:
            raise ValueError(f"Unsupported browser: {self.browser}. Use: chrome, firefox, edge")
        return build_fn()

    def _build_chrome(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={self.window_size}")
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _build_firefox(self):
        options = webdriver.FirefoxOptions()
        if self.headless:
            options.add_argument("--headless")
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)

    def _build_edge(self):
        options = webdriver.EdgeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        service = EdgeService(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=options)

    def _by(self, strategy: str) -> str:
        return STRATEGY_MAP.get(strategy.lower(), By.CSS_SELECTOR)

    def navigate(self, url: str) -> None:
        logger.debug(f"[SeleniumDriver] Navigate -> {url}")
        self.driver.get(url)

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title

    def go_back(self) -> None:
        self.driver.back()

    def go_forward(self) -> None:
        self.driver.forward()

    def refresh(self) -> None:
        self.driver.refresh()

    def find_element(self, locator: str, strategy: str = "css"):
        return self.driver.find_element(self._by(strategy), locator)

    def find_elements(self, locator: str, strategy: str = "css") -> list:
        return self.driver.find_elements(self._by(strategy), locator)

    def click(self, locator: str, strategy: str = "css") -> None:
        logger.debug(f"[SeleniumDriver] Click -> [{strategy}] {locator}")
        self.wait_for_element_clickable(locator, strategy=strategy)
        self.find_element(locator, strategy).click()

    def type_text(self, locator: str, text: str, strategy: str = "css") -> None:
        logger.debug(f"[SeleniumDriver] Type '{text}' -> [{strategy}] {locator}")
        el = self.find_element(locator, strategy)
        el.clear()
        el.send_keys(text)

    def clear(self, locator: str, strategy: str = "css") -> None:
        self.find_element(locator, strategy).clear()

    def get_text(self, locator: str, strategy: str = "css") -> str:
        return self.find_element(locator, strategy).text

    def get_attribute(self, locator: str, attribute: str, strategy: str = "css") -> str:
        return self.find_element(locator, strategy).get_attribute(attribute)

    def select_by_text(self, locator: str, text: str, strategy: str = "css") -> None:
        Select(self.find_element(locator, strategy)).select_by_visible_text(text)

    def select_by_value(self, locator: str, value: str, strategy: str = "css") -> None:
        Select(self.find_element(locator, strategy)).select_by_value(value)

    def wait_for_element(self, locator: str, timeout: int = 10, strategy: str = "css") -> None:
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((self._by(strategy), locator))
        )

    def wait_for_element_clickable(self, locator: str, timeout: int = 10, strategy: str = "css") -> None:
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((self._by(strategy), locator))
        )

    def wait_for_url_contains(self, text: str, timeout: int = 10) -> None:
        WebDriverWait(self.driver, timeout).until(EC.url_contains(text))

    def screenshot(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.driver.save_screenshot(path)
        logger.info(f"[SeleniumDriver] Screenshot -> {path}")

    def scroll_to_element(self, locator: str, strategy: str = "css") -> None:
        el = self.find_element(locator, strategy)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", el)

    def scroll_to_top(self) -> None:
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to_bottom(self) -> None:
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def hover(self, locator: str, strategy: str = "css") -> None:
        ActionChains(self.driver).move_to_element(self.find_element(locator, strategy)).perform()

    def switch_to_frame(self, locator: str, strategy: str = "css") -> None:
        self.driver.switch_to.frame(self.find_element(locator, strategy))

    def switch_to_default_content(self) -> None:
        self.driver.switch_to.default_content()

    def execute_script(self, script: str, *args) -> any:
        return self.driver.execute_script(script, *args)

    def _resolve_strategy(self, strategy: str):
        return self._by(strategy)
