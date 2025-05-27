from typing import TYPE_CHECKING

from ..datasource.registry import all_data_source, BaseDataSource

def update_all_datasource() -> None:
    for ds in all_data_source:
        ds_instance: BaseDataSource = ds()
        ds_instance.update_all_securities(intraday=False)

def update_security_mapping() -> None:
    for ds in all_data_source:
        ds_instance: BaseDataSource = ds()
        ds_instance.update_security_mappings()

def update_all() -> None:
    update_security_mapping()
    update_all_datasource()