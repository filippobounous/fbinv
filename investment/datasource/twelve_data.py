import pandas as pd
import requests
from typing import TYPE_CHECKING, List, Dict, Union
from twelvedata import TDClient

from .base import BaseDataSource
from ..config import TWELVE_DATA_API_KEY
from ..core.security.currency_cross import CurrencyCross

if TYPE_CHECKING:
    from ..core import Security

# https://github.com/twelvedata/twelvedata-python

class TwelveDataDataSource(BaseDataSource):
    name: str = "twelve_data"
    allowed_intervals: List[str] = [
        '1min', '5min', '15min', '30min', '45min',
        '1h', '2h', '4h', '8h', '1day',
        '1week', '1month'
    ]

    def _get_ts_from_remote(self, security: Security, interval: str = '1day') -> pd.DataFrame:
        if isinstance(security, CurrencyCross):
            symbol = f"{security.currency_vs}/{security.currency}"
        else:
            symbol = self._get_symbol(isin_code=security.code)

        if symbol is None:
            raise ValueError(f"Security {security.code} not found in {self.name} data source.")

        td = TDClient(apikey=TWELVE_DATA_API_KEY)
        
        if interval in self.allowed_intervals:
            df = td.time_series(
                symbol=symbol,
                interval=interval,
            ).as_pandas()
            return df
        else:
            raise ValueError(f"Interval {interval} not acceptable, please pass one of {self.allowed_intervals}.")
    
    @staticmethod
    def _get_symbol(isin_code: str) -> str:
        url = f"https://api.twelvedata.com/symbol_search?isin={isin_code}"
        response = requests.get(url)
        
        li : List[Dict[str, Union[float, str]]]= response.json()["data"]
        
        if len(li) > 0:
            return li[0].get("symbol")