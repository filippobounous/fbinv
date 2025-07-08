from .mapping import BaseMappingEntity


class Room(BaseMappingEntity):
    """A room within a house that can contain items."""

    entity_type: str = "room"
    house_code: str
    room_type: str
    floor: int
    area_sqm: float
    windows: int
    doors: int

__all__ = [
    "Room",
]
