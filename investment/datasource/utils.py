"""Helpers for selecting the default data source."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import BaseDataSource


def get_datasource(datasource: "BaseDataSource" | None = None) -> "BaseDataSource":
    """Return the provided data source or the default one."""
    from .registry import default_timeseries_datasource

    if datasource is None:
        datasource = default_timeseries_datasource

    return datasource


__all__ = [
    "get_datasource",
]
