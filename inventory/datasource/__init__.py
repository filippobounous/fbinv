"""Inventory data source classes."""

from .base import BaseDataSource
from .local import LocalDataSource

__all__ = ["BaseDataSource", "LocalDataSource"]
