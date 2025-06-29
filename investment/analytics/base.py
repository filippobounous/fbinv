"""Common validation helper for analytics classes."""

from abc import abstractmethod
from typing import Callable, Any

from pandas import DataFrame, DatetimeIndex, Series

class _BaseAnalytics:
    """Shared input validation for analytics calculators."""

    @staticmethod
    @abstractmethod
    def registry() -> dict[str, Callable[..., Any]]:
        """Map method names to calculation functions."""

    @staticmethod
    def _validate(df: DataFrame) -> Series:
        """Validate input DataFrame and return simple returns series."""
        from .returns import ReturnsCalculator

        if df.empty:
            raise ValueError("Input DataFrame is empty.")
        if "close" not in df.columns:
            raise ValueError("DataFrame must contain a 'close' column.")
        if not isinstance(df.index, DatetimeIndex):
            raise ValueError("DataFrame index must be a DatetimeIndex.")

        ret_df = ReturnsCalculator(use_ln_ret=False, ret_win_size=1).calculate(df)
        return ret_df.set_index("as_of_date")["return"]
