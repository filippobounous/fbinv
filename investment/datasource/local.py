import datetime
import pandas as pd
from typing import Any, Dict, Union, List, TYPE_CHECKING, ClassVar

from .base import BaseDataSource
from ..config import PORTFOLIO_PATH, BASE_PATH
from ..core import Portfolio
from ..core.security.registry import security_registry

if TYPE_CHECKING:
    from ..core import Security
    from ..core.mapping import BaseMappingEntity
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

class LocalDataSource(BaseDataSource):
    name: ClassVar[str] = "local"

    def _get_currency_cross_ts_from_remote(
        self,
        security: 'CurrencyCross', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")

    def _get_equity_ts_from_remote(
        self,
        security: 'Equity', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")

    def _get_etf_ts_from_remote(
        self,
        security: 'ETF', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")

    def _get_fund_ts_from_remote(
        self,
        security: 'Fund', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise NotImplementedError(f"No remote source for {self.name} datasource.")
    
    @staticmethod
    def _format_ts_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError(f"Not implemented.")

    def load_portfolio(self, portfolio: "Portfolio") -> Dict[str, Any]:
        """
        Load a portfolio from the csv file.
        """
        df = self._portfolio_mapping()
        row = df.loc[df.code == portfolio.code]

        return self._load(df=row, entity=portfolio)

    def load_security(self, security: "Security") -> Dict[str, Any]:
        """
        Load a security from the csv file.
        """
        df = self._security_mapping()
        df_reporting_ccy = self._reporting_currency()

        # set multiplier
        df = df.merge(df_reporting_ccy, how="left", on=["reporting_currency", "currency"])
        mask = (df["reporting_currency"] == df["currency"]) & (df["multiplier"].isna())
        df.loc[mask, "multiplier"] = 1.0

        row = df.loc[df.code == security.code]

        return self._load(df=row, entity=security)
    
    @staticmethod
    def _load(df: pd.DataFrame, entity: "BaseMappingEntity") -> Dict[str, Any]:
        if len(df) > 1:
            raise ValueError(f"Duplicate {entity.entity_type} for code '{entity.code}'.")
        elif len(df) == 0:
            raise ValueError(f"No {entity.entity_type} for code '{entity.code}'.")
        else:
            di = df.iloc[0].to_dict()
            return {k: v for k, v in di.items() if not pd.isna(v)}

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
    
    @staticmethod
    def _security_mapping() -> pd.DataFrame:
        return pd.read_csv(f"{BASE_PATH}/security_mapping.csv")

    @staticmethod
    def _portfolio_mapping() -> pd.DataFrame:
        return pd.read_csv(f"{BASE_PATH}/portfolio_mapping.csv")

    @staticmethod
    def _reporting_currency() -> pd.DataFrame:
        return pd.read_csv(f"{BASE_PATH}/reporting_currency.csv")
        
    def get_all_available_securities(self, as_instance: bool = False) -> List[Union[str, "Security"]]:
        """
        List all available securities.
        """
        li = []

        df = self._security_mapping()
        
        if as_instance:
            for _, row in df.iterrows():
                code = row.get("code")
                entity_type = row.get("type")

                obj  = security_registry.get(entity_type)

                if obj:
                    li.append(obj(code))
        else:
            li = df["code"].to_list()
        
        return li
