from pathlib import Path
from typing import Dict, Optional, ClassVar, TYPE_CHECKING, Tuple

from ..config import TIMESERIES_DATA_PATH, BASE_PATH
from abc import abstractmethod
import datetime
import os
import pandas as pd
from pydantic import BaseModel
from tqdm import tqdm

from ..utils.consts import DATA_START_DATE
from ..utils.date_utils import today_midnight
from ..utils.exceptions import DataSourceMethodException, AlphaVantageException, TwelveDataException
from ..utils.warnings import warnings

if TYPE_CHECKING:
    from ..core.security import BaseSecurity
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

class BaseDataSource(BaseModel):
    """Abstract interface for retrieving and caching data."""

    name: ClassVar[str] = "base"
    data_start_date: datetime.datetime = DATA_START_DATE

    @property
    def internal_mapping_code(self) -> str:
        """Column name for this source's security codes."""
        return f"{self.name}_code"

    @property
    def timeseries_data_path(self) -> str:
        """Directory for cached time series."""
        return f"{TIMESERIES_DATA_PATH}/{self.name}"
    
    @property
    def security_mapping_path(self) -> str:
        """CSV file containing this source's security mapping."""
        return f"{BASE_PATH}/security_mapping-{self.name}.csv"

    def get_security_mapping(self) -> pd.DataFrame:
        """Load the mapping file from disk."""
        return pd.read_csv(self.security_mapping_path)

    def get_price_history(self, security: "BaseSecurity", intraday: bool = False, local_only: bool = False, **kwargs) -> pd.DataFrame:
        """Return merged local and remote price history for a security."""
        if intraday:
            raise DataSourceMethodException(f"Intraday not currently supported. Should not be used.")
        
        df_local = self._read_timeseries_from_local(security=security, intraday=intraday, series_type="price_history")
        
        if not local_only:
            df_remote = self._load_price_history_from_remote(security=security, intraday=intraday, df=df_local, **kwargs)
        else:
            df_remote = pd.DataFrame()
        
        if not df_remote.empty:
            df = pd.concat([df_remote, df_local])
            if df.empty:
                return df
            
            df = df
        else:
            df = df_local
        
        if not df.empty:
            df = df.reset_index(drop=True).set_index("as_of_date").sort_index().drop_duplicates()
        
            self._write_timeseries_to_local(security=security, df=df, intraday=intraday, series_type="price_history")
            
        return df
    
    def _write_timeseries_to_local(self, security: "BaseSecurity", df: pd.DataFrame, intraday: bool, series_type: str) -> None:
        """Persist a time series to disk."""
        file_path = security.get_file_path(datasource_name=self.name, intraday=intraday, series_type=series_type)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=True)

    def _read_timeseries_from_local(self, security: "BaseSecurity", intraday: bool, series_type: str) -> pd.DataFrame:
        """Load a cached time series if available."""
        file_path = Path(security.get_file_path(datasource_name=self.name, intraday=intraday, series_type=series_type))
        if not file_path.exists():
            return pd.DataFrame() # or return None if preferred
        df = pd.read_csv(file_path, parse_dates=["as_of_date"])
        return df
    
    def _load_price_history_from_remote(self, security: "BaseSecurity", intraday: bool, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Fetch missing periods of price history from the remote API."""
        df_to_concat = []

        symbol = getattr(security, self.internal_mapping_code, None)
        if symbol is None:
            warnings.warn(f"Mising internal code for {self.name} datasource for {security.code}")
            return df
        
        try:
            start_date, end_date = self._default_start_and_end_date(
                df=df,
                symbol=symbol,
                intraday=intraday,
                **kwargs,
            )

            empty = df.empty
            lower_bound_missing = None if empty else (min(df["as_of_date"]) > start_date)
            upper_bound_missing = None if empty else (max(df["as_of_date"]) < end_date)

            if empty:
                df_to_concat.append(self._get_price_history_from_remote(
                    security=security, intraday=intraday,
                    start_date=start_date, end_date=end_date
                ))
            
            elif lower_bound_missing or upper_bound_missing:
                df_to_concat = []
                
                if lower_bound_missing:
                    df_to_concat.append(self._get_price_history_from_remote(
                        security=security, intraday=intraday,
                        start_date=start_date,
                        end_date=min(df["as_of_date"]),
                    ))
                
                if upper_bound_missing:
                    df_to_concat.append(self._get_price_history_from_remote(
                        security=security, intraday=intraday,
                        start_date=max(df["as_of_date"]),
                        end_date=end_date,
                    ))

        except DataSourceMethodException:
            warnings.warn(f"No remote series for {self.name} datasource for {security.code}.")

        except (AlphaVantageException, TwelveDataException) as e:
            warnings.warn(f"Unable to retrieve remote series for {self.name} datasource for {security.code}: {e}")

        return pd.concat(df_to_concat) if df_to_concat else pd.DataFrame()

    def _get_price_history_from_remote(
        self,
        security: "BaseSecurity", intraday: bool = False,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
    ) -> pd.DataFrame:
        """Dispatch to the correct remote retrieval method."""
        ts_method_dict = {
            "currency_cross": self._get_currency_cross_price_history_from_remote,
            "equity": self._get_equity_price_history_from_remote,
            "etf": self._get_etf_price_history_from_remote,
            "fund": self._get_fund_price_history_from_remote,
        }

        ts_method = ts_method_dict.get(security.entity_type)

        if ts_method is None:
            raise KeyError(f"Entity type '{security.entity_type}' has not been configured.")
        else:
            df = ts_method(
                security=security, intraday=intraday,
                start_date=start_date, end_date=end_date,
            )
            return self._format_price_history_from_remote(df)
    
    @abstractmethod
    def _get_currency_cross_price_history_from_remote(
        self,
        security: "CurrencyCross", intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Retrieve FX price history from the remote service."""
        pass

    @abstractmethod
    def _get_equity_price_history_from_remote(
        self,
        security: "Equity", intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Retrieve equity price history from the remote service."""
        pass

    @abstractmethod
    def _get_etf_price_history_from_remote(
        self,
        security: "ETF", intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Retrieve ETF price history from the remote service."""
        pass

    @abstractmethod
    def _get_fund_price_history_from_remote(
        self,
        security: "Fund", intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Retrieve fund price history from the remote service."""
        pass

    @staticmethod
    @abstractmethod
    def _format_price_history_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        """Normalise the remote DataFrame format."""
        pass

    def _default_start_and_end_date(
        self,
        df: pd.DataFrame,
        symbol: str,
        intraday: bool,
        **kwargs,
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        """Fallback implementation for determining update ranges."""
        start_date = kwargs.get("start_date", self.data_start_date)
        end_date = kwargs.get("end_date", today_midnight() + datetime.timedelta(days=-1))
        return start_date, end_date
    
    @staticmethod
    def _get_file_names_in_path(path: str) -> Dict[str, datetime.datetime]:
        """
        Get file names from path with last modified dates.

        Args:
            path (str): path_name

        Returns:
            Dict[str, datetime.datetime]: Dictionary of file names and last modified date.
        """
        
        folder = Path(path)
        
        di = {}
        for file_path in folder.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'): # skips hidden files
                # Name without extension
                file_stem = file_path.stem

                # Last modified datetime
                last_modified_timestamp = file_path.stat().st_mtime
                last_modified_datetime = datetime.datetime.fromtimestamp(last_modified_timestamp)
                
                di[file_stem] = last_modified_datetime

        return di
    
    def update_price_histories(self, intraday: bool = False, **kwargs) -> Dict[str, bool]:
        """Update price histories for all known securities."""
        from .local import LocalDataSource
        li = LocalDataSource().get_all_securities(as_instance=True)

        di = {}
        for security in tqdm(li, desc=f"Updating securities for {self.name}"):
            df = self.get_price_history(security=security, intraday=intraday, **kwargs)
            
            di[security.code] = not df.empty

        return di
    
    @abstractmethod
    def _update_security_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return an updated security mapping DataFrame."""
        pass
    
    def update_security_mapping(self) -> pd.DataFrame:
        """Update the local mapping file using the remote API."""
        from .registry import LocalDataSource
        try:
            df = LocalDataSource().get_security_mapping()
            df = self._update_security_mapping(df=df)
            df.to_csv(self.security_mapping_path, index=False)

        except DataSourceMethodException:
            df = pd.DataFrame()
            warnings.warn(f"No remote security mapping for {self.name} datasource.")

        return df

    def full_update(self, start_date: Optional[datetime.datetime] = None, intraday: bool = False) -> Dict[str, bool]:
        """Update security mapping and all price histories."""
        from .local import LocalDataSource

        df_mapping = self.update_security_mapping()
        di = self.update_price_histories(start_date=start_date, intraday=intraday)
        
        li = LocalDataSource().get_all_securities(as_instance=True)

        if len(df_mapping) == len(li):
            di["security_mapping"] = True
        else:
            di["security_mapping"] = False

        return di
