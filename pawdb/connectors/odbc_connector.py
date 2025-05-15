import platform
import pyodbc
import pandas as pd
from .base import BaseConnector


class ODBCConnector(BaseConnector):
    """ODBC Connector for MS SQL Server."""

    def connect(self):
        """
        Establishes an ODBC connection using configuration parameters.
        Expected keys in self.config: DRIVER, SERVER, DATABASE, UID, PWD, optional TRUSTED_CONNECTION.
        """
        conn_str = (
            f"DRIVER={{{self.config.get('DRIVER', 'ODBC Driver 17 for SQL Server')}}};"
            f"SERVER={self.config['SERVER']};"
            f"DATABASE={self.config['DATABASE']};"
        )

        # Check if running on Windows and TRUSTED_CONNECTION is enabled
        if platform.system() == "Windows" and self.config.get(
            "TRUSTED_CONNECTION", False
        ):
            conn_str += "Trusted_Connection=yes;"
        else:
            # Default to SQL Server Authentication
            conn_str += f"UID={self.config['UID']};PWD={self.config['PWD']};"

        # Add TrustServerCertificate for SSL connections
        conn_str += "TrustServerCertificate=yes;"

        # Establish the connection
        self.connection = pyodbc.connect(conn_str)
        self.cursor = self.connection.cursor()

    def close(self):
        """Closes the cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: dict = None) -> None:
        """Execute a query without returning results."""
        if not self.connection:
            self.connect()

        self.cursor.execute(query, params or {})
        self.connection.commit()

    def fetch_query(self, query: str, params: dict = None) -> list:
        """Execute a query and fetch all results as a list of tuples."""
        if not self.connection:
            self.connect()

        if params:
            # Pass parameters only if they exist
            self.cursor.execute(query, params)
        else:
            # Execute query without parameters
            self.cursor.execute(query)

        return self.cursor.fetchall()

    def read_query(self, query: str, params: dict = None) -> pd.DataFrame:
        """Return query results as a DataFrame."""
        if not self.connection:
            self.connect()

        return pd.read_sql(query, self.connection, params=params or {})
