from typing import TYPE_CHECKING

from ..datasource.registry import all_data_source, LocalDataSource

if TYPE_CHECKING:
    from ..datasource.base import BaseDataSource

def update_all_datasource() -> None:
    for ds in all_data_source:
        ds_instance: BaseDataSource = ds()
        ds_instance.update_all_securities(intraday=False)