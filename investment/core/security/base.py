from typing import Optional, ClassVar

from ...config import HISTORICAL_DATA_PATH
from ..mapping import BaseMappingEntity

class Security(BaseMappingEntity):
    entity_type: ClassVar[str] = "security"
    name: Optional[str] = None
    reporting_currency: Optional[str] = None
    currency: Optional[str] = None
    financial_times_code: Optional[str] = None
    financial_times_security_type: Optional[str] = None
    bloomberg_code: Optional[str] = None
    yahoo_finance_code: Optional[str] = None
    twelve_data_code: Optional[str] = None
    alpha_vantage_code: Optional[str] = None
    multiplier: Optional[float] = None

    def __init__(self, code: Optional[str] = None, **kwargs):
        from ...datasource.registry import data_source_codes
        
        if code is not None:
            kwargs["code"] = code

        super().__init__(**kwargs)

        missing = [
            k
            for k, v in self.__dict__.items()
            if v is None and k not in ["entity_type"] + data_source_codes
        ]
        if missing:
            raise ValueError(f"{self.code} is missing required values for: {missing}.")

    def get_file_path(self, datasource_name: str, intraday: bool) -> str:
        file_name = getattr(self, f"{datasource_name}_code", None)
        folder_name = "intraday" if intraday else "daily"
        return f"{HISTORICAL_DATA_PATH}/{folder_name}/{datasource_name}/{self.entity_type}/{file_name}_{folder_name}.csv"