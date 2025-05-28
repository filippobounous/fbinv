import pandas as pd
from typing import Optional, ClassVar, TYPE_CHECKING

from ...config import HISTORICAL_DATA_PATH
from ..mapping import BaseMappingEntity

if TYPE_CHECKING:
    from ...datasource.base import BaseDataSource

class Security(BaseMappingEntity):
    entity_type: ClassVar[str] = "security"
    name: Optional[str] = None
    figi_code: Optional[str] = None
    reporting_currency: Optional[str] = None
    currency: Optional[str] = None
    financial_times_code: Optional[str] = None
    financial_times_security_type: Optional[str] = None
    bloomberg_code: Optional[str] = None
    yahoo_finance_code: Optional[str] = None
    twelve_data_code: Optional[str] = None
    alpha_vantage_code: Optional[str] = None
    multiplier: Optional[float] = None

    def __init__(self, code: Optional[str] = None, **kwargs) -> None:
        from ...datasource.registry import datasource_codes
        
        if code is not None:
            kwargs["code"] = code

        super().__init__(**kwargs)

        missing = [
            k
            for k, v in self.__dict__.items()
            if v is None and k not in ["entity_type"] + datasource_codes
        ]
        if missing:
            raise ValueError(f"{self.code} is missing required values for: {missing}.")

    def get_file_path(self, datasource_name: str, intraday: bool) -> str:
        from ...datasource.registry import LocalDataSource, OpenFigiDataSource

        if datasource_name == LocalDataSource.name:
            _file_name = "code"
        elif datasource_name == OpenFigiDataSource.name:
            _file_name = "figi_code"
        else:
            _file_name = getattr(self, f"{datasource_name}_code", None)
        
        file_name = _file_name.replace("/", "") if _file_name else _file_name

        folder_name = "intraday" if intraday else "daily"
        return f"{HISTORICAL_DATA_PATH}/{folder_name}/{datasource_name}/{self.entity_type}/{file_name}_{folder_name}.csv"

    def get_timeseries(self, datasource: Optional["BaseDataSource"] = None, local_only: bool = False, intraday: bool = False) -> pd.DataFrame:
        from ...datasource.registry import default_timeseries_datasource

        if datasource is None:
            datasource = default_timeseries_datasource
        
        return datasource.get_timeseries(security=self, intraday=intraday, local_only=local_only)
