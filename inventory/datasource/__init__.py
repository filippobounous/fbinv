"""Inventory BaseDataSource class and its subclasses to load, read and write various data types"""

from .base import BaseDataSource
from .local import LocalDataSource

__all__ = ["BaseDataSource", "LocalDataSource"]
