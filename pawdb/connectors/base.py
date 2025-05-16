"""Interface for database connectors."""

from abc import ABC, abstractmethod
import pandas as pd


class BaseConnector(ABC):
    """Interface for database connectors."""

    def __init__(self, config: dict):
        """
        Initialize the connector with a configuration dictionary.

        Args:
            config (dict): Configuration dictionary containing connection parameters.
        """
        self.config = config
        self.connection = None
        self.cursor = None

    @abstractmethod
    def execute_query(self, query: str, params: dict = None) -> None:
        """Execute a query that does not return results."""
        pass

    @abstractmethod
    def fetch_query(self, query: str, params: dict = None) -> list[tuple]:
        """Fetch results from a query."""
        pass

    @abstractmethod
    def read_query(self, query: str, params: dict = None) -> pd.DataFrame:
        """Read a query and return the results as a DataFrame."""
        pass

    @abstractmethod
    def connect(self):
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def close(self):
        """Close the database connection."""
        pass
