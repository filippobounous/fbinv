"""Helper functions for working with datasource instances."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from .base import BaseDataSource


def get_datasource(datasource: Optional["BaseDataSource"] = None) -> "BaseDataSource":
    """Return a datasource instance or the default timeseries datasource."""

    from .registry import default_timeseries_datasource

    if datasource is None:
        datasource = default_timeseries_datasource

    return datasource
