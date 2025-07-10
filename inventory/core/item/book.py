"""Inventory item model representing books."""

from .base import BaseItem

class Book(BaseItem):
    """A book item with language and format information."""

    entity_type: str = "book"
    language: str
    type_format: str

__all__ = [
    "Book",
]
