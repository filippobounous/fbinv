"""Value-at-Risk analytics for assessing downside risk.

This module provides the :class:`VaRCalculator` class which exposes a few
commonly used approaches for estimating Value‑at‑Risk (VaR).  All
calculations operate on a price history ``pandas.DataFrame`` that is
validated by ``_BaseAnalytics`` and converted to a series of simple returns.
The class includes methods for historical VaR based on empirical quantiles as
well as parametric and conditional forms often used in risk management.
"""

from statistics import NormalDist
from typing import Optional, Callable, Union
from functools import partial

import numpy as np
import pandas as pd

from .base import _BaseAnalytics

class VaRCalculator(_BaseAnalytics):
    """Value-at-Risk related calculations.

    The methods are provided as class methods for stateless use.  The ``df``
    argument should contain historical prices indexed by dates and is
    converted to simple returns before the risk measure is computed.  All
    methods accept ``window`` and ``expanding`` parameters to compute rolling or
    expanding estimates.
    """

    @staticmethod
    def _apply_window(
        series: pd.Series,
        func: Callable[[np.ndarray], float],
        window: Optional[int],
        expanding: bool,
    ) -> Union[float, pd.Series]:
        """Apply ``func`` over a rolling or expanding window."""
        if window is not None:
            return series.rolling(window).apply(func, raw=True)
        if expanding:
            return series.expanding().apply(func, raw=True)
        return float(func(series.to_numpy()))

    @staticmethod
    def _calc_value_at_risk(arr: np.ndarray, confidence_level: float) -> float:
        """Return historical VaR for ``arr`` at ``confidence_level``."""
        return float(-np.quantile(arr, 1 - confidence_level))

    @staticmethod
    def _calc_parametric_var(arr: np.ndarray, z: float) -> float:
        """Return parametric VaR for ``arr`` using ``z`` score."""
        mean = arr.mean()
        std = np.std(arr, ddof=1)
        return float(-(mean + z * std))

    @staticmethod
    def _calc_conditional_var(arr: np.ndarray, confidence_level: float) -> float:
        """Return conditional VaR for ``arr`` at ``confidence_level``."""
        var_thresh = np.quantile(arr, 1 - confidence_level)
        tail_losses = arr[arr <= var_thresh]
        if tail_losses.size == 0:
            return float(-var_thresh)
        return float(-tail_losses.mean())

    @classmethod
    def value_at_risk(
        cls,
        df: pd.DataFrame,
        confidence_level: float = 0.95,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[float, pd.Series]:
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
        func = partial(cls._calc_value_at_risk, confidence_level=confidence_level)
        return cls._apply_window(returns, func, window, expanding)

    @classmethod
    def parametric_var(
        cls,
        df: pd.DataFrame,
        confidence_level: float = 0.95,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[float, pd.Series]:
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
        z = NormalDist().inv_cdf(1 - confidence_level)
        func = partial(cls._calc_parametric_var, z=z)
        return cls._apply_window(returns, func, window, expanding)

    @classmethod
    def conditional_var(
        cls,
        df: pd.DataFrame,
        confidence_level: float = 0.95,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[float, pd.Series]:
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
        func = partial(
            cls._calc_conditional_var, confidence_level=confidence_level
        )
        return cls._apply_window(returns, func, window, expanding)
