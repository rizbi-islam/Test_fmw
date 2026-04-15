"""
JSON Data Provider.
Reads test data from .json files.

Config:
    data:
      default_provider: json
      json:
        data_dir: "assets/data"

JSON format expected:
{
  "TestData": [
    {"RowID": "row1", "username": "user1", "password": "pass1"},
    {"RowID": "row2", "username": "user2", "password": "pass2"}
  ]
}
"""
import json
import os
from typing import Any, Optional, List
from loguru import logger
from core.data.base_provider import BaseDataProvider


class JsonProvider(BaseDataProvider):
    """Reads test data from JSON files. One file per dataset."""

    def __init__(self, data_dir: str = "assets/data"):
        self.data_dir   = data_dir
        self._cache: dict = {}

    def connect(self) -> None:
        os.makedirs(self.data_dir, exist_ok=True)
        self._load_all()
        logger.success(f"[JsonProvider] Loaded {len(self._cache)} datasets from {self.data_dir}")

    def disconnect(self) -> None:
        self._cache.clear()

    def _load_all(self) -> None:
        """Load all .json files from data_dir."""
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.data_dir, filename)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    # Each key = a table name
                    for table_name, rows in data.items():
                        self._cache[table_name] = rows
                        logger.debug(f"[JsonProvider] Loaded table '{table_name}' ({len(rows)} rows)")
                elif isinstance(data, list):
                    # Use filename without extension as table name
                    table_name = os.path.splitext(filename)[0]
                    self._cache[table_name] = data

    def get_row(self, sheet_or_table: str, row_index: int) -> dict:
        rows = self._get_rows(sheet_or_table)
        if row_index >= len(rows):
            raise IndexError(f"[JsonProvider] Row {row_index} out of range in '{sheet_or_table}'")
        return rows[row_index]

    def get_all_rows(self, sheet_or_table: str) -> List[dict]:
        return list(self._get_rows(sheet_or_table))

    def get_value(self, sheet_or_table: str, row_index: int, column: str) -> Any:
        return self.get_row(sheet_or_table, row_index).get(column)

    def write_result(self, sheet_or_table: str, row_index: int,
                     column: str, value: Any) -> None:
        """Write result back to in-memory cache (not persisted to file)."""
        self._get_rows(sheet_or_table)[row_index][column] = value
        logger.debug(f"[JsonProvider] In-memory update: {sheet_or_table}[{row_index}].{column}={value}")

    def find_row(self, sheet_or_table: str, column: str, value: Any) -> Optional[dict]:
        for row in self._get_rows(sheet_or_table):
            if str(row.get(column, "")).strip() == str(value).strip():
                return row
        return None

    def _get_rows(self, table_name: str) -> List[dict]:
        if table_name not in self._cache:
            raise ValueError(
                f"[JsonProvider] Table '{table_name}' not found. "
                f"Available: {list(self._cache.keys())}"
            )
        return self._cache[table_name]
