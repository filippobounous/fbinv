"""Base item model used by all inventory items."""

from ..mapping import BaseMappingEntity

class BaseItem(BaseMappingEntity):
    """Base class for any item stored in the inventory."""

    entity_type: str = "item"
    room_code: str
    creator: str
    category: str
    subcategory: str

__all__ = [
    "BaseItem",
]
