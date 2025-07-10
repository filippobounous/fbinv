"""Helpers for selecting the default inventory data source."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .registry import default_datasource

if TYPE_CHECKING:
    from .base import BaseDataSource

def get_datasource(datasource: "BaseDataSource" | None = None) -> "BaseDataSource":
    """Return the provided data source or the default one."""
    if datasource is None:
        datasource = default_datasource
    return datasource

__all__ = [
    "get_datasource",
]
