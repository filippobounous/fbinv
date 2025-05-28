from abc import abstractmethod
import datetime
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from tqdm import tqdm
from typing import Dict, Optional, ClassVar, TYPE_CHECKING, Tuple

from ..config import HISTORICAL_DATA_PATH, BASE_PATH
from ..utils.consts import DATA_START_DATE
from ..utils.date_utils import today_midnight
from ..utils.exceptions import DataSourceMethodException
from ..utils.warnings import warnings

if TYPE_CHECKING:
    from ..core import Security
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

class BaseDataSource(BaseModel):
    name: ClassVar[str] = "base"
    data_start_date: datetime.datetime = DATA_START_DATE

    @property
    def internal_mapping_code(self) -> str:
        return f"{self.name}_code"

    @property
    def historical_data_path(self) -> str:
        return f"{HISTORICAL_DATA_PATH}/{self.name}"
    
    @property
    def _security_mapping_path(self) -> str:
        return f"{BASE_PATH}/security_mapping_{self.name}.csv"

    def _security_mapping(self) -> pd.DataFrame:
        return pd.read_csv(self._security_mapping_path)

    def get_timeseries(self, security: "Security", intraday: bool = False, **kwargs) -> pd.DataFrame:
        if intraday:
            raise DataSourceMethodException(f"Intraday not currently supported. Should not be used.")
        
        df = self._read_ts_from_local(security=security, intraday=intraday)

        start_date, end_date = self._default_start_and_end_date(
            df=df,
            symbol=self.internal_mapping_code,
            intraday=intraday,
            **kwargs,
        )

        empty = df.empty
        lower_bound_missing = None if empty else (min(df["as_of_date"]) > start_date)
        upper_bound_missing = None if empty else (max(df["as_of_date"]) < end_date)

        try:
            df_to_concat = []
            if empty:
                df_to_concat.append(self._get_ts_from_remote(
                    security=security, intraday=intraday,
                    start_date=start_date, end_date=end_date
                ))
            
            elif lower_bound_missing or upper_bound_missing:
                df_to_concat = []
                
                if lower_bound_missing:
                    df_to_concat.append(self._get_ts_from_remote(
                        security=security, intraday=intraday,
                        start_date=start_date,
                        end_date=min(df["as_of_date"]),
                    ))
                
                if upper_bound_missing:
                    df_to_concat.append(self._get_ts_from_remote(
                        security=security, intraday=intraday,
                        start_date=max(df["as_of_date"]),
                        end_date=end_date,
                    ))

        except DataSourceMethodException:
            warnings.warn(f"No remote series for {self.name} datasource for {security.code}.")
        
        except Exception as e:
            warnings.warn(f"""
            Exception for {self.name} datasource for {security.code} as "{e}" for params:
            start_date({start_date}), end_date({end_date}), intraday({intraday}),
            empty({empty}), lower_bound_missing({lower_bound_missing}), upper_bound_missing({upper_bound_missing}),
            """)
        
        if df_to_concat:
            df_to_concat.append(df)
            df = pd.concat(df_to_concat)
            if df.empty:
                return df
            
            df = df.reset_index(drop=True).set_index("as_of_date").sort_index().drop_duplicates()
            self._write_ts_to_local(security=security, df=df, intraday=intraday)
            
        return df

    def _read_ts_from_local(self, security: "Security", intraday: bool) -> pd.DataFrame:
        file_path = Path(security.get_file_path(datasource_name=self.name, intraday=intraday))
        if not file_path.exists():
            return pd.DataFrame() # or return None if preferred
        df = pd.read_csv(file_path, parse_dates=["as_of_date"])

        import pdb; pdb.set_trace()
        return df

    def _get_ts_from_remote(
        self,
        security: "Security", intraday: bool = False,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
    ) -> pd.DataFrame:
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
            df = ts_method(
                security=security, intraday=intraday,
                start_date=start_date, end_date=end_date,
            )
            return self._format_ts_from_remote(df)
    
    @abstractmethod
    def _get_currency_cross_ts_from_remote(self, security: "CurrencyCross", intraday: bool) -> pd.DataFrame:
        pass

    @abstractmethod
    def _get_equity_ts_from_remote(self, security: "Equity", intraday: bool) -> pd.DataFrame:
        pass

    @abstractmethod
    def _get_etf_ts_from_remote(self, security: "ETF", intraday: bool) -> pd.DataFrame:
        pass

    @abstractmethod
    def _get_fund_ts_from_remote(self, security: "Fund", intraday: bool) -> pd.DataFrame:
        pass

    @staticmethod
    @abstractmethod
    def _format_ts_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        pass

    def _default_start_and_end_date(
        self,
        df: pd.DataFrame,
        symbol: str,
        intraday: bool,
        **kwargs,
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        start_date = kwargs.get("start_date", self.data_start_date)
        end_date = kwargs.get("end_date", today_midnight() + datetime.timedelta(days=-1))
        return start_date, end_date
    
    def _write_ts_to_local(self, security: "Security", df: pd.DataFrame, intraday: bool) -> None:
        df.to_csv(security.get_file_path(datasource_name=self.name, intraday=intraday), index=True)

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
    
    def update_all_securities(self, intraday: bool = False, **kwargs) -> Dict[str, bool]:
        from .local import LocalDataSource
        li = LocalDataSource().get_all_available_securities(as_instance=True)

        di = {}
        for security in tqdm(li, desc=f"Updating securities for {self.name}"):
            df = self.get_timeseries(security=security, intraday=intraday, **kwargs)
            
            di[security.code] = not df.empty

        return di
    
    @abstractmethod
    def _update_security_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
    
    def update_security_mappings(self) -> pd.DataFrame:
        from .registry import LocalDataSource
        try:
            df = LocalDataSource()._security_mapping()
            df = self._update_security_mapping(df=df)
            df.to_csv(self._security_mapping_path, index=False)

        except DataSourceMethodException:
            df = pd.DataFrame()
            warnings.warn(f"No remote security mapping for {self.name} datasource.")

        except Exception as e:
            warnings.warn(f"""
            Exception for {self.name} datasource as "{e}" while updating security mappings
            """)

        return df

    def full_update(self, intraday: bool = False) -> Dict[str, bool]:
        from .local import LocalDataSource

        df_mapping = self.update_security_mappings()
        di = self.update_all_securities(intraday=intraday)
        
        li = LocalDataSource().get_all_available_securities(as_instance=True)

        if len(df_mapping) == len(li):
            di["security_mapping"] = True
        else:
            di["security_mapping"] = False

        return di
