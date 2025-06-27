"""Performance metrics for price history series.

This module defines :class:`PerformanceMetrics` which contains a collection of
helpers used when evaluating portfolio or security performance.  Each method
expects a ``pandas.DataFrame`` with a ``close`` column indexed by dates.  The
``_BaseAnalytics`` mixin validates the input and converts it to a series of
simple returns using :class:`ReturnsCalculator`.  These returns are then used to
derive cumulative and annualised performance statistics, drawdown measures and
risk‑adjusted ratios such as Sharpe and Sortino.
"""

from typing import Optional

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
    describing the drawdown path.
    """

    @classmethod
    def cumulative_return(cls, df: pd.DataFrame) -> float:
        """Cumulative simple return over the entire series.

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
        return float((1 + returns).prod() - 1)

    @classmethod
    def annualised_return(
        cls, df: pd.DataFrame, periods_per_year: int = TRADING_DAYS
    ) -> float:
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
        n_periods = len(returns)
        if n_periods == 0:
            return 0.0
        cumulative = (1 + returns).prod()
        return float(cumulative ** (periods_per_year / n_periods) - 1)

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
    def max_drawdown(cls, df: pd.DataFrame) -> float:
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
        dd = cls.drawdown_series(df)
        return float(dd["drawdown"].min())

    @classmethod
    def sharpe_ratio(
        cls,
        df: pd.DataFrame,
        risk_free_rate: float = 0.0,
        periods_per_year: int = TRADING_DAYS,
    ) -> Optional[float]:
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
        excess = returns - risk_free_rate / periods_per_year
        std = returns.std()
        if std == 0:
            return None
        return float(excess.mean() / std * np.sqrt(periods_per_year))

    @classmethod
    def sortino_ratio(
        cls,
        df: pd.DataFrame,
        risk_free_rate: float = 0.0,
        periods_per_year: int = TRADING_DAYS,
    ) -> Optional[float]:
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
        excess = returns - risk_free_rate / periods_per_year
        downside_std = excess[excess < 0].std()
        if downside_std == 0:
            return None
        return float(excess.mean() / downside_std * np.sqrt(periods_per_year))

    @classmethod
    def volatility(cls, df: pd.DataFrame, periods_per_year: int = TRADING_DAYS) -> float:
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
        return float(returns.std() * np.sqrt(periods_per_year))

    @classmethod
    def downside_volatility(
        cls, df: pd.DataFrame, periods_per_year: int = TRADING_DAYS
    ) -> float:
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
        downside = returns[returns < 0]
        if downside.empty:
            return 0.0
        return float(downside.std() * np.sqrt(periods_per_year))

    @classmethod
    def calmar_ratio(
        cls, df: pd.DataFrame, periods_per_year: int = TRADING_DAYS
    ) -> Optional[float]:
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
        ann_ret = cls.annualised_return(df, periods_per_year)
        max_dd = cls.max_drawdown(df)
        if max_dd == 0:
            return None
        return float(ann_ret / abs(max_dd))

    @classmethod
    def omega_ratio(
        cls,
        df: pd.DataFrame,
        target_return: float = 0.0,
        periods_per_year: int = TRADING_DAYS,
    ) -> Optional[float]:
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
        excess = returns - target_period_return
        positive = excess[excess > 0].sum()
        negative = (-excess[excess < 0]).sum()
        if negative == 0:
            return None
        return float(positive / negative)

    @classmethod
    def hit_ratio(cls, df: pd.DataFrame) -> float:
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
        return float((returns > 0).sum() / len(returns))
