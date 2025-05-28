from tqdm import tqdm
from typing import TYPE_CHECKING, Dict, Tuple

from ..datasource.registry import all_datasource

if TYPE_CHECKING:
    from ..datasource.base import BaseDataSource

def update_all_timeseries() -> Dict[str, Dict[str, bool]]:
    di = {}
    for ds in tqdm(all_datasource, desc="Updating all data sources"):
        ds_instance: "BaseDataSource" = ds()
        di[ds_instance.name] = ds_instance.update_all_timeseries(intraday=False)
    return di

def update_security_mapping() -> Dict[str, bool]:
    di = {}
    for ds in tqdm(all_datasource, desc="Updating all security mappings"):
        ds_instance: "BaseDataSource" = ds()
        di[ds_instance.name] = False if ds_instance.update_security_mappings().empty else True
    return di

def update_all() -> Tuple[Dict[str, bool], Dict[str, Dict[str, bool]]]:
    di_mapping = update_security_mapping()
    di_timeseries = update_all_timeseries()
    return di_mapping, di_timeseries