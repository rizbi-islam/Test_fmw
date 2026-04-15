"""Abstract Data Provider — all data sources implement this contract."""
from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseDataProvider(ABC):

    @abstractmethod
    def connect(self) -> None:
        """Initialize connection to the data source."""

    @abstractmethod
    def disconnect(self) -> None:
        """Close the connection."""

    @abstractmethod
    def get_row(self, sheet_or_table: str, row_index: int) -> dict:
        """Return one row as a dict by index (0-based)."""

    @abstractmethod
    def get_all_rows(self, sheet_or_table: str) -> list:
        """Return all rows from a sheet/table as list of dicts."""

    @abstractmethod
    def get_value(self, sheet_or_table: str, row_index: int, column: str) -> Any:
        """Return a single cell/field value."""

    @abstractmethod
    def write_result(self, sheet_or_table: str, row_index: int,
                     column: str, value: Any) -> None:
        """Write a result back to the data source."""

    @abstractmethod
    def find_row(self, sheet_or_table: str, column: str, value: Any) -> Optional[dict]:
        """Find first row where column == value."""
