"""Helpers for selecting the default data source."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .base import BaseDataSource

def get_datasource(datasource: Optional["BaseDataSource"] = None) -> "BaseDataSource":
    """Return the provided data source or the default one."""
    from .registry import default_timeseries_datasource

    if datasource is None:
        datasource = default_timeseries_datasource

    return datasource
