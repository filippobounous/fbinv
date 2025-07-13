"""Model representing rooms inside houses."""

from .mapping import BaseMappingEntity

class Room(BaseMappingEntity):
    """A room within a house that can contain items."""

    entity_type: str = "room"
    house_code: str | None = None
    room_type: str | None = None
    floor: int | None = None
    area_sqm: float | None = None
    windows: int | None = None
    doors: int | None = None

    @property
    def required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""
        return self.base_required_fields + [
            "house_code",
            "room_type",
            "floor",
        ]

__all__ = [
    "Room",
]
