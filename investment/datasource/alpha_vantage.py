import datetime
import pandas as pd
import requests
from typing import TYPE_CHECKING, ClassVar, Dict, Any, Tuple

from .base import BaseDataSource
from ..config import ALPHA_VANTAGE_API_KEY
from ..utils.date_utils import today_midnight
from ..utils.exceptions import DataSourceMethodException, AlphaVantageException

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

# https://alpha-vantage.readthedocs.io/en/latest/
# https://www.alphavantage.co/documentation/
# https://pypi.org/project/alpha-vantage/

class AlphaVantageDataSource(BaseDataSource):
    name: ClassVar[str] = "alpha_vantage"
    base_url: str = "https://www.alphavantage.co/query"

    def _get_currency_cross_ts_from_remote(
        self,
        security: 'CurrencyCross', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
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
        
        response = self._get_response(self.base_url, params=params)
        data = None if intraday else response.get('Time Series FX (Daily)')

        return pd.DataFrame(data).T

    def _get_equity_ts_from_remote(
        self,
        security: 'Equity', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
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

        response = self._get_response(self.base_url, params=params)
        data = None

        return pd.DataFrame(data).T

    def _get_etf_ts_from_remote(
        self,
        security: 'ETF', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException("Method not implemented.")

    def _get_fund_ts_from_remote(
        self,
        security: 'Fund', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException("Method not implemented.")
    
    @staticmethod
    def _format_ts_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        df = df.reset_index().rename(columns={
            "index": "as_of_date",
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
        })
        df['as_of_date'] = pd.to_datetime(df['as_of_date'])
        return df
        
    def _get_response(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        data = requests.get(url=url, params=params).json()
        self._check_response(data=data)
        return data
    
    @staticmethod
    def _check_response(data: Dict[str, Any]) -> None:
        info = data.get("Information")
        if info and "standard API rate limit" in info:
            raise AlphaVantageException(f"AlphaVantageException, rate limit exceeded: '{info}'")

    def _default_start_and_end_date(self, df: pd.DataFrame, **kwargs) -> Tuple[datetime.datetime, datetime.datetime]:
        if df.empty:
            return super()._default_start_and_end_date(df=df, **kwargs)
        start_date = df["as_of_date"].min()
        end_date = today_midnight()
        return start_date, end_date

    def _update_security_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote security mapping for {self.name} datasource.")
