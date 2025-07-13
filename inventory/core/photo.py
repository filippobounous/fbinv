"""Models for photos linked to inventory entities."""

import datetime

from .mapping import BaseMappingEntity

class Photo(BaseMappingEntity):
    """Model representing a photo linked to a mapping entity."""

    entity_type: str = "photo"
    related_entity_type: str | None = None
    related_code: str | None = None
    date_take: datetime.datetime | None = None
    photographer: str | None = None
    angle: str | None = None

    @property
    def required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""
        return self.base_required_fields + [
            "related_entity_type",
            "related_code",
            "date_take",
            "photographer",
            "angle",
        ]

__all__ = [
    "Photo",
]
