import sqlite3
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class RowResult:
    cells: dict[str, Any]


class SqliteDriver:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None


    def connect(self) -> sqlite3.Connection:
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn


    def execute_query(self, query: str, params: Optional[list[Any]] = None) -> Optional[list[RowResult]]:
        try:
            conn = self.connect()
            cursor = conn.cursor()
            print(f"executing query: {query}")
            cursor.execute(query, params or [])
            if cursor.description is None:
                return None
            rows = cursor.fetchall()
            return [RowResult(cells=dict(row)) for row in rows]
        except Exception as e:
            print(f"Error executing query: {e}")
            raise e
