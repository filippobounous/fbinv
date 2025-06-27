"""Value-at-Risk analytics for assessing downside risk.

This module provides the :class:`VaRCalculator` class which exposes a few
commonly used approaches for estimating Value‑at‑Risk (VaR).  All
calculations operate on a price history ``pandas.DataFrame`` that is
validated by ``_BaseAnalytics`` and converted to a series of simple returns.
The class includes methods for historical VaR based on empirical quantiles as
well as parametric and conditional forms often used in risk management.
"""

from statistics import NormalDist
import pandas as pd

from .base import _BaseAnalytics

class VaRCalculator(_BaseAnalytics):
    """Value-at-Risk related calculations.

    The methods are provided as class methods for stateless use.  The ``df``
    argument should contain historical prices indexed by dates and is
    converted to simple returns before the risk measure is computed.
    """

    @classmethod
    def value_at_risk(cls, df: pd.DataFrame, confidence_level: float = 0.95) -> float:
        """Historical VaR at the given confidence level.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        confidence_level : float, optional
            Probability used to determine the VaR quantile. Defaults to 0.95.

        Returns
        -------
        float
            Historical VaR expressed as a negative decimal.
        """
        returns = cls._validate(df)
        return float(-returns.quantile(1 - confidence_level))

    @classmethod
    def parametric_var(cls, df: pd.DataFrame, confidence_level: float = 0.95) -> float:
        """Parametric VaR assuming normally distributed returns.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        confidence_level : float, optional
            Confidence level used to compute the z‑score.

        Returns
        -------
        float
            Parametric VaR expressed as a negative decimal.
        """
        returns = cls._validate(df)
        mean = returns.mean()
        std = returns.std()
        z = NormalDist().inv_cdf(1 - confidence_level)
        return float(-(mean + z * std))

    @classmethod
    def conditional_var(cls, df: pd.DataFrame, confidence_level: float = 0.95) -> float:
        """Expected shortfall conditional on losses beyond VaR.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        confidence_level : float, optional
            Confidence level used when computing the initial VaR threshold.

        Returns
        -------
        float
            Average loss given that losses exceed the VaR level.
        """
        returns = cls._validate(df)
        var_threshold = -cls.value_at_risk(df, confidence_level)
        tail_losses = returns[returns <= -var_threshold]
        if tail_losses.empty:
            return float(var_threshold)
        return float(-tail_losses.mean())
