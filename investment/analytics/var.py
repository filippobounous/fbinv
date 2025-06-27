"""Value-at-Risk analytics for assessing downside risk.

The :class:`VaRCalculator` provides historical, parametric and conditional
Value-at-Risk estimations using validated return series.
"""

from statistics import NormalDist
import pandas as pd

from .base import _BaseAnalytics

class VaRCalculator(_BaseAnalytics):
    """Value-at-Risk related calculations."""

    @classmethod
    def value_at_risk(cls, df: pd.DataFrame, confidence_level: float = 0.95) -> float:
        """Historical VaR at the given confidence level."""
        returns = cls._validate(df)
        return float(-returns.quantile(1 - confidence_level))

    @classmethod
    def parametric_var(cls, df: pd.DataFrame, confidence_level: float = 0.95) -> float:
        """Parametric VaR assuming normally distributed returns."""
        returns = cls._validate(df)
        mean = returns.mean()
        std = returns.std()
        z = NormalDist().inv_cdf(1 - confidence_level)
        return float(-(mean + z * std))

    @classmethod
    def conditional_var(cls, df: pd.DataFrame, confidence_level: float = 0.95) -> float:
        """Expected shortfall conditional on losses beyond VaR."""
        returns = cls._validate(df)
        var_threshold = -cls.value_at_risk(df, confidence_level)
        tail_losses = returns[returns <= -var_threshold]
        if tail_losses.empty:
            return float(var_threshold)
        return float(-tail_losses.mean())
