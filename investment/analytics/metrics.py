"""Performance metrics for price history series.

The :class:`PerformanceMetrics` class provides cumulative and annualised
returns, drawdown measures and risk-adjusted ratios such as Sharpe and
Sortino.
"""

from typing import Optional

import numpy as np
import pandas as pd

from ..utils.consts import TRADING_DAYS
from .base import _BaseAnalytics

class PerformanceMetrics(_BaseAnalytics):
    """Collection of common portfolio performance calculations."""

    @classmethod
    def cumulative_return(cls, df: pd.DataFrame) -> float:
        """Cumulative simple return over the entire series."""
        returns = cls._validate(df)
        return float((1 + returns).prod() - 1)

    @classmethod
    def annualised_return(
        cls, df: pd.DataFrame, periods_per_year: int = TRADING_DAYS
    ) -> float:
        """Annualised return assuming ``periods_per_year`` observations."""
        returns = cls._validate(df)
        n_periods = len(returns)
        if n_periods == 0:
            return 0.0
        cumulative = (1 + returns).prod()
        return float(cumulative ** (periods_per_year / n_periods) - 1)

    @classmethod
    def drawdown_series(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Series of drawdowns as percentages from peak equity."""
        returns = cls._validate(df)
        cum_returns = (1 + returns).cumprod()
        running_max = cum_returns.cummax()
        drawdown = (cum_returns - running_max) / running_max
        return pd.DataFrame({"as_of_date": drawdown.index, "drawdown": drawdown})

    @classmethod
    def max_drawdown(cls, df: pd.DataFrame) -> float:
        """Maximum drawdown observed in the series."""
        dd = cls.drawdown_series(df)
        return float(dd["drawdown"].min())

    @classmethod
    def sharpe_ratio(
        cls,
        df: pd.DataFrame,
        risk_free_rate: float = 0.0,
        periods_per_year: int = TRADING_DAYS,
    ) -> Optional[float]:
        """Annualised Sharpe ratio of the returns series."""
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
        """Annualised Sortino ratio using downside deviation."""
        returns = cls._validate(df)
        excess = returns - risk_free_rate / periods_per_year
        downside_std = excess[excess < 0].std()
        if downside_std == 0:
            return None
        return float(excess.mean() / downside_std * np.sqrt(periods_per_year))

    @classmethod
    def volatility(cls, df: pd.DataFrame, periods_per_year: int = TRADING_DAYS) -> float:
        """Annualised standard deviation of returns."""
        returns = cls._validate(df)
        return float(returns.std() * np.sqrt(periods_per_year))

    @classmethod
    def downside_volatility(
        cls, df: pd.DataFrame, periods_per_year: int = TRADING_DAYS
    ) -> float:
        """Annualised deviation of negative returns only."""
        returns = cls._validate(df)
        downside = returns[returns < 0]
        if downside.empty:
            return 0.0
        return float(downside.std() * np.sqrt(periods_per_year))

    @classmethod
    def calmar_ratio(
        cls, df: pd.DataFrame, periods_per_year: int = TRADING_DAYS
    ) -> Optional[float]:
        """Ratio of annualised return to maximum drawdown."""
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
        """Omega ratio relative to ``target_return`` per year."""
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
        """Proportion of periods with a positive return."""
        returns = cls._validate(df)
        return float((returns > 0).sum() / len(returns))
