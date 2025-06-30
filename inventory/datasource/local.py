"""Local data source implementation."""

from .base import BaseDataSource


class LocalDataSource(BaseDataSource):
    """Simplistic local data source returning no data."""

    def load(self) -> dict:
        """Return an empty inventory data set."""
        return {}
