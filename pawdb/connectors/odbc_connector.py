import platform
import pyodbc
import pandas as pd
import logging
from pythonjsonlogger import jsonlogger
from .base import BaseConnector
from .decorators import log_execution_time


# create a custom JSON formatter to remove null values
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def process_log_record(self, log_record):
        return {key: value for key, value in log_record.items() if value is not None}


# Configure logger
logger = logging.getLogger("pawdb")
logger.setLevel(logging.INFO)

# Add a JSON formatter to the logger
if not logger.hasHandlers():
    stream_handler = logging.StreamHandler()
    json_formatter = CustomJsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s %(method)s %(query)s %(rows)s %(execution_time)s"
    )
    stream_handler.setFormatter(json_formatter)
    logger.addHandler(stream_handler)


class ODBCConnector(BaseConnector):
    """ODBC Connector for MS SQL Server."""

    def connect(self):
        """Establishes an ODBC connection using configuration parameters."""
        conn_str = (
            f"DRIVER={{{self.config.get('DRIVER', 'ODBC Driver 17 for SQL Server')}}};"
            f"SERVER={self.config['SERVER']};"
            f"DATABASE={self.config['DATABASE']};"
        )
        if platform.system() == "Windows" and self.config.get(
            "TRUSTED_CONNECTION", False
        ):
            conn_str += "Trusted_Connection=yes;"
        else:
            conn_str += f"UID={self.config['UID']};PWD={self.config['PWD']};"
        conn_str += "TrustServerCertificate=yes;"

        self.connection = pyodbc.connect(conn_str)
        self.cursor = self.connection.cursor()
        logger.info(
            "Connected to database.",
            extra={
                "method": f"{self.__module__}.{self.__class__.__name__}.connect",
                "database": self.config["DATABASE"],
            },
        )

    def close(self):
        """Closes the cursor and connection."""
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

        if params:
            df = pd.read_sql(query, self.connection, params=params)
        else:
            df = pd.read_sql(query, self.connection)
        return {"log_context": {"query": query, "rows_fetched": len(df)}, "data": df}
