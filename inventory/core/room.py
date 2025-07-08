from .mapping import BaseMappingEntity

class Room(BaseMappingEntity):
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
