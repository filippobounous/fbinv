"""Base item model used by all inventory items."""

from ..mapping import BaseMappingEntity

class BaseItem(BaseMappingEntity):
    """Base class for any item stored in the inventory."""

    entity_type: str = "item"
    room_code: str | None = None
    creator: str | None = None
    category: str | None = None
    subcategory: str | None = None

    @property
    def required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""
        return self.base_required_fields + [
            "room_code",
            "creator",
            "category",
            "subcategory",
        ]

__all__ = [
    "BaseItem",
]
