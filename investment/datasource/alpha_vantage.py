"""Data source wrapper for the Alpha Vantage API."""

from typing import TYPE_CHECKING, ClassVar, Dict, Any, Tuple

import datetime
import pandas as pd
import requests

from .base import BaseDataSource
from ..config import ALPHA_VANTAGE_API_KEY
from ..utils.consts import DEFAULT_TIMEOUT
from ..utils.date_utils import today_midnight
from ..utils.exceptions import DataSourceMethodException, AlphaVantageException

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

# https://alpha-vantage.readthedocs.io/en/latest/
# https://www.alphavantage.co/documentation/
# https://pypi.org/project/alpha-vantage/

class AlphaVantageDataSource(BaseDataSource):
    """Remote data source using the Alpha Vantage API."""

    name: ClassVar[str] = "alpha_vantage"
    base_url: str = "https://www.alphavantage.co/query"

    def _get_currency_cross_price_history_from_remote(
        self,
        security: 'CurrencyCross', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Retrieve FX prices from Alpha Vantage."""
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

    def _get_equity_price_history_from_remote(
        self,
        security: 'Equity', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Retrieve equity prices from Alpha Vantage."""
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
            function_param = "TIME_SERIES_DAILY" # "TIME_SERIES_DAILY_ADJUSTED"

        params.update({
            "function": function_param,
            "symbol": security.alpha_vantage_code,
            "output_size": "full",
            "datatype": "json",
            "apikey": ALPHA_VANTAGE_API_KEY,
        })

        # TODO: finish alphavantage source
        response = self._get_response(self.base_url, params=params)
        data = None

        return pd.DataFrame(data).T

    def _get_etf_price_history_from_remote(
        self,
        security: 'ETF', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Retrieve ETF prices from Alpha Vantage."""
        # TODO: finish alphavantage source
        return self._get_equity_price_history_from_remote(
            security=security, intraday=intraday,
            start_date=start_date, end_date=end_date,
        )

    def _get_fund_price_history_from_remote(
        self,
        security: 'Fund', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Retrieve mutual fund prices from Alpha Vantage."""
        # TODO: finish alphavantage source
        return self._get_equity_price_history_from_remote(
            security=security, intraday=intraday,
            start_date=start_date, end_date=end_date,
        )

    @staticmethod
    def _format_price_history_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        """Normalise remote data to common column names."""
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
        """Send request and validate the response."""
        data = requests.get(url=url, params=params, timeout=DEFAULT_TIMEOUT).json()
        self._check_response(data=data)
        return data

    @staticmethod
    def _check_response(data: Dict[str, Any]) -> None:
        """Raise helpful errors when the API returns messages."""
        info = data.get("Information")
        if info:
            if "standard API rate limit" in info:
                raise AlphaVantageException(f"Rate limit exceeded: '{info}'")
            elif "This is a premium endpoint." in info:
                raise AlphaVantageException(f"Security not included in plan: '{info}'")

    def _default_start_and_end_date(
        self,
        df: pd.DataFrame, symbol: str,
        intraday: bool, **kwargs,
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        """Return sensible start/end dates for an update call."""
        if df.empty:
            return super()._default_start_and_end_date(
                df=df, symbol=symbol, intraday=intraday, **kwargs
            )
        start_date = df["as_of_date"].min()
        end_date = today_midnight()
        return start_date, end_date

    def _update_security_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a mapping DataFrame pulled from Alpha Vantage."""
        raise DataSourceMethodException(
            f"No remote security mapping for {self.name} datasource."
        )
