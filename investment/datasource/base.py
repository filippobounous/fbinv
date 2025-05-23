from abc import abstractmethod
import datetime
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Optional

from ..config import HISTORICAL_DATA_PATH
from ..core import Security
from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

class BaseDataSource(BaseModel):
    name: str = "base"

    def get_timeseries(self, security: Security, intraday: bool = False) -> pd.DataFrame:
        df = self._read_ts_from_local(security=security, intraday=intraday)
        
        if df.empty or (min(df.as_of_date) < datetime.date.today() - datetime.timedelta(days=1)):
            df_new = self._get_ts_from_remote(security=security, intraday=intraday)
            
            df = pd.concat([df, df_new]).reset_index(drop=True).set_index("as_of_date").drop_duplicates()
            
            self._write_ts_to_local(security=security, df=df, intraday=intraday)
        return df
    
    def _write_ts_to_local(self, security: Security, df: pd.DataFrame, intraday: bool) -> None:
        df.to_csv(security.get_file_path(datasource_name=self.name, intraday=intraday), index=True)

    def _read_ts_from_local(self, security: Security, intraday: bool) -> pd.DataFrame:
        file_path = Path(security.get_file_path(datasource_name=self.name, intraday=intraday))
        if not file_path.exists():
            return pd.DataFrame() # or return None if preferred
        df = pd.read_csv(file_path)
        return df.set_index("as_of_date")

    @property
    def historical_data_path(self) -> str:
        return f"{HISTORICAL_DATA_PATH}/{self.name}"

    def _get_ts_from_remote(self, security: Security, intraday: bool = False) -> pd.DataFrame:
        ts_method_dict = {
            "currency_cross": self._get_currency_cross_ts_from_remote,
            "equity": self._get_equity_ts_from_remote,
            "etf": self._get_etf_ts_from_remote,
            "fund": self._get_fund_ts_from_remote,
        }

        ts_method = ts_method_dict.get(security.entity_type)

        if ts_method is None:
            raise KeyError(f"Entity type '{security.entity_type}' has not been configured.")
        else:
            df = ts_method(security=security, intraday=intraday)
            return self._format_ts_from_remote(df)
    
    @abstractmethod
    def _get_currency_cross_ts_from_remote(self, security: CurrencyCross, intraday: bool) -> pd.DataFrame:
        pass

    @abstractmethod
    def _get_equity_ts_from_remote(self, security: Equity, intraday: bool) -> pd.DataFrame:
        pass

    @abstractmethod
    def _get_etf_ts_from_remote(self, security: ETF, intraday: bool) -> pd.DataFrame:
        pass

    @abstractmethod
    def _get_fund_ts_from_remote(self, security: Fund, intraday: bool) -> pd.DataFrame:
        pass

    @staticmethod
    @abstractmethod
    def _format_ts_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        pass

    def get_all_available_data_files(self) -> Dict[str, datetime.datetime]:
        """
        Get file names from path with last modified dates for historical data.

        Returns:
            Dict[str, datetime.datetime]: Dictionary of file names and last modified date.
        """
        return self._get_file_names_in_path(path=self.historical_data_path)
    
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
    
    def update_all_securities(self, intraday: bool = False) -> Dict[str, bool]:
        from .local import LocalDataSource
        li = LocalDataSource().get_all_available_securities(as_instance=True)

        for security in li:
            try:
                self.get_timeseries(security=security, intraday=intraday)
            except Exception as e:
                print(f"Failure for {security.code} by {e}")