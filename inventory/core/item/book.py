from .base import BaseItem

class BookItem(BaseItem):
    entity_type: str = "book"
    language: str
    type_format: str

__all__ = [
    "BookItem",
]
