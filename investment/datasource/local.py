"""Data source for reading local CSV files."""

import datetime
from typing import Any, Dict, Union, List, TYPE_CHECKING, ClassVar, Optional

import pandas as pd

from .base import BaseDataSource
from ..config import PORTFOLIO_PATH, BASE_PATH
from ..utils.exceptions import DataSourceMethodException, SecurityMappingError

if TYPE_CHECKING:
    from ..core.mapping import BaseMappingEntity
    from ..core.portfolio import Portfolio
    from ..core.security.registry import Composite, CurrencyCross, Equity, ETF, Fund, BaseSecurity

class LocalDataSource(BaseDataSource):
    """Data source that reads from local CSV files only."""

    name: ClassVar[str] = "local"

    @property
    def portfolio_mapping(self) -> pd.DataFrame:
        """Return portfolio mapping table from disk."""
        return pd.read_csv(f"{BASE_PATH}/portfolio_mapping.csv")

    @property
    def reporting_currency(self) -> pd.DataFrame:
        """Return reporting currency reference table."""
        return pd.read_csv(f"{BASE_PATH}/reporting_currency.csv")

    def _get_currency_cross_price_history_from_remote(
        self,
        security: 'CurrencyCross', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Local source has no remote FX data."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_equity_price_history_from_remote(
        self,
        security: 'Equity', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Local source has no remote equity data."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_etf_price_history_from_remote(
        self,
        security: 'ETF', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Local source has no remote ETF data."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_fund_price_history_from_remote(
        self,
        security: 'Fund', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Local source has no remote fund data."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    @staticmethod
    def _format_price_history_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        """Return the DataFrame unchanged."""
        return df

    def load_portfolio(self, portfolio: "Portfolio") -> Dict[str, Any]:
        """Load a portfolio from the CSV file."""
        df = self.portfolio_mapping
        row = df.loc[df.code == portfolio.code]

        return self._load(df=row, entity=portfolio)

    def load_security(self, security: "BaseSecurity") -> Dict[str, Any]:
        """Load a security from the CSV file."""
        df = self.get_security_mapping()
        df_reporting_ccy = self.reporting_currency

        # set multiplier
        df = df.merge(df_reporting_ccy, how="left", on=["reporting_currency", "currency"])
        mask = (df["reporting_currency"] == df["currency"]) & (df["multiplier"].isna())
        df.loc[mask, "multiplier"] = 1.0

        row = df.loc[df.code == security.code]

        return self._load(df=row, entity=security)

    def load_composite_security(self, composite: "Composite") -> Dict[str, Any]:
        """Return attributes for a composite security."""
        di = composite.security.model_dump()
        di.pop("code") # remove code as not needed

        di["currency"] = composite.currency_cross.currency

        return di
    
    def load_generic_security(self, **kwargs) -> "BaseSecurity":
        """Instantiate a security based on mapping information."""
        from ..core.security.registry import security_registry
        
        df = self.get_security_mapping()
        row = df[df.code == kwargs["code"]]
        entity_type = self._load(df=row).get("type")
        
        entity = security_registry.get(entity_type)
        
        return entity(**kwargs)
        
    @staticmethod
    def _load(df: pd.DataFrame, entity: Optional["BaseMappingEntity"] = None) -> Dict[str, Any]:
        """Convert a single CSV row to a dictionary."""
        if len(df) > 1:
            raise SecurityMappingError(f"Duplicate {entity.entity_type} for code '{entity.code}'" if entity else "Duplicate data.")
        if len(df) == 0:
            raise SecurityMappingError(f"No {entity.entity_type} for code '{entity.code}'" if entity else "Missing data.")

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
        from ..core.portfolio import Portfolio

        di = self._get_file_names_in_path(path=PORTFOLIO_PATH)
        if as_instance:
            return [Portfolio(name) for name, _ in di.items()]
        return di

    def get_all_securities(
        self, column: str = "code", as_instance: bool = False
    ) -> List[Union[str, "BaseSecurity"]]:
        """List all available securities."""
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
        """Local source has no remote mapping update."""
        raise DataSourceMethodException(f"No remote security mapping for {self.name} datasource.")
