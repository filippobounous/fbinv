"""Value-at-Risk analytics for assessing downside risk.

This module provides the :class:`VaRCalculator` class which exposes a few
commonly used approaches for estimating Value-at-Risk (VaR). All calculations
operate on a price history ``pandas.DataFrame`` validated by ``_BaseAnalytics``
and converted to simple returns.
"""

from statistics import NormalDist
from typing import Callable

import pandas as pd

from .base import BaseAnalytics
from ..utils.consts import DEFAULT_CONFIDENCE_LEVEL, DEFAULT_VAR_WIN_SIZE

# TODO: rolling window with win_size instead of setting as single value
# TODO: implement correlation for portfolio
# TODO: rethink how this is used in the context of portfolio etc, perhaps should be done similarly
# to correlation page

class VaRCalculator(BaseAnalytics):
    """Value-at-Risk related calculations."""

    @staticmethod
    def registry() -> dict[str, Callable[..., pd.DataFrame]]:
        """Map method names to VaR calculation functions."""
        return {
            "historical": VaRCalculator.historical_var,
            "parametric": VaRCalculator.parametric_var,
            "conditional": VaRCalculator.conditional_var,
        }

    @staticmethod
    def _apply_window(
        series: pd.Series,
        func: Callable[[pd.Series], float],
        var_win_size: int,
    ) -> pd.Series:
        """Apply ``func`` over a mandatory rolling ``var_win_size``."""

        result = series.rolling(var_win_size).apply(func, raw=False)
        return result.dropna()

    @staticmethod
    def _to_dataframe(
        series: pd.Series,
        var_method: str,
        var_win_size: int,
        confidence_level: float,
    ) -> pd.DataFrame:
        """Format ``series`` into a DataFrame with parameter info."""

        return pd.DataFrame(
            {
                "as_of_date": series.index,
                "var_method": var_method,
                "var_win_size": var_win_size,
                "confidence_level": confidence_level,
                "var": series,
            }
        )

    @classmethod
    def historical_var(
        cls,
        df: pd.DataFrame,
        var_win_size: int = DEFAULT_VAR_WIN_SIZE,
        confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    ) -> pd.DataFrame:
        """Historical VaR at the given confidence level.

        Returns a DataFrame with columns ``as_of_date`` and ``var`` alongside
        the input parameters.
        """
        returns = cls._validate(df)

        def func(x: pd.Series) -> float:
            return float(-x.quantile(1 - confidence_level))

        result = cls._apply_window(returns, func, var_win_size)
        return cls._to_dataframe(result, "historical", var_win_size, confidence_level)

    @classmethod
    def parametric_var(
        cls,
        df: pd.DataFrame,
        var_win_size: int = DEFAULT_VAR_WIN_SIZE,
        confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    ) -> pd.DataFrame:
        """Parametric VaR assuming normally distributed returns.

        Returns a DataFrame describing the rolling VaR series and parameters.
        """
        returns = cls._validate(df)

        def func(x: pd.Series) -> float:
            mean = x.mean()
            std = x.std()
            z = NormalDist().inv_cdf(1 - confidence_level)
            return float(-(mean + z * std))

        result = cls._apply_window(returns, func, var_win_size)
        return cls._to_dataframe(result, "parametric", var_win_size, confidence_level)

    @classmethod
    def conditional_var(
        cls,
        df: pd.DataFrame,
        var_win_size: int = DEFAULT_VAR_WIN_SIZE,
        confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    ) -> pd.DataFrame:
        """Expected shortfall conditional on losses beyond VaR.

        Returns a DataFrame describing the rolling conditional VaR series.
        """
        returns = cls._validate(df)

        def func(x: pd.Series) -> float:
            var_threshold = -x.quantile(1 - confidence_level)
            tail_losses = x[x <= -var_threshold]
            if tail_losses.empty:
                return float(var_threshold)
            return float(-tail_losses.mean())

        result = cls._apply_window(returns, func, var_win_size)
        return cls._to_dataframe(result, "conditional", var_win_size, confidence_level)
