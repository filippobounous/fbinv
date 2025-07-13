"""Base classes for mapping entities used in the inventory module."""

from __future__ import annotations

from abc import abstractmethod
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
    name: str | None = None
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

        di: dict[str, Any] = lds.load_entity(self)
        for key, el in di.items():
            if hasattr(self, key):
                setattr(self, key, el)

    @property
    def missing_fields(self) -> list[str]:
        """Return a list of required arguments that are missing."""
        return [arg for arg in self.required_fields if getattr(self, arg, None) is None]

    @property
    def base_required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""
        return ["entity_type", "id", "code", "version", "is_deleted"]

    @property
    @abstractmethod
    def required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""


__all__ = [
    "BaseMappingEntity",
]
