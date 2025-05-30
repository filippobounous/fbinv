"""Datasource that reads data from the local filesystem only."""

import datetime
from typing import Any, Dict, Union, List, TYPE_CHECKING, ClassVar

import pandas as pd

from .base import BaseDataSource
from ..config import PORTFOLIO_PATH, BASE_PATH
from ..utils.exceptions import DataSourceMethodException, SecurityMappingError

if TYPE_CHECKING:
    from ..core import Security
    from ..core.mapping import BaseMappingEntity
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund
    from ..core import Portfolio

class LocalDataSource(BaseDataSource):
    """Datasource that serves data already available locally."""

    name: ClassVar[str] = "local"

    @property
    def portfolio_mapping(self) -> pd.DataFrame:
        """Return the portfolio mapping table."""

        return pd.read_csv(f"{BASE_PATH}/portfolio_mapping.csv")

    @property
    def reporting_currency(self) -> pd.DataFrame:
        """DataFrame mapping securities to their reporting currency."""

        return pd.read_csv(f"{BASE_PATH}/reporting_currency.csv")

    def _get_currency_cross_price_history_from_remote(
        self,
        security: 'CurrencyCross', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")

    def _get_equity_price_history_from_remote(
        self,
        security: 'Equity', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")

    def _get_etf_price_history_from_remote(
        self,
        security: 'ETF', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")

    def _get_fund_price_history_from_remote(
        self,
        security: 'Fund', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote series for {self.name} datasource for {security.code}.")
    
    @staticmethod
    def _format_price_history_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        """Return ``df`` unchanged as no remote calls are made."""

        return df

    def load_portfolio(self, portfolio: "Portfolio") -> Dict[str, Any]:
        """Load a portfolio's details from CSV."""
        df = self.portfolio_mapping
        row = df.loc[df.code == portfolio.code]

        return self._load(df=row, entity=portfolio)

    def load_security(self, security: "Security") -> Dict[str, Any]:
        """Load a security's details from CSV and apply multipliers."""
        df = self.get_security_mapping()
        df_reporting_ccy = self.reporting_currency

        # set multiplier
        df = df.merge(df_reporting_ccy, how="left", on=["reporting_currency", "currency"])
        mask = (df["reporting_currency"] == df["currency"]) & (df["multiplier"].isna())
        df.loc[mask, "multiplier"] = 1.0

        row = df.loc[df.code == security.code]

        return self._load(df=row, entity=security)
    
    def load_composite(self, composite: "Composite") -> Dict[str, Any]:
        """Placeholder for loading composite securities."""
        pass

    @staticmethod
    def _load(df: pd.DataFrame, entity: "BaseMappingEntity") -> Dict[str, Any]:
        """Convert a single-row DataFrame to a mapping dictionary."""
        if len(df) > 1:
            raise SecurityMappingError(f"Duplicate {entity.entity_type} for code '{entity.code}'")
        if len(df) == 0:
            raise SecurityMappingError(f"No {entity.entity_type} for code '{entity.code}'")

        di = df.iloc[0].to_dict()
        return {k: v for k, v in di.items() if not pd.isna(v)}

    def get_all_portfolios(
        self, as_instance: bool = False
    ) -> Union[Dict[str, datetime.datetime], List["Portfolio"]]:
        """
        Get all available portfolios with last modified date.
        
        Args:
            as_instance (bool): If True then returns a list of Portfolio classes.

        Returns:
            Union[Dict[str, datetime.datetime], List[Portfolio]]:Dictionary of file names
            and last modified date or List of Portfolios
        """
        from ..core import Portfolio

        di = self._get_file_names_in_path(path=PORTFOLIO_PATH)
        if as_instance:
            return [Portfolio(name) for name, _ in di.items()]
        return di

    def get_all_securities(self, column: str = "code", as_instance: bool = False) -> List[Union[str, "Security"]]:
        """Return all available securities either as codes or instances."""
        from ..core.security.registry import security_registry

        li = []

        df = self.get_security_mapping()
        
        if as_instance:
            for _, row in df.iterrows():
                code = row.get(column)
                entity_type = row.get("type")

                obj  = security_registry.get(entity_type)

                if obj:
                    li.append(obj(code))
        else:
            li = df[column].to_list()
        
        return li

    def _update_security_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        raise DataSourceMethodException(f"No remote security mapping for {self.name} datasource.")
