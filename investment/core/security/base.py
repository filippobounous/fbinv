"""Base Security class as a generic abstraction for all others"""

from typing import Optional, ClassVar, TYPE_CHECKING, Union

import pandas as pd

from ...config import TIMESERIES_DATA_PATH
from ...datasource.utils import get_datasource
from ..mapping import BaseMappingEntity

if TYPE_CHECKING:
    from .composite import Composite
    from ...datasource.base import BaseDataSource


class BaseSecurity(BaseMappingEntity):
    """
    BaseSecurity
    
    Abstraction for generalised security classes.
    Not intended to be initialised alone.
    Generic input is code, all other attributes are initialised using LocalDataSource
    through BaseMappingEntity __init__.
    """
    entity_type: ClassVar[str] = "base_security"
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
        """Initialise security attributes from local mapping data."""
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

    def get_file_path(self, datasource_name: str, intraday: bool, series_type: str) -> str:
        """
        Returns the file path for the timeseries of a given security, datasource,
        type and frequency
        """
        from ...datasource.registry import LocalDataSource, OpenFigiDataSource

        if datasource_name == LocalDataSource.name:
            _code = "code"
        elif datasource_name == OpenFigiDataSource.name:
            _code = "figi_code"
        else:
            _code = getattr(self, f"{datasource_name}_code", None)

        code = _code.replace("/", "") if _code else _code

        data_frequency = "intraday" if intraday else "daily"

        path_name = f"{TIMESERIES_DATA_PATH}/{series_type}/{datasource_name}/{self.entity_type}"
        file_name = f"{code}-{data_frequency}-{series_type}.csv"
        return f"{path_name}/{file_name}"

    def get_price_history(
        self,
        datasource: Optional["BaseDataSource"] = None,
        local_only: bool = True,
        intraday: bool = False,
    ) -> pd.DataFrame:
        """Returns price history"""
        _datasource = get_datasource(datasource=datasource)
        return _datasource.get_price_history(
            security=self, intraday=intraday, local_only=local_only
        )

    def convert_to_currency(self, currency: str) -> Union["BaseSecurity", "Composite"]:
        """Converts a security to its composite self, by applying a currency conversion"""
        from .composite import Composite
        if currency ==  self.currency:
            return self
        else:
            return Composite(security=self, currency=currency)
