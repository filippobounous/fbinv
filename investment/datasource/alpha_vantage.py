import pandas as pd
import requests
from typing import TYPE_CHECKING

from .base import BaseDataSource
from ..config import ALPHA_VANTAGE_API_KEY

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

# https://alpha-vantage.readthedocs.io/en/latest/
# https://www.alphavantage.co/documentation/
# https://pypi.org/project/alpha-vantage/

class AlphaVantageDataSource(BaseDataSource):
    name: str = "alpha_vantage"
    base_url: str = "https://www.alphavantage.co/query"

    def _get_currency_cross_ts_from_remote(self, security: 'CurrencyCross', intraday: bool) -> pd.DataFrame:
        params = {}
        if intraday:
            function_param = "FX_INTRADAY"
            params.update({"interval": "1min"})
        else:
            function_param = "FX_DAILY"
        
        params.update({
            "function": function_param,
            "from_symbol": security.currency_vs,
            "to_symbol": security.currency,
            "output_size": "full",
            "datatype": "json",
            "apikey": ALPHA_VANTAGE_API_KEY,
        })
        
        data = requests.get(self.base_url, params=params).json()

        return pd.DataFrame(data)

    def _get_equity_ts_from_remote(self, security: 'Equity', intraday: bool) -> pd.DataFrame:
        params = {}
        if intraday:
            function_param = "TIME_SERIES_INTRADAY"
            params.update({
                "interval": "1min",
                "symbol": security.alpha_vantage_code,
                "adjusted": True,
                "extended_hours": True,
            })
        else:
            function_param = "TIME_SERIES_DAILY_ADJUSTED"
        
        params.update({
            "function": function_param,
            "symbol": security.alpha_vantage_code,
            "output_size": "full",
            "datatype": "json",
            "apikey": ALPHA_VANTAGE_API_KEY,
        })
        
        data = requests.get(self.base_url, params=params).json()

        return pd.DataFrame(data)

    def _get_etf_ts_from_remote(self, security: 'ETF', intraday: bool) -> pd.DataFrame:
        raise NotImplementedError("Method not implemented.")

    def _get_fund_ts_from_remote(self, security: 'Fund', intraday: bool) -> pd.DataFrame:
        raise NotImplementedError("Method not implemented.")
    
    @staticmethod
    def _format_ts_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        pass # TODO