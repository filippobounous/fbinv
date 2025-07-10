"""Registry of available inventory data sources."""

from typing import TYPE_CHECKING

from .local import LocalDataSource

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from .base import BaseDataSource

all_datasource: list["BaseDataSource"] = [
    LocalDataSource,
]

datasource_registry: dict[str, "BaseDataSource"] = {
    LocalDataSource.name: LocalDataSource,
}

datasource_codes: list[str] = [
    f"{LocalDataSource.name}_code",
]

default_datasource = LocalDataSource()

__all__ = [
    "all_datasource",
    "datasource_registry",
    "datasource_codes",
    "default_datasource",
]
