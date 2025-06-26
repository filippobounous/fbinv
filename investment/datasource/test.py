import pandas as pd
import datetime
from typing import TYPE_CHECKING, ClassVar

from .base import BaseDataSource
from ..utils.exceptions import DataSourceMethodException

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

class TestDataSource(BaseDataSource):
    name: ClassVar[str] = "test"

    def _get_currency_cross_price_history_from_remote(
        self,
        security: 'CurrencyCross',
        intraday: bool,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")

    def _get_equity_price_history_from_remote(
        self,
        security: 'Equity',
        intraday: bool,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")

    def _get_etf_price_history_from_remote(
        self,
        security: 'ETF',
        intraday: bool,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")

    def _get_fund_price_history_from_remote(
        self,
        security: 'Fund',
        intraday: bool,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")
    
    @staticmethod
    def _format_price_history_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        return df
