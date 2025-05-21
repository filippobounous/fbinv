import datetime
import pandas as pd
from typing import Any, Dict, Union, List, TYPE_CHECKING

from .base import BaseDataSource
from ..core import Portfolio
from private.consts.file_paths import PORTFOLIO_PATH, BASE_PATH

if TYPE_CHECKING:
    from ..core import Security, BaseMappingEntity

class LocalDataSource(BaseDataSource):
    name: str = "local"

    def _get_ts_from_remote(self, security: "Security") -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")

    @staticmethod
    def load_portfolio(portfolio: "Portfolio") -> Dict[str, Any]:
        """
        Load a portfolio from the csv file.
        """
        df = pd.read_csv(f"{BASE_PATH}/portfolio_mapping.csv")
        row = df.loc[df.code == portfolio.code]

        return LocalDataSource._load(df=row, entity=portfolio)

    @staticmethod
    def load_security(security: "Security") -> Dict[str, Any]:
        """
        Load a portfolio from the csv file.
        """
        df = pd.read_csv(f"{BASE_PATH}/security_mapping.csv")
        row = df.loc[df.code == security.code]

        return LocalDataSource._load(df=row, entity=security)
        
    def _load(df: pd.DataFrame, entity: "BaseMappingEntity") -> Dict[str, Any]:
        if len(df) > 1:
            raise ValueError(f"Duplicate {entity.entity_type} for code '{entity.code}'.")
        elif len(df) == 0:
            raise ValueError(f"No {entity.entity_type} for code '{entity.code}'.")
        else:
            return df.iloc[0].to_dict()

    def get_all_available_portfolios(self, as_instance: bool = False) -> Union[Dict[str, datetime.datetime], List[Portfolio]]:
        """
        Get all available portfolios with last modified date.
        
        Args:
            as_instance (bool): If True then returns a list of Portfolio classes.

        Returns:
            Union[Dict[str, datetime.datetime], List[Portfolio]]: Dictionary of file names and last modified date
            or List of Portfolios
        """
        di = self._get_file_names_in_path(path=PORTFOLIO_PATH)
        if as_instance:
            return [Portfolio(name) for name, _ in di.items()]
        else:
            return di