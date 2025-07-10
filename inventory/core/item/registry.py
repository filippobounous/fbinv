"""Full registy of BaseSecuirty subclasses"""

from typing import TYPE_CHECKING

from .book import BookItem
from .decor import DecorItem
from .music import MusicItem

if TYPE_CHECKING:
    from .base import BaseItem

all_securities: list['BaseItem']= [
    BookItem,
    DecorItem,
    MusicItem,
]

security_registry: dict[str, 'BaseItem'] = {
    i.model_fields["entity_type"].default: i
    for i in all_securities
}

__all__ = [
    "all_securities",
    "security_registry",
]
