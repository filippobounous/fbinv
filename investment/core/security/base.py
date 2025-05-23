from typing import Optional

from ..mapping import BaseMappingEntity
from ..config import HISTORICAL_DATA_PATH

class Security(BaseMappingEntity):
    entity_type: str = "security"
    name: Optional[str] = None
    isin_code: Optional[str] = None
    reporting_currency: Optional[str] = None
    currency: Optional[str] = None
    financial_times_code: Optional[str] = None
    financial_times_security_type: Optional[str] = None
    bloomberg_code: Optional[str] = None
    yahoo_finance_code: Optional[str] = None
    multiplier: Optional[float] = None

    def get_file_path(self, datasource_name: str) -> str:
        file_name = getattr(self, f"{datasource_name}_code", None)
        return f"{HISTORICAL_DATA_PATH}/{datasource_name}/{file_name}"