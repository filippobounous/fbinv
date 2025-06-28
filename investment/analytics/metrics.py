"""Performance metrics for price history series.

This module defines :class:`PerformanceMetrics` which contains a collection of
helpers used when evaluating portfolio or security performance.  Each method
expects a ``pandas.DataFrame`` with a ``close`` column indexed by dates.  The
``_BaseAnalytics`` mixin validates the input and converts it to a series of
simple returns using :class:`ReturnsCalculator`.  These returns are then used to
derive cumulative and annualised performance statistics, drawdown measures and
risk‑adjusted ratios such as Sharpe and Sortino.
"""

from typing import Optional, Callable, Union
from functools import partial

import numpy as np
import pandas as pd

from ..utils.consts import TRADING_DAYS
from .base import _BaseAnalytics

class PerformanceMetrics(_BaseAnalytics):
    """Collection of common portfolio performance calculations.

    Each metric is implemented as a class method so that the class can be used
    in a stateless fashion. The ``df`` argument should contain historical price
    data obtained from ``BaseSecurity.get_price_history`` or a similar helper
    and must have a ``close`` column indexed by ``DatetimeIndex``. The methods
    return scalar values or, in the case of :meth:`drawdown_series`, a DataFrame
    describing the drawdown path. Most metrics can also be evaluated over
    rolling or expanding windows by supplying the ``window`` or ``expanding``
    parameters.
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

    # calculation helpers used with ``_apply_window``
    @staticmethod
    def _calc_cumulative_return(arr: np.ndarray) -> float:
        """Return the cumulative simple return of ``arr``."""
        return float(np.prod(1 + arr) - 1)

    @staticmethod
    def _calc_annualised_return(arr: np.ndarray, periods_per_year: int) -> float:
        """Return annualised simple return from ``arr``."""
        n = len(arr)
        if n == 0:
            return 0.0
        cumulative = np.prod(1 + arr)
        return float(cumulative ** (periods_per_year / n) - 1)

    @staticmethod
    def _calc_sharpe_ratio(
        arr: np.ndarray, risk_free_rate: float, periods_per_year: int
    ) -> float:
        """Return the annualised Sharpe ratio for ``arr``."""
        excess = arr - risk_free_rate / periods_per_year
        std = np.std(arr, ddof=1)
        if std == 0:
            return np.nan
        return float(excess.mean() / std * np.sqrt(periods_per_year))

    @staticmethod
    def _calc_sortino_ratio(
        arr: np.ndarray, risk_free_rate: float, periods_per_year: int
    ) -> float:
        """Return the annualised Sortino ratio for ``arr``."""
        excess = arr - risk_free_rate / periods_per_year
        downside = excess[excess < 0]
        if downside.size == 0:
            return np.nan
        downside_std = np.std(downside, ddof=1)
        if downside_std == 0:
            return np.nan
        return float(excess.mean() / downside_std * np.sqrt(periods_per_year))

    @staticmethod
    def _calc_volatility(arr: np.ndarray, periods_per_year: int) -> float:
        """Return annualised volatility of ``arr``."""
        return float(np.std(arr, ddof=1) * np.sqrt(periods_per_year))

    @staticmethod
    def _calc_downside_volatility(arr: np.ndarray, periods_per_year: int) -> float:
        """Return annualised downside volatility of ``arr``."""
        downside = arr[arr < 0]
        if downside.size == 0:
            return 0.0
        return float(np.std(downside, ddof=1) * np.sqrt(periods_per_year))

    @staticmethod
    def _calc_calmar_ratio(arr: np.ndarray, periods_per_year: int) -> float:
        """Return Calmar ratio computed from ``arr``."""
        n = len(arr)
        if n == 0:
            return np.nan
        cumulative = np.prod(1 + arr)
        ann_ret = cumulative ** (periods_per_year / n) - 1
        cum_returns = np.cumprod(1 + arr)
        running_max = np.maximum.accumulate(cum_returns)
        drawdown = (cum_returns - running_max) / running_max
        max_dd = drawdown.min()
        if max_dd == 0:
            return np.nan
        return float(ann_ret / abs(max_dd))

    @staticmethod
    def _calc_omega_ratio(arr: np.ndarray, target_period_return: float) -> float:
        """Return Omega ratio relative to ``target_period_return``."""
        excess = arr - target_period_return
        positive = excess[excess > 0].sum()
        negative = (-excess[excess < 0]).sum()
        if negative == 0:
            return np.nan
        return float(positive / negative)

    @staticmethod
    def _calc_hit_ratio(arr: np.ndarray) -> float:
        """Return fraction of observations in ``arr`` that are positive."""
        return float(np.mean(arr > 0))

    @classmethod
    def cumulative_return(
        cls,
        df: pd.DataFrame,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[float, pd.Series]:
        """Cumulative simple return.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.

        Returns
        -------
        float
            Total simple return expressed as a decimal value.
        """
        returns = cls._validate(df)
        func = cls._calc_cumulative_return
        return cls._apply_window(returns, func, window, expanding)

    @classmethod
    def annualised_return(
        cls,
        df: pd.DataFrame,
        periods_per_year: int = TRADING_DAYS,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[float, pd.Series]:
        """Annualised return of the series.

        The calculation assumes that returns are evenly spaced and scales the
        cumulative return according to the provided ``periods_per_year``.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        periods_per_year : int, optional
            Number of observations that constitute a year. Defaults to trading
            days (252).

        Returns
        -------
        float
            Annualised simple return as a decimal value.
        """
        returns = cls._validate(df)
        func = partial(cls._calc_annualised_return, periods_per_year=periods_per_year)
        return cls._apply_window(returns, func, window, expanding)

    @classmethod
    def drawdown_series(
        cls,
        df: pd.DataFrame,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> pd.DataFrame:
        """Series of drawdowns as percentages from peak equity.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.

        Returns
        -------
        pandas.DataFrame
            ``as_of_date`` and ``drawdown`` columns describing the drawdown
            path.
        """
        returns = cls._validate(df)
        cum_returns = (1 + returns).cumprod()
        if window is not None:
            running_max = cum_returns.rolling(window).max()
        elif expanding:
            running_max = cum_returns.expanding().max()
        else:
            running_max = cum_returns.cummax()
        drawdown = (cum_returns - running_max) / running_max
        return pd.DataFrame({"as_of_date": drawdown.index, "drawdown": drawdown})

    @classmethod
    def max_drawdown(
        cls,
        df: pd.DataFrame,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> float:
        """Maximum drawdown observed in the series.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.

        Returns
        -------
        float
            Largest percentage drop from a prior peak.
        """
        dd = cls.drawdown_series(df, window=window, expanding=expanding)
        return float(dd["drawdown"].min())

    @classmethod
    def sharpe_ratio(
        cls,
        df: pd.DataFrame,
        risk_free_rate: float = 0.0,
        periods_per_year: int = TRADING_DAYS,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[Optional[float], pd.Series]:
        """Annualised Sharpe ratio of the returns series.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        risk_free_rate : float, optional
            Risk‑free rate expressed per year.
        periods_per_year : int, optional
            Number of observations that constitute a year.

        Returns
        -------
        Optional[float]
            Sharpe ratio or ``None`` if the return variance is zero.
        """
        returns = cls._validate(df)
        func = partial(
            cls._calc_sharpe_ratio,
            risk_free_rate=risk_free_rate,
            periods_per_year=periods_per_year,
        )
        result = cls._apply_window(returns, func, window, expanding)
        if isinstance(result, pd.Series):
            return result
        return None if np.isnan(result) else float(result)

    @classmethod
    def sortino_ratio(
        cls,
        df: pd.DataFrame,
        risk_free_rate: float = 0.0,
        periods_per_year: int = TRADING_DAYS,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[Optional[float], pd.Series]:
        """Annualised Sortino ratio using downside deviation.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        risk_free_rate : float, optional
            Risk‑free rate per year used as the hurdle rate.
        periods_per_year : int, optional
            Number of observations that constitute a year.

        Returns
        -------
        Optional[float]
            Sortino ratio or ``None`` if downside deviation is zero.
        """
        returns = cls._validate(df)
        func = partial(
            cls._calc_sortino_ratio,
            risk_free_rate=risk_free_rate,
            periods_per_year=periods_per_year,
        )
        result = cls._apply_window(returns, func, window, expanding)
        if isinstance(result, pd.Series):
            return result
        return None if np.isnan(result) else float(result)

    @classmethod
    def volatility(
        cls,
        df: pd.DataFrame,
        periods_per_year: int = TRADING_DAYS,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[float, pd.Series]:
        """Annualised standard deviation of returns.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        periods_per_year : int, optional
            Number of observations that constitute a year.

        Returns
        -------
        float
            Annualised volatility expressed as a decimal value.
        """
        returns = cls._validate(df)
        func = partial(cls._calc_volatility, periods_per_year=periods_per_year)
        return cls._apply_window(returns, func, window, expanding)

    @classmethod
    def downside_volatility(
        cls,
        df: pd.DataFrame,
        periods_per_year: int = TRADING_DAYS,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[float, pd.Series]:
        """Annualised deviation of negative returns only.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        periods_per_year : int, optional
            Number of observations that constitute a year.

        Returns
        -------
        float
            Downside volatility calculated from negative returns only.
        """
        returns = cls._validate(df)
        func = partial(
            cls._calc_downside_volatility, periods_per_year=periods_per_year
        )
        return cls._apply_window(returns, func, window, expanding)

    @classmethod
    def calmar_ratio(
        cls,
        df: pd.DataFrame,
        periods_per_year: int = TRADING_DAYS,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[Optional[float], pd.Series]:
        """Ratio of annualised return to maximum drawdown.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        periods_per_year : int, optional
            Number of observations that constitute a year.

        Returns
        -------
        Optional[float]
            Calmar ratio or ``None`` if there is no drawdown.
        """
        returns = cls._validate(df)
        func = partial(cls._calc_calmar_ratio, periods_per_year=periods_per_year)
        result = cls._apply_window(returns, func, window, expanding)
        if isinstance(result, pd.Series):
            return result
        return None if np.isnan(result) else float(result)

    @classmethod
    def omega_ratio(
        cls,
        df: pd.DataFrame,
        target_return: float = 0.0,
        periods_per_year: int = TRADING_DAYS,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[Optional[float], pd.Series]:
        """Omega ratio relative to ``target_return`` per year.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        target_return : float, optional
            Desired return per year used as the threshold.
        periods_per_year : int, optional
            Number of observations that constitute a year.

        Returns
        -------
        Optional[float]
            Omega ratio or ``None`` if no negative excess returns are present.
        """
        returns = cls._validate(df)
        target_period_return = target_return / periods_per_year
        func = partial(
            cls._calc_omega_ratio, target_period_return=target_period_return
        )
        result = cls._apply_window(returns, func, window, expanding)
        if isinstance(result, pd.Series):
            return result
        return None if np.isnan(result) else float(result)

    @classmethod
    def hit_ratio(
        cls,
        df: pd.DataFrame,
        window: Optional[int] = None,
        expanding: bool = False,
    ) -> Union[float, pd.Series]:
        """Proportion of periods with a positive return.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.

        Returns
        -------
        float
            Fraction of observations where returns are strictly positive.
        """
        returns = cls._validate(df)
        func = cls._calc_hit_ratio
        return cls._apply_window(returns, func, window, expanding)
