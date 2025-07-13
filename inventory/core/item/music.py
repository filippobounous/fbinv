"""Inventory item model for music media."""

from .base import BaseItem


class Music(BaseItem):
    """A music recording stored in the inventory."""

    entity_type: str = "music"
    language: str
    type_format: str

    @property
    def required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""
        return super().required_fields + [
            "language",
            "type_format",
        ]


__all__ = [
    "Music",
]
