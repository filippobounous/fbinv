import datetime
import pandas as pd
import re
from typing import TYPE_CHECKING, ClassVar
import yfinance as yf

from .base import BaseDataSource
from ..utils.consts import DATA_START_DATE
from ..utils.date_utils import today_midnight

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

# https://ranaroussi.github.io/yfinance/

class YahooFinanceDataSource(BaseDataSource):
    name: ClassVar[str] = "yahoo_finance"

    def _get_currency_cross_ts_from_remote(
        self,
        security: 'CurrencyCross', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        symbol = security.yahoo_finance_code
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
    def _format_ts_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        df_simple = df.copy().reset_index()
        df_simple.columns = [
            re.sub(r"\s+", "_", col.lower())
            for col in df_simple.columns.get_level_values(0)
        ]
        df_simple = df_simple.rename(columns={"date": "as_of_date"})
        return df_simple
        
    def _time_series(
        self,
        symbol: str, intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        if symbol is None:
            return pd.DataFrame()
        
        interval =  "1m" if intraday else "1d"

        end_date = end_date + datetime.timedelta(days=2) # required by API
        
        return yf.download(
            symbol,
            interval=interval,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            auto_adjust=True,
        )
