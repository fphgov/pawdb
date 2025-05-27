"""SQLite Connector module for development and testing."""

import sqlite3
import pandas as pd
from .base import BaseConnector
from .decorators import log_execution_time

from . import logger


class SQLiteConnector(BaseConnector):
    """SQLite Connector for development and testing."""

    def connect(self):
        """Establishes a connection to the SQLite database."""
        db_path = self.config.get("DATABASE", ":memory:")  # Default to in-memory DB
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        logger.info(
            "Connected to SQLite database.",
            extra={
                "method": f"{self.__module__}.{self.__class__.__name__}.connect",
                "database": db_path,
            },
        )

    def close(self):
        """Closes the cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info(
            "SQLite database connection closed.",
            extra={"method": f"{self.__module__}.{self.__class__.__name__}.close"},
        )

    @log_execution_time
    def execute_query(self, query: str, params: dict = None) -> None:
        """Execute a query without returning results."""
        if not self.connection:
            self.connect()

        self.cursor.execute(query, params or {})
        self.connection.commit()
        return {"log_context": {"query": query, "rows_affected": self.cursor.rowcount}}

    @log_execution_time
    def fetch_query_to_list(self, query: str, params: dict = None) -> list[tuple]:
        """Execute a query and fetch all results as a list of tuples."""
        if not self.connection:
            self.connect()

        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return {
            "log_context": {"query": query, "rows_fetched": len(rows)},
            "data": rows,
        }

    @log_execution_time
    def fetch_query_to_pandas(self, query: str, params: dict = None) -> pd.DataFrame:
        """Return query results as a DataFrame."""
        if not self.connection:
            self.connect()

        df = pd.read_sql(query, self.connection, params=params)
        return {"log_context": {"query": query, "rows_fetched": len(df)}, "data": df}
