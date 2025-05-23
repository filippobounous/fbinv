import datetime
import pandas as pd
from pydantic import ConfigDict
import requests
from twelvedata import TDClient
from typing import TYPE_CHECKING, List, Dict, Union, ClassVar, Tuple, Any

from .base import BaseDataSource
from ..config import TWELVE_DATA_API_KEY

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

# https://github.com/twelvedata/twelvedata-python

class TwelveDataDataSource(BaseDataSource):
    name: ClassVar[str] = "twelve_data"
    td: TDClient = TDClient(apikey=TWELVE_DATA_API_KEY)
    output_size: int = 5000
    data_start_date: datetime.datetime = datetime.datetime(2003,12,1)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _get_currency_cross_ts_from_remote(
        self,
        security: 'CurrencyCross', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        symbol = f"{security.currency_vs}/{security.currency}"
        return self._time_series(
            symbol=symbol, intraday=intraday,
            start_date=start_date, end_date=end_date,
        )

    def _get_equity_ts_from_remote(
        self,
        security: 'Equity', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise NotImplementedError("Method not implemented.")

    def _get_etf_ts_from_remote(
        self,
        security: 'ETF', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise NotImplementedError("Method not implemented.")

    def _get_fund_ts_from_remote(
        self,
        security: 'Fund', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise NotImplementedError("Method not implemented.")
    
    @staticmethod
    def _get_symbol(isin_code: str) -> str:
        url = f"https://api.twelvedata.com/symbol_search?isin={isin_code}"
        response = requests.get(url)
        
        li : List[Dict[str, Union[float, str]]]= response.json()["data"]
        
        if len(li) > 0:
            return li[0].get("symbol")
    
    @staticmethod
    def _format_ts_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        return df.reset_index().rename(columns={"datetime": "as_of_date"})
    
    def _get_dates(
        self,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        intraday: bool
    ) -> List[Tuple[datetime.datetime, datetime.datetime]]:
        result = []
        current_start = start_date
        shifted_end_date = end_date + datetime.timedelta(days=2) # required by API

        delta = (
            timedelta(minutes=self.output_size)
            if intraday
            else datetime.timedelta(days=self.output_size - 1)
        )

        while current_start <= shifted_end_date:
            current_end = min(
                current_start + delta,
                shifted_end_date,
            )
            result.append((current_start, current_end))
            current_start = current_end + datetime.timedelta(days=1)

        return result
        
    def _time_series(
        self,
        symbol: str, intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        interval =  "1min" if intraday else "1day"
        
        dfs = []
        dates = self._get_dates(start_date=start_date, end_date=end_date, intraday=intraday)

        for _start_date, _end_date in dates:
            dfs.append(self.td.time_series(
                symbol=symbol,
                interval=interval,
                outputsize=self.output_size,
                start_date=_start_date.strftime("%Y-%m-%d"),
                end_date=_end_date.strftime("%Y-%m-%d"),
            ).as_pandas())

        return pd.concat(dfs)
    
    def usage(self) -> Dict[str, Any]:
        return self.td.api_usage().as_json()