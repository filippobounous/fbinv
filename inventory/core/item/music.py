from .base import BaseItem

class MusicItem(BaseItem):
    entity_type: str = "music"
    language: str
    type_format: str

__all__ = [
    "MusicItem",
]
