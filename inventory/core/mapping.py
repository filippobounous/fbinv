"""Base classes for mapping entities used in the inventory module."""

from __future__ import annotations

import datetime
from abc import abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict

from ..datasource import (
    LocalDataSource,
    datasource_registry,
    default_datasource,
)


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
    sys_create_time: datetime.datetime

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
        missing = []
        for arg in self.required_fields:
            if getattr(self, arg, None) is None:
                missing.append(arg)
        return missing

    @property
    def base_required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""
        return ["entity_type", "id", "code", "version", "is_deleted"]

    @property
    @abstractmethod
    def required_fields(self) -> list[str]:
        """Return a list of required fields for the entity."""

    def edit(self, **kwargs: Any) -> None:
        """Update attributes and increment version/time stamp."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.version += 1
        self.sys_create_time = datetime.datetime.now(datetime.timezone.utc)

    def save(self, datasource_name: str = default_datasource.name) -> None:
        """Append the current entity to the specified datasource CSV."""
        ds_cls = datasource_registry.get(datasource_name)
        if ds_cls is None:
            raise KeyError(f"Datasource '{datasource_name}' not found")
        ds = ds_cls()
        path = Path(ds.mapping_path(self.entity_type))
        df = pd.DataFrame([self.model_dump()])
        df.to_csv(path, mode="a", index=False, header=not path.exists())


__all__ = [
    "BaseMappingEntity",
]
