"""
SQLite Data Provider.
Zero-config local database — no server needed.
Perfect for local development and CI/CD environments.

Config:
    data:
      default_provider: sqlite
      sqlite:
        db_path: "data/kwaf_test.db"
"""
from typing import Any, Optional, List
from loguru import logger
from core.data.base_provider import BaseDataProvider


class SQLiteProvider(BaseDataProvider):
    """SQLite data provider using SQLAlchemy ORM."""

    def __init__(self, db_path: str = "data/kwaf_test.db"):
        self.db_path = db_path
        self._conn = None
        self._engine = None

    def connect(self) -> None:
        import os
        from sqlalchemy import create_engine, text
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        self._engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self._conn = self._engine.connect()
        logger.success(f"[SQLiteProvider] Connected: {self.db_path}")

    def disconnect(self) -> None:
        if self._conn:
            self._conn.close()
        if self._engine:
            self._engine.dispose()
        logger.info("[SQLiteProvider] Disconnected.")

    def get_row(self, sheet_or_table: str, row_index: int) -> dict:
        rows = self.get_all_rows(sheet_or_table)
        if row_index >= len(rows):
            raise IndexError(
                f"[SQLiteProvider] Row {row_index} out of range in '{sheet_or_table}' "
                f"(total: {len(rows)})"
            )
        return rows[row_index]

    def get_all_rows(self, sheet_or_table: str) -> List[dict]:
        from sqlalchemy import text
        result = self._conn.execute(text(f"SELECT * FROM {sheet_or_table}"))
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def get_value(self, sheet_or_table: str, row_index: int, column: str) -> Any:
        return self.get_row(sheet_or_table, row_index).get(column)

    def write_result(self, sheet_or_table: str, row_index: int,
                     column: str, value: Any) -> None:
        from sqlalchemy import text
        # Assumes table has a rowid; update by offset
        rows = self.get_all_rows(sheet_or_table)
        if row_index >= len(rows):
            raise IndexError(f"Row {row_index} out of range.")
        row = rows[row_index]
        # Find primary key (first column)
        pk_col = list(row.keys())[0]
        pk_val = row[pk_col]
        sql = text(f"UPDATE {sheet_or_table} SET {column} = :value WHERE {pk_col} = :pk")
        self._conn.execute(sql, {"value": value, "pk": pk_val})
        self._conn.commit()
        logger.debug(f"[SQLiteProvider] Updated {sheet_or_table}.{column} where {pk_col}={pk_val}")

    def find_row(self, sheet_or_table: str, column: str, value: Any) -> Optional[dict]:
        from sqlalchemy import text
        result = self._conn.execute(
            text(f"SELECT * FROM {sheet_or_table} WHERE {column} = :val"),
            {"val": value}
        )
        columns = list(result.keys())
        row = result.fetchone()
        if row:
            return dict(zip(columns, row))
        return None

    def create_table_from_excel(self, excel_path: str, sheet_name: str,
                                 table_name: str) -> None:
        """
        Utility: import an Excel sheet into SQLite table.
        Useful for migrating from Excel to DB workflow.
        """
        import openpyxl
        from sqlalchemy import text

        wb  = openpyxl.load_workbook(excel_path, data_only=True)
        ws  = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return

        headers = [str(h).strip().replace(" ", "_") if h else f"col_{i}"
                   for i, h in enumerate(rows[0])]
        cols_def = ", ".join([f"{h} TEXT" for h in headers])

        self._conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        self._conn.execute(text(f"CREATE TABLE {table_name} ({cols_def})"))

        for row in rows[1:]:
            if all(v is None for v in row):
                continue
            placeholders = ", ".join([f":col_{i}" for i in range(len(headers))])
            params = {f"col_{i}": str(v) if v is not None else ""
                      for i, v in enumerate(row)}
            self._conn.execute(
                text(f"INSERT INTO {table_name} VALUES ({placeholders})"), params
            )
        self._conn.commit()
        logger.success(
            f"[SQLiteProvider] Imported '{sheet_name}' -> table '{table_name}' "
            f"({len(rows)-1} rows)"
        )
