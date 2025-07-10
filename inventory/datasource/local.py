"""Local-only inventory datasource."""

from __future__ import annotations

from typing import Any, ClassVar, TYPE_CHECKING

from .base import BaseDataSource

if TYPE_CHECKING:
    from ..core import (
        House, Photo, Room, BookItem, DecorItem, MusicItem
    )

class LocalDataSource(BaseDataSource):
    """Data source that reads from local CSV files."""

    name: ClassVar[str] = "local"

    def load_house(self, house: "House") -> dict[str, Any]:
        pass

    def load_photo(self, photo: "Photo") -> dict[str, Any]:
        pass

    def load_room(self, room: "Room") -> dict[str, Any]:
        pass

    def load_book(self, book_item: "BookItem") -> dict[str, Any]:
        pass

    def load_decor(self, deco_item: "DecorItem") -> dict[str, Any]:
        pass

    def load_music(self, music_item: "MusicItem") -> dict[str, Any]:
        pass

__all__ = [
    "LocalDataSource",
]
