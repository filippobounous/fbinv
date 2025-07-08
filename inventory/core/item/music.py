from .base import BaseItem


class MusicItem(BaseItem):
    """A music recording stored in the inventory."""

    entity_type: str = "music"
    language: str
    type_format: str

__all__ = [
    "MusicItem",
]
