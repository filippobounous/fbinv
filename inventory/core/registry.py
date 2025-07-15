"""Registry of all mapping entity classes in the inventory module."""

from typing import TYPE_CHECKING

from . import Category, House, Photo, Room, Subcategory
from .item import BaseItem, Book, Decor, Music

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from .mapping import BaseMappingEntity

all_entities: list[type["BaseMappingEntity"]] = [
    House,
    Room,
    Category,
    Subcategory,
    Photo,
    BaseItem,
    Book,
    Decor,
    Music,
]

entity_registry: dict[str, type["BaseMappingEntity"]] = {
    cls.model_fields["entity_type"].default: cls for cls in all_entities
}

__all__ = [
    "all_entities",
    "entity_registry",
]
