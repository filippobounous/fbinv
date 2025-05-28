import datetime
import pandas as pd
from typing import TYPE_CHECKING, ClassVar

from .base import BaseDataSource
from ..utils.exceptions import DataSourceMethodException

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

class FinancialTimesDataSource(BaseDataSource):
    name: ClassVar[str] = "financial_times"

    def _get_currency_cross_ts_from_remote(
        self,
        security: 'CurrencyCross', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")

    def _get_equity_ts_from_remote(
        self,
        security: 'Equity', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")

    def _get_etf_ts_from_remote(
        self,
        security: 'ETF', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")

    def _get_fund_ts_from_remote(
        self,
        security: 'Fund', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")
    
    @staticmethod
    def _format_ts_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        return df

    def _update_security_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote security mapping for {self.name} datasource.")
