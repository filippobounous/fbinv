"""Performance metrics for price history series.

This module defines :class:`PerformanceMetrics` which contains a collection of
helpers used when evaluating portfolio or security performance.  Each method
expects a ``pandas.DataFrame`` with a ``close`` column indexed by dates.  The
``_BaseAnalytics`` mixin validates the input and converts it to a series of
simple returns using :class:`ReturnsCalculator`.  These returns are then used to
derive cumulative and annualised performance statistics, drawdown measures and
risk‑adjusted ratios such as Sharpe and Sortino.
"""

from typing import Callable, Any

import numpy as np
import pandas as pd

from .base import _BaseAnalytics
from ..utils.consts import (
    TRADING_DAYS,
    DEFAULT_METRIC_WIN_SIZE,
    DEFAULT_RISK_FREE_RATE,
)

# TODO: rolling window with win_size instead of setting as single value
# TODO: implement correlation for portfolio
# TODO: rethink how this is used in the context of portfolio etc, perhaps should be done similarly to correlation page

# TODO: rolling window with win_size instead of setting as single value
# TODO: implement correlation for portfolio
# TODO: rethink how this is used in the context of portfolio etc, perhaps should be done similarly
# to correlation page

class PerformanceMetrics(_BaseAnalytics):
    """Collection of common portfolio performance calculations.

    Each metric is implemented as a class method so that the class can be used
    in a stateless fashion. The ``df`` argument should contain historical price
    data obtained from ``BaseSecurity.get_price_history`` or a similar helper
    and must have a ``close`` column indexed by ``DatetimeIndex``. The methods
    return scalar values or, in the case of :meth:`drawdown_series`, a DataFrame
    describing the drawdown path.
    """

    @staticmethod
    def registry() -> dict[str, Callable[..., pd.DataFrame]]:
        """Return mapping of metric names to calculation methods."""
        return {
            "cumulative_return": PerformanceMetrics.cumulative_return,
            "annualised_return": PerformanceMetrics.annualised_return,
            "drawdown_series": PerformanceMetrics.drawdown_series,
            "max_drawdown": PerformanceMetrics.max_drawdown,
            "sharpe_ratio": PerformanceMetrics.sharpe_ratio,
            "sortino_ratio": PerformanceMetrics.sortino_ratio,
            "downside_volatility": PerformanceMetrics.downside_volatility,
            "calmar_ratio": PerformanceMetrics.calmar_ratio,
            "omega_ratio": PerformanceMetrics.omega_ratio,
            "hit_ratio": PerformanceMetrics.hit_ratio,
        }

    @staticmethod
    def _apply_window(
        series: pd.Series,
        func: Callable[[pd.Series], float],
        metric_win_size: int,
    ) -> pd.Series:
        """Apply ``func`` over a mandatory rolling ``metric_win_size``."""

        result = series.rolling(metric_win_size).apply(func, raw=False)
        return result.dropna()

    @staticmethod
    def _to_dataframe(
        series: pd.Series,
        metric: str,
        metric_win_size: int,
        **metric_kwargs: Any,
    ) -> pd.DataFrame:
        """Format ``series`` into a DataFrame with parameter info."""

        df_dict = {
            "as_of_date": series.index,
            "metric": metric,
            "metric_win_size": metric_win_size,
            "value": series,
        }
        for key, value in metric_kwargs.items():
            df_dict[key] = value
        return pd.DataFrame(df_dict)

    @classmethod
    def cumulative_return(
        cls,
        df: pd.DataFrame,
        metric_win_size: int = DEFAULT_METRIC_WIN_SIZE,
    ) -> pd.DataFrame:
        """Cumulative simple return.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.

        Returns
        -------
        pandas.DataFrame
            Columns ``as_of_date`` and ``value`` containing the cumulative
            return for each rolling window.
        """
        returns = cls._validate(df)

        def func(x: pd.Series) -> float:
            return float((1 + x).prod() - 1)

        result = cls._apply_window(returns, func, metric_win_size)
        return cls._to_dataframe(result, "cumulative_return", metric_win_size)

    @classmethod
    def annualised_return(
        cls,
        df: pd.DataFrame,
        metric_win_size: int = DEFAULT_METRIC_WIN_SIZE,
        periods_per_year: int = TRADING_DAYS,
    ) -> pd.DataFrame:
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
        pandas.DataFrame
            Rolling annualised return with ``as_of_date`` and ``value`` columns.
        """
        returns = cls._validate(df)

        def func(x: pd.Series) -> float:
            n_periods = len(x)
            if n_periods == 0:
                return 0.0
            cumulative = (1 + x).prod()
            return float(cumulative ** (periods_per_year / n_periods) - 1)

        result = cls._apply_window(returns, func, metric_win_size)
        return cls._to_dataframe(
            result,
            "annualised_return",
            metric_win_size,
            periods_per_year=periods_per_year,
        )

    @classmethod
    def drawdown_series(cls, df: pd.DataFrame) -> pd.DataFrame:
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
        running_max = cum_returns.cummax()
        drawdown = (cum_returns - running_max) / running_max
        return pd.DataFrame({"as_of_date": drawdown.index, "drawdown": drawdown})

    @classmethod
    def max_drawdown(
        cls,
        df: pd.DataFrame,
        metric_win_size: int = DEFAULT_METRIC_WIN_SIZE,
    ) -> pd.DataFrame:
        """Maximum drawdown observed in the series.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.

        Returns
        -------
        pandas.DataFrame
            ``as_of_date`` and ``value`` of the maximum drawdown for each
            rolling window.
        """
        def func(x: pd.Series) -> float:
            cum_returns = (1 + x).cumprod()
            running_max = cum_returns.cummax()
            drawdown = (cum_returns - running_max) / running_max
            return float(drawdown.min())

        returns = cls._validate(df)
        result = cls._apply_window(returns, func, metric_win_size)
        return cls._to_dataframe(result, "max_drawdown", metric_win_size)

    @classmethod
    def sharpe_ratio(
        cls,
        df: pd.DataFrame,
        metric_win_size: int = DEFAULT_METRIC_WIN_SIZE,
        risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
        periods_per_year: int = TRADING_DAYS,
    ) -> pd.DataFrame:
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
        pandas.DataFrame
            Sharpe ratio for each ``as_of_date`` with the supplied parameters.
        """
        returns = cls._validate(df)
        excess = returns - risk_free_rate / periods_per_year

        def func(x: pd.Series) -> float:
            std = x.std()
            if std == 0:
                return np.nan
            return float(x.mean() / std * np.sqrt(periods_per_year))

        result = cls._apply_window(excess, func, metric_win_size)
        return cls._to_dataframe(
            result,
            "sharpe_ratio",
            metric_win_size,
            risk_free_rate=risk_free_rate,
            periods_per_year=periods_per_year,
        )

    @classmethod
    def sortino_ratio(
        cls,
        df: pd.DataFrame,
        metric_win_size: int = DEFAULT_METRIC_WIN_SIZE,
        risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
        periods_per_year: int = TRADING_DAYS,
    ) -> pd.DataFrame:
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
        pandas.DataFrame
            Sortino ratio for each ``as_of_date`` with the supplied parameters.
        """
        returns = cls._validate(df)
        excess = returns - risk_free_rate / periods_per_year

        def func(x: pd.Series) -> float:
            downside_std = x[x < 0].std()
            if downside_std == 0:
                return np.nan
            return float(x.mean() / downside_std * np.sqrt(periods_per_year))

        result = cls._apply_window(excess, func, metric_win_size)
        return cls._to_dataframe(
            result,
            "sortino_ratio",
            metric_win_size,
            risk_free_rate=risk_free_rate,
            periods_per_year=periods_per_year,
        )

    @classmethod
    def downside_volatility(
        cls,
        df: pd.DataFrame,
        metric_win_size: int = DEFAULT_METRIC_WIN_SIZE,
        periods_per_year: int = TRADING_DAYS,
    ) -> pd.DataFrame:
        """Annualised deviation of negative returns only.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        periods_per_year : int, optional
            Number of observations that constitute a year.

        Returns
        -------
        pandas.DataFrame
            Downside volatility per ``as_of_date`` computed from negative
            returns only.
        """
        returns = cls._validate(df)

        def func(x: pd.Series) -> float:
            downside = x[x < 0]
            if downside.empty:
                return np.nan
            return float(downside.std() * np.sqrt(periods_per_year))

        result = cls._apply_window(returns, func, metric_win_size)
        return cls._to_dataframe(
            result,
            "downside_volatility",
            metric_win_size,
            periods_per_year=periods_per_year,
        )

    @classmethod
    def calmar_ratio(
        cls,
        df: pd.DataFrame,
        metric_win_size: int = DEFAULT_METRIC_WIN_SIZE,
        periods_per_year: int = TRADING_DAYS,
    ) -> pd.DataFrame:
        """Ratio of annualised return to maximum drawdown.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.
        periods_per_year : int, optional
            Number of observations that constitute a year.

        Returns
        -------
        pandas.DataFrame
            Calmar ratio for each ``as_of_date`` with the supplied parameters.
        """
        ann_ret = cls.annualised_return(
            df,
            periods_per_year=periods_per_year,
            metric_win_size=metric_win_size,
        )["value"]
        max_dd = cls.max_drawdown(
            df,
            metric_win_size=metric_win_size,
        )["value"]
        result = ann_ret / abs(max_dd)
        return cls._to_dataframe(
            result,
            "calmar_ratio",
            metric_win_size,
            periods_per_year=periods_per_year,
        )

    @classmethod
    def omega_ratio(
        cls,
        df: pd.DataFrame,
        metric_win_size: int = DEFAULT_METRIC_WIN_SIZE,
        target_return: float = DEFAULT_RISK_FREE_RATE,
        periods_per_year: int = TRADING_DAYS,
    ) -> pd.DataFrame:
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
        pandas.DataFrame
            Omega ratio for each ``as_of_date`` with the supplied parameters.
        """
        returns = cls._validate(df)
        target_period_return = target_return / periods_per_year
        excess = returns - target_period_return

        def func(x: pd.Series) -> float:
            positive = x[x > 0].sum()
            negative = (-x[x < 0]).sum()
            if negative == 0:
                return np.nan
            return float(positive / negative)

        result = cls._apply_window(excess, func, metric_win_size)
        return cls._to_dataframe(
            result,
            "omega_ratio",
            metric_win_size,
            target_return=target_return,
            periods_per_year=periods_per_year,
        )

    @classmethod
    def hit_ratio(
        cls,
        df: pd.DataFrame,
        metric_win_size: int = DEFAULT_METRIC_WIN_SIZE,
    ) -> pd.DataFrame:
        """Proportion of periods with a positive return.

        Parameters
        ----------
        df : pandas.DataFrame
            Price history with a ``close`` column.

        Returns
        -------
        pandas.DataFrame
            Fraction of observations where returns are strictly positive
            for each ``as_of_date``.
        """
        returns = cls._validate(df)

        def func(x: pd.Series) -> float:
            return float((x > 0).sum() / len(x))

        result = cls._apply_window(returns, func, metric_win_size)
        return cls._to_dataframe(result, "hit_ratio", metric_win_size)
