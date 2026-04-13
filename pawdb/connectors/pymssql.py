"""pymssql Connector module for MS SQL Server (via FreeTDS)."""

import pymssql
import pandas as pd
from .base import BaseConnector
from .decorators import log_execution_time

from . import logger


class PyMSSQLConnector(BaseConnector):
    """MS SQL Server connector using pymssql / FreeTDS.

    This avoids the Microsoft ODBC driver entirely by relying on
    FreeTDS for the TDS protocol layer.

    Expected config keys:
        SERVER   - hostname or IP of the SQL Server instance
        DATABASE - database name
        UID      - username
        PWD      - password
        PORT     - (optional) port number, defaults to 1433
        CHARSET  - (optional) character set, defaults to 'utf8'
    """

    def connect(self):
        """Establish a connection to MS SQL Server via pymssql."""
        self.connection = pymssql.connect(
            server=self.config["SERVER"],
            user=self.config["UID"],
            password=self.config["PWD"],
            database=self.config["DATABASE"],
            port=str(self.config.get("PORT", "1433")),
            charset=self.config.get("CHARSET", "utf8"),
        )
        self.cursor = self.connection.cursor()
        logger.info(
            "Connected to database.",
            extra={
                "method": f"{self.__module__}.{self.__class__.__name__}.connect",
                "database": self.config["DATABASE"],
            },
        )

    def close(self):
        """Close the cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info(
            "Database connection closed.",
            extra={"method": f"{self.__module__}.{self.__class__.__name__}.close"},
        )

    @log_execution_time
    def execute_query(self, query: str, params: dict = None) -> None:
        """Execute a query without returning results."""
        if not self.connection:
            self.connect()

        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
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

        if params:
            df = pd.read_sql(query, self.connection, params=params)
        else:
            df = pd.read_sql(query, self.connection)
        return {"log_context": {"query": query, "rows_fetched": len(df)}, "data": df}
