"""
MySQL Data Provider.
Production-grade relational DB provider using SQLAlchemy + PyMySQL.

Config in config.yaml:
    data:
      default_provider: mysql
      mysql:
        host: "localhost"
        port: 3306
        database: "kwaf_db"
        username: "root"
        password: "your_password"
        pool_size: 5
"""
from typing import Any, Optional, List
from loguru import logger
from core.data.base_provider import BaseDataProvider


class MySQLProvider(BaseDataProvider):
    """MySQL data provider using SQLAlchemy + PyMySQL driver."""

    def __init__(self, host: str = "localhost", port: int = 3306,
                 database: str = "kwaf_db", username: str = "root",
                 password: str = "", pool_size: int = 5):
        self.host      = host
        self.port      = int(port)
        self.database  = database
        self.username  = username
        self.password  = password
        self.pool_size = pool_size
        self._engine   = None
        self._conn     = None

    def connect(self) -> None:
        from sqlalchemy import create_engine
        url = (
            f"mysql+pymysql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
            f"?charset=utf8mb4"
        )
        self._engine = create_engine(url, pool_size=self.pool_size, echo=False)
        self._conn   = self._engine.connect()
        logger.success(
            f"[MySQLProvider] Connected: {self.username}@{self.host}:{self.port}/{self.database}"
        )

    def disconnect(self) -> None:
        if self._conn:
            self._conn.close()
        if self._engine:
            self._engine.dispose()
        logger.info("[MySQLProvider] Disconnected.")

    def get_row(self, sheet_or_table: str, row_index: int) -> dict:
        rows = self.get_all_rows(sheet_or_table)
        if row_index >= len(rows):
            raise IndexError(
                f"[MySQLProvider] Row {row_index} out of range in '{sheet_or_table}'"
            )
        return rows[row_index]

    def get_all_rows(self, sheet_or_table: str) -> List[dict]:
        from sqlalchemy import text
        result  = self._conn.execute(text(f"SELECT * FROM `{sheet_or_table}`"))
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def get_value(self, sheet_or_table: str, row_index: int, column: str) -> Any:
        return self.get_row(sheet_or_table, row_index).get(column)

    def write_result(self, sheet_or_table: str, row_index: int,
                     column: str, value: Any) -> None:
        from sqlalchemy import text
        rows   = self.get_all_rows(sheet_or_table)
        row    = rows[row_index]
        pk_col = list(row.keys())[0]
        pk_val = row[pk_col]
        sql = text(
            f"UPDATE `{sheet_or_table}` SET `{column}` = :value WHERE `{pk_col}` = :pk"
        )
        self._conn.execute(sql, {"value": value, "pk": pk_val})
        self._conn.commit()
        logger.debug(f"[MySQLProvider] Updated {sheet_or_table}.{column}")

    def find_row(self, sheet_or_table: str, column: str, value: Any) -> Optional[dict]:
        from sqlalchemy import text
        result  = self._conn.execute(
            text(f"SELECT * FROM `{sheet_or_table}` WHERE `{column}` = :val LIMIT 1"),
            {"val": value}
        )
        columns = list(result.keys())
        row     = result.fetchone()
        return dict(zip(columns, row)) if row else None
