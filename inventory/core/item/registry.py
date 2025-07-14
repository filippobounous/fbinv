"""Full registy of BaseItem subclasses"""

from typing import TYPE_CHECKING

from .book import Book
from .decor import Decor
from .music import Music

if TYPE_CHECKING:
    from .base import BaseItem

all_securities: list["BaseItem"] = [
    Book,
    Decor,
    Music,
]

security_registry: dict[str, "BaseItem"] = {
    i.model_fields["entity_type"].default: i for i in all_securities
}

__all__ = [
    "all_securities",
    "security_registry",
]
