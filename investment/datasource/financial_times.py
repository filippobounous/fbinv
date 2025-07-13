"""Local placeholder for Financial Times data source."""  # TODO

import datetime
from typing import TYPE_CHECKING, ClassVar

import pandas as pd

from ..utils.exceptions import DataSourceMethodException
from .base import BaseDataSource

if TYPE_CHECKING:
    from ..core.security.registry import ETF, CurrencyCross, Equity, Fund


class FinancialTimesDataSource(BaseDataSource):
    """Placeholder data source for the Financial Times service."""

    name: ClassVar[str] = "financial_times"

    def _get_currency_cross_price_history_from_remote(
        self,
        security: "CurrencyCross",
        intraday: bool,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Financial Times remote data is not implemented."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_equity_price_history_from_remote(
        self,
        security: "Equity",
        intraday: bool,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Financial Times remote data is not implemented."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_etf_price_history_from_remote(
        self,
        security: "ETF",
        intraday: bool,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Financial Times remote data is not implemented."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    def _get_fund_price_history_from_remote(
        self,
        security: "Fund",
        intraday: bool,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> pd.DataFrame:
        """Financial Times remote data is not implemented."""
        raise DataSourceMethodException(
            f"No remote series for {self.name} datasource for {security.code}."
        )

    @staticmethod
    def _format_price_history_from_remote(df: pd.DataFrame) -> pd.DataFrame:
        """Return the input DataFrame unchanged."""
        return df

    def _update_security_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Financial Times mapping is not implemented."""
        raise DataSourceMethodException(
            f"No remote security mapping for {self.name} datasource."
        )


__all__ = [
    "FinancialTimesDataSource",
]
