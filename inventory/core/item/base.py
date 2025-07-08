from ..mapping import BaseMappingEntity

class BaseItem(BaseMappingEntity):
    entity_type: str = "item"
    room_code: str
    creator: str
    category: str
    subcategory: str

__all__ = [
    "BaseItem",
]
