from abc import abstractmethod
import datetime
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Optional

from ..core import Security
from private.consts.file_paths import HISTORICAL_DATA_PATH
from ..utils.consts import DATA_START_DATE

class BaseDataSource(BaseModel):
    name: str = "base"

    def get_timeseries(self, security: Security) -> None:
        df = self._read_ts_from_local(security=security)
        
        if min(df.as_of_date) < datetime.date.today() - datetime.timedelta(days=1):
            df_new = self._get_ts_from_remote(security=security)
            
            df = pd.concat([df, df_new]).reset_index(drop=True).set_index("as_of_date").drop_duplicates()
            
            self._write_ts_to_local(security=security, df=df)
        return df
    
    def _write_ts_to_local(self, security: Security, df: pd.DataFrame) -> None:
        df.to_csv(security.get_file_path(datasource_name=self.name), index=True)

    def _read_ts_from_local(self, security: Security) -> pd.DataFrame:
        df = pd.read_csv(security.get_file_path(datasource_name=self.name))
        return df.set_index("as_of_date")

    @property
    def historical_data_path(self) -> str:
        return f"{HISTORICAL_DATA_PATH}/{self.name}"

    @abstractmethod
    def _get_ts_from_remote(self, security: Security) -> pd.DataFrame:
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
            Dict[str, datetime.datetime]: Dictionary of file names and last modifided date.
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
    
    def update_all_securities(
        self,
        start_date: datetime.datetime = DATA_START_DATE,
        end_date: Optional[datetime.datetime] = None
    ) -> None:
        column = f"{self.name}_code"
