from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .base import BaseDataSource

def get_datasource(datasouce: Optional["BaseDataSource"] = None) -> "BaseDataSource":
    from .registry import default_timeseries_datasource

    if datasource is None:
        datasource = default_timeseries_datasource

    return datasouce