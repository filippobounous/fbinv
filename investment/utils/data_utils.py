from tqdm import tqdm
from typing import TYPE_CHECKING, Dict, Tuple

from ..datasource.registry import all_datasource

if TYPE_CHECKING:
    from ..datasource.base import BaseDataSource


def update_all_price_history(
    intraday: bool = False, local_only: bool = False
) -> Dict[str, Dict[str, bool]]:
    di = {}
    for ds in tqdm(all_datasource, desc="Updating all data sources"):
        ds_instance: "BaseDataSource" = ds()
        di[ds_instance.name] = ds_instance.update_price_histories(
            intraday=intraday, local_only=local_only
        )
    return di


def update_all_security_mapping() -> Dict[str, bool]:
    di = {}
    for ds in tqdm(all_datasource, desc="Updating all security mappings"):
        ds_instance: "BaseDataSource" = ds()
        di[ds_instance.name] = (
            False if ds_instance.update_security_mapping().empty else True
        )
    return di


def update_all(
    intraday: bool = False, local_only: bool = False
) -> Tuple[Dict[str, bool], Dict[str, Dict[str, bool]]]:
    di_mapping = update_all_security_mapping()
    di_timeseries = update_all_price_history(intraday=intraday, local_only=local_only)
    return di_mapping, di_timeseries
