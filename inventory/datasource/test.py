"""Simple local data source used for testing."""

from typing import ClassVar

from .base import BaseDataSource


class TestDataSource(BaseDataSource):
    """Very small data source used for tests only."""

    name: ClassVar[str] = "test"
    __test__ = False  # avoid pytest treating this as a test class
