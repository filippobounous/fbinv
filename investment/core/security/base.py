"""Base Security class as a generic abstraction for all others"""

from typing import ClassVar, TYPE_CHECKING

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
    name: str | None = None
    figi_code: str | None = None
    reporting_currency: str | None = None
    currency: str | None = None
    financial_times_code: str | None = None
    financial_times_security_type: str | None = None
    bloomberg_code: str | None = None
    yahoo_finance_code: str | None = None
    twelve_data_code: str | None = None
    alpha_vantage_code: str | None = None
    multiplier: float | None = None

    def __init__(self, code: str | None = None, **kwargs) -> None:
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
        datasource: "BaseDataSource" | None = None,
        local_only: bool = True,
        intraday: bool = False,
        currency: str | None = None,
    ) -> pd.DataFrame:
        """Returns price history"""
        if (not currency) or (currency == self.currency):
            _datasource = get_datasource(datasource=datasource)
            df =  _datasource.get_price_history(
                security=self, intraday=intraday, local_only=local_only
            )

        else:
            composite = self.convert_to_currency(currency=currency)
            df = composite.get_price_history(
                datasource=datasource,
                local_only=local_only,
                intraday=intraday,
            )

        return df

    def convert_to_currency(self, currency: str) -> "BaseSecurity" | "Composite":
        """Converts a security to its composite self, by applying a currency conversion"""
        from .composite import Composite
        return (
            self
            if currency ==  self.currency
            else Composite(security=self, composite_currency=currency)
        )
