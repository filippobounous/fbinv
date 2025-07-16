"""Common validation helper for analytics classes."""

from abc import abstractmethod
from typing import Any, Callable

from pandas import DataFrame, DatetimeIndex, Series


class BaseAnalytics:
    """Shared input validation for analytics calculators."""

    @staticmethod
    @abstractmethod
    def registry() -> dict[str, Callable[..., Any]]:
        """Map method names to calculation functions."""

    @staticmethod
    def _validate(df: DataFrame) -> Series:
        """Validate input DataFrame and return simple returns series."""

        if df.empty:
            raise ValueError("Input DataFrame is empty.")
        if "close" not in df.columns:
            raise ValueError("DataFrame must contain a 'close' column.")
        if not isinstance(df.index, DatetimeIndex):
            raise ValueError("DataFrame index must be a DatetimeIndex.")

        returns = df.sort_index()["close"].pct_change().dropna()
        returns.index.name = "as_of_date"
        return returns


__all__ = [
    "BaseAnalytics",
]
