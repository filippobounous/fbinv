import pandas as pd
from typing import TYPE_CHECKING

from .base import BaseDataSource

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

class BloombergDataSource(BaseDataSource):
    name: str = "bloomberg"

    def _get_currency_cross_ts_from_remote(self, security: 'CurrencyCross', intraday: bool) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")

    def _get_equity_ts_from_remote(self, security: 'Equity', intraday: bool) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")

    def _get_etf_ts_from_remote(self, security: 'ETF', intraday: bool) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")

    def _get_fund_ts_from_remote(self, security: 'Fund', intraday: bool) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")
    
    @staticmethod
    def _format_ts_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError(f"Not implemented.")