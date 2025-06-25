import datetime
import pandas as pd
from pydantic import ConfigDict
from itertools import product
import requests
from time import sleep
from tqdm import tqdm
from twelvedata import TDClient
from twelvedata.exceptions import TwelveDataError
from typing import TYPE_CHECKING, List, Dict, ClassVar, Tuple, Any, Optional
import warnings

from .base import BaseDataSource
from ..config import TWELVE_DATA_API_KEY
from ..utils.date_utils import today_midnight
from ..utils.exceptions import TwelveDataException

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund, BaseSecurity

# https://github.com/twelvedata/twelvedata-python

class TwelveDataDataSource(BaseDataSource):
    name: ClassVar[str] = "twelve_data"
    base_url: str = "https://api.twelvedata.com"
    _td: Optional[TDClient] = None
    output_size: int = 5000
    request_counter: ClassVar[int] = 0
    window_start: ClassVar[datetime.datetime] = datetime.datetime.utcnow() # free version limitation
    max_requests_per_minute: ClassVar[int] = 8 # free version limitation

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def td(self) -> TDClient:
        if not self._td:
            self._td = TDClient(apikey=TWELVE_DATA_API_KEY)
        return self._td

    def _get_currency_cross_price_history_from_remote(
        self,
        security: 'CurrencyCross', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        return self._get_security_ts_from_remote(
            security=security, intraday=intraday,
            start_date=start_date, end_date=end_date,
        )

    def _get_equity_price_history_from_remote(
        self,
        security: 'Equity', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        return self._get_security_ts_from_remote(
            security=security, intraday=intraday,
            start_date=start_date, end_date=end_date,
        )

    def _get_etf_price_history_from_remote(
        self,
        security: 'ETF', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        return self._get_security_ts_from_remote(
            security=security, intraday=intraday,
            start_date=start_date, end_date=end_date,
        )

    def _get_fund_price_history_from_remote(
        self,
        security: 'Fund', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        return self._get_security_ts_from_remote(
            security=security, intraday=intraday,
            start_date=start_date, end_date=end_date,
        )

    def _get_security_ts_from_remote(
        self,
        security: 'BaseSecurity', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        return self._time_series(
            symbol=security.twelve_data_code, intraday=intraday,
            start_date=start_date, end_date=end_date,
        )
    
    @staticmethod
    def _format_price_history_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
        else:
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
            datetime.timedelta(minutes=self.output_size)
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
        interval = self._interval_code(intraday=intraday)
        dfs = []

        dates = self._get_dates(start_date=start_date, end_date=end_date, intraday=intraday)

        for _start_date, _end_date in dates:
            self._respect_rate_limit()
            try:
                df = self.td.time_series(
                    symbol=symbol,
                    interval=interval,
                    outputsize=self.output_size,
                    start_date=_start_date.strftime("%Y-%m-%d"),
                    end_date=_end_date.strftime("%Y-%m-%d"),
                ).as_pandas()
            except TwelveDataError as e:
                warnings.warn(f"""
                    Missing data for parmas:
                    symbol({symbol}), interval({interval}), outputsize({self.output_size}),
                    start_date({_start_date.strftime("%Y-%m-%d")}), end_date({_end_date.strftime("%Y-%m-%d")})
                """)
                df = pd.DataFrame()

            dfs.append(df)

        return pd.concat(dfs)

    def _check_start_date_for_security(self, symbol: str, intraday: bool) -> Optional[datetime.datetime]:
        df = self.get_security_mapping()

        # this actually does not get triggered as there is an earlier exception raised
        if symbol not in df["symbol"].to_list():
            warnings.warn(f"Updating mapping for {symbol} in {self.name} datasource.")

            df = self.update_security_mapping()

            if symbol not in df["symbol"]:
                warnings.warn(f"Missing mapping for {symbol} in {self.name} datasource.")
        
        row = df[df["symbol"] == symbol].iloc[0].to_dict()
        value = row.get(self._earliest_date_column(intraday=intraday))

        return pd.to_datetime(value) if (value and not pd.isna(value)) else None
    
    def _interval_code(self, intraday: bool) -> str:
        return "1min" if intraday else "1day"
    
    def _earliest_date_column(self, intraday: bool) -> str:
        return f"earliest_date_intraday_{intraday}"

    def _respect_rate_limit(self):
        cls = self.__class__  # For cleaner access to class variables

        now = datetime.datetime.utcnow()
        if now - cls.window_start >= datetime.timedelta(minutes=1):
            cls.window_start = now
            cls.request_counter = 0

        if cls.request_counter >= cls.max_requests_per_minute:
            time_to_wait = 60 - (now - cls.window_start).total_seconds()
            if time_to_wait > 0:
                print(f"Pausing for {time_to_wait} seconds.")
                sleep(time_to_wait)

            cls.window_start = datetime.datetime.utcnow()
            cls.request_counter = 0

        cls.request_counter += 1
    
    def usage(self) -> Dict[str, Any]:
        self._respect_rate_limit()
        return self.td.api_usage().as_json()

    def available_data(self, entity_type: str) -> pd.DataFrame:
        available_entities = {
            "currency_cross": "forex_pairs",
            "equity": "stocks",
            "crypto": "cryptocurrencies",
            "fund": "funds",
            "bond": "bonds",
            "etf": "etfs",
            "commodity": "commodities",
            "exchange": "exchanges",
        }
        code = available_entities.get(entity_type)
        if code:
            url = f"{self.base_url}/{code}"
            response = requests.get(url)
            if entity_type in ["fund", "bond"]:
                data = response.json().get('result').get('list')
            else:
                data = response.json().get("data")
            return pd.DataFrame(data)
        else:
            return pd.DataFrame()
        
    def earliest_date(self, symbol: str, intraday: bool = False) -> Optional[datetime.datetime]:
        self._respect_rate_limit()
        params = {
            "symbol": symbol,
            "apikey": TWELVE_DATA_API_KEY,
            "interval": self._interval_code(intraday=intraday),
        }
        url = f"{self.base_url}/earliest_timestamp"
        response = requests.get(url, params=params)

        data = response.json()
        if data.get("status") == "error":
            return None
        else:
            return datetime.datetime.utcfromtimestamp(data.get("unix_time"))
        
    def _update_security_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        df_list = []
        for entity_type, _df in tqdm(df.groupby("type"), desc=f"Updating security mapping for {self.name}"):
            mapping_df = self.available_data(entity_type=entity_type)

            df_merged = mapping_df.merge(
                _df[[self.internal_mapping_code]],
                left_on="symbol", right_on=self.internal_mapping_code,
                how="right",
            ).drop(columns=self.internal_mapping_code)

            df_list.append(df_merged)

        df_mapping = pd.concat(df_list)

        for symbol, intraday in product(df_mapping["symbol"].to_list(), [True, False]):
            date = self.earliest_date(symbol=symbol, intraday=intraday)
            
            col_name = self._earliest_date_column(intraday=intraday)
            if col_name not in df_mapping.columns:
                df_mapping[col_name] = None
            
            df_mapping.loc[df_mapping["symbol"] == symbol, col_name] = date

        return df_mapping

    def _default_start_and_end_date(
        self,
        df: pd.DataFrame,
        symbol: str,
        intraday: bool,
        **kwargs,
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        start_date = kwargs.get("start_date", self._check_start_date_for_security(symbol=symbol, intraday=intraday))
        end_date = kwargs.get("end_date", today_midnight())

        if start_date is None:
            raise TwelveDataException(f"Missing start_date mapping for {symbol}.")

        return start_date, end_date
