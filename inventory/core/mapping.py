"""Base classes for mapping entities used in the inventory module."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from ..datasource import LocalDataSource

class BaseMappingEntity(BaseModel):
    """Base object populated from local mapping data.

    Attributes
    ----------
    is_deleted : bool
        Flag indicating whether the record has been soft deleted.
    version : int
        Revision number for the record.
    """

    entity_type: str
    id: int
    code: str
    name: str
    description: str | None = None
    notes: str | None = None
    version: int
    is_deleted: bool
    _local_datasource: LocalDataSource = LocalDataSource
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def __setattr__(self, name: str, value):
        """Allow setting undefined attributes without raising."""
        try:
            super().__setattr__(name, value)
        except ValueError:
            object.__setattr__(self, name, value)

    def __init__(self, **kwargs) -> None:
        """Initialise the object from local mapping files."""
        kwargs.setdefault(
            "entity_type", self.__class__.__fields__["entity_type"].default
        )
        super().__init__(**kwargs)

        lds: LocalDataSource = self._local_datasource()

        load_methods = {
            "household": lds.load_house,
            "photo": lds.load_photo,
            "room": lds.load_room,
            "book": lds.load_book,
            "decor": lds.load_decor,
            "item": lds.load_item,
        }

        init_method = load_methods.get(self.entity_type)

        if init_method is None:
            raise KeyError(f"Entity type '{self.entity_type}' has not been configured.")

        di: dict[str, Any] = init_method(self)
        for key, el in di.items():
            if hasattr(self, key):
                setattr(self, key, el)

__all__ = [
    "BaseMappingEntity",
]
