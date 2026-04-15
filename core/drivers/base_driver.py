"""
Abstract Base Driver
All concrete drivers MUST implement this contract.
Adding a new driver = create new file + inherit this class.
"""
from abc import ABC, abstractmethod
from typing import Optional
from loguru import logger


class BaseDriver(ABC):
    """
    Contract for all driver implementations.
    Defines the mandatory interface that the Keyword Engine uses.
    """

    def __init__(self, config: dict):
        self.config = config
        self.driver = None
        self._is_active = False

    # --- Lifecycle ---

    @abstractmethod
    def start(self) -> None:
        """Initialize and launch the driver/browser."""

    @abstractmethod
    def quit(self) -> None:
        """Terminate the driver/browser cleanly."""

    # --- Navigation ---

    @abstractmethod
    def navigate(self, url: str) -> None:
        """Navigate to a URL."""

    @abstractmethod
    def get_current_url(self) -> str:
        """Return the current page URL."""

    @abstractmethod
    def get_title(self) -> str:
        """Return the current page title."""

    @abstractmethod
    def go_back(self) -> None:
        """Browser back."""

    @abstractmethod
    def go_forward(self) -> None:
        """Browser forward."""

    @abstractmethod
    def refresh(self) -> None:
        """Reload the page."""

    # --- Element Interaction ---

    @abstractmethod
    def find_element(self, locator: str, strategy: str = "css"):
        """Find a single element."""

    @abstractmethod
    def find_elements(self, locator: str, strategy: str = "css") -> list:
        """Find multiple elements."""

    @abstractmethod
    def click(self, locator: str, strategy: str = "css") -> None:
        """Click an element."""

    @abstractmethod
    def type_text(self, locator: str, text: str, strategy: str = "css") -> None:
        """Clear and type text into an input."""

    @abstractmethod
    def clear(self, locator: str, strategy: str = "css") -> None:
        """Clear an input field."""

    @abstractmethod
    def get_text(self, locator: str, strategy: str = "css") -> str:
        """Return visible text of an element."""

    @abstractmethod
    def get_attribute(self, locator: str, attribute: str, strategy: str = "css") -> str:
        """Return an element attribute value."""

    @abstractmethod
    def select_by_text(self, locator: str, text: str, strategy: str = "css") -> None:
        """Select dropdown option by visible text."""

    @abstractmethod
    def select_by_value(self, locator: str, value: str, strategy: str = "css") -> None:
        """Select dropdown option by value."""

    # --- Waits ---

    @abstractmethod
    def wait_for_element(self, locator: str, timeout: int = 10, strategy: str = "css") -> None:
        """Wait until element is visible."""

    @abstractmethod
    def wait_for_element_clickable(self, locator: str, timeout: int = 10, strategy: str = "css") -> None:
        """Wait until element is clickable."""

    @abstractmethod
    def wait_for_url_contains(self, text: str, timeout: int = 10) -> None:
        """Wait until URL contains text."""

    # --- Page Actions ---

    @abstractmethod
    def screenshot(self, path: str) -> None:
        """Take a screenshot and save to path."""

    @abstractmethod
    def scroll_to_element(self, locator: str, strategy: str = "css") -> None:
        """Scroll element into view."""

    @abstractmethod
    def scroll_to_top(self) -> None:
        """Scroll to top of page."""

    @abstractmethod
    def scroll_to_bottom(self) -> None:
        """Scroll to bottom of page."""

    @abstractmethod
    def hover(self, locator: str, strategy: str = "css") -> None:
        """Mouse hover over element."""

    @abstractmethod
    def switch_to_frame(self, locator: str, strategy: str = "css") -> None:
        """Switch context into an iframe."""

    @abstractmethod
    def switch_to_default_content(self) -> None:
        """Switch back to main document."""

    @abstractmethod
    def execute_script(self, script: str, *args) -> any:
        """Execute JavaScript."""

    # --- Properties ---

    @property
    def is_active(self) -> bool:
        return self._is_active

    def _resolve_strategy(self, strategy: str):
        raise NotImplementedError
