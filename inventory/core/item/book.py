"""Inventory item model representing books."""

from .base import BaseItem


class Book(BaseItem):
    """A book item with language and format information."""

    entity_type: str = "book"
    language: str | None = None
    type_format: str | None = None

    @property
    def required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""
        return super().required_fields + [
            "language",
        ]


__all__ = [
    "Book",
]
