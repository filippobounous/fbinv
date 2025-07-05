"""Simple local data source used for testing."""

import datetime
from typing import TYPE_CHECKING, ClassVar, Any

import pandas as pd

from .base import BaseDataSource
from ..core.security import CurrencyCross
from ..utils.exceptions import DataSourceMethodException

if TYPE_CHECKING:
    from ..core.portfolio import Portfolio
    from ..core.security import ETF, Equity, Fund, Composite, BaseSecurity

class TestDataSource(BaseDataSource):
    """Very small data source used for tests only."""

    name: ClassVar[str] = "test"
    __test__ = False  # avoid pytest treating this as a test class

    def _get_currency_cross_price_history_from_remote(
        self,
        security: 'CurrencyCross', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Test source has no remote data."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_equity_price_history_from_remote(
        self,
        security: 'Equity', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Test source has no remote data."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_etf_price_history_from_remote(
        self,
        security: 'ETF', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Test source has no remote data."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_fund_price_history_from_remote(
        self,
        security: 'Fund', intraday: bool,
        start_date: datetime.datetime, end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Test source has no remote data."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    @staticmethod
    def _format_price_history_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        """Return the DataFrame unchanged."""
        return df

    def _update_security_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Test mapping is not implemented."""
        raise DataSourceMethodException(
            f"No remote security mapping for {self.name} datasource."
        )

    # --- methods for test mapping -------------------------------------------------
    def load_security(self, security: "BaseSecurity") -> dict[str, Any]:
        """Return dummy attributes for any security."""
        di = {
            "name": "dummy",
            "figi_code": "FIGI",
            "reporting_currency": "USD",
            "currency": "USD",
            "financial_times_code": "ft",
            "financial_times_security_type": "stock",
            "bloomberg_code": "bb",
            "yahoo_finance_code": "yf",
            "twelve_data_code": "td",
            "alpha_vantage_code": "av",
            "multiplier": 1.0,
            "isin_code": "isin",
        }

        if isinstance(security, CurrencyCross):
            di["currency_vs"] = security.code[3:]

        return di

    def load_composite_security(self, composite: "Composite") -> dict[str, Any]:
        """Load attributes for a composite security."""
        di = self.load_security(composite.security)
        di["currency"] = composite.currency_cross.currency
        return di

    # placeholder loaders so BaseMappingEntity initialisation succeeds
    def load_portfolio(self, portfolio: "Portfolio") -> dict[str, Any]:
        """Return dummy portfolio attributes."""
        return {}

    def load_generic_security(self, **kwargs) -> "BaseSecurity":
        """Return a generic BaseSecurity instance for tests."""
        from ..core.security.base import BaseSecurity

        class DummySecurity(BaseSecurity):
            """Dummy security class for testing purposes."""
            entity_type: str = "dummy"

            def get_price_history(self, *args, **kwargs) -> pd.DataFrame:
                return pd.DataFrame()

        return DummySecurity(**kwargs)  # type: ignore[arg-type]
