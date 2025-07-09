import datetime

from .mapping import BaseMappingEntity

class Photo(BaseMappingEntity):
    entity_type: str = "photo"
    related_entity_type: str
    related_code: str
    date_take: datetime.datetime
    photographer: str
    angle: str

__all__ = [
    "Photo",
]
