"""Simple local data source used for testing."""

import datetime
from typing import TYPE_CHECKING, ClassVar

import pandas as pd

from .base import BaseDataSource
from ..utils.exceptions import DataSourceMethodException

if TYPE_CHECKING:
    from ..core.security.registry import CurrencyCross, Equity, ETF, Fund

class TestDataSource(BaseDataSource):
    """Very small data source used for tests only."""

    name: ClassVar[str] = "test"

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
