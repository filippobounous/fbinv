"""Base classes for inventory data sources."""

from pydantic import BaseModel


class BaseDataSource(BaseModel):
    """Simplistic interface for loading inventory data."""

    def load(self) -> dict:
        """Load data from the underlying source."""
        raise NotImplementedError
