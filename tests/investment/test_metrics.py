"""Unit tests for the :mod:`investment.analytics.metrics` module."""

import unittest

import numpy as np
import pandas as pd

from investment.analytics import PerformanceMetrics
from investment.utils.consts import TRADING_DAYS


def sharpe_func(x: pd.Series) -> float:
    """Return the Sharpe ratio for an array of returns."""
    std = x.std()
    if std == 0:
        return np.nan
    return x.mean() / std * np.sqrt(TRADING_DAYS)


def hit_func(x: pd.Series) -> float:
    """Return the hit ratio for a window of returns."""
    return float((x > 0).sum() / len(x))


def md_func(x: pd.Series) -> float:
    """Return the maximum drawdown for a window."""
    cum = (1 + x).cumprod()
    running_max = cum.cummax()
    drawdown = (cum - running_max) / running_max
    return float(drawdown.min())


def sortino_func(x: pd.Series) -> float:
    """Return the Sortino ratio for the returns."""
    downside = x[x < 0].std()
    if downside == 0:
        return np.nan
    return x.mean() / downside * np.sqrt(TRADING_DAYS)


def dvol_func(x: pd.Series) -> float:
    """Return downside volatility for the returns."""
    d = x[x < 0]
    if d.empty:
        return np.nan
    return d.std() * np.sqrt(TRADING_DAYS)


def omega_func(x: pd.Series) -> float:
    """Return the Omega ratio for the returns."""
    pos = x[x > 0].sum()
    neg = (-x[x < 0]).sum()
    if neg == 0:
        return np.nan
    return pos / neg


class PerformanceMetricsTests(unittest.TestCase):
    """Test cases for :class:`PerformanceMetrics`."""

    def test_cumulative_and_sharpe(self):
        """Verify cumulative returns and Sharpe ratio calculations."""
        dates = pd.date_range("2020-01-01", periods=6, freq="D")
        prices = pd.DataFrame({"close": [1, 2, 3, 4, 5, 6]}, index=dates)
        cum = PerformanceMetrics.cumulative_return(prices, metric_win_size=3)
        returns = prices["close"].pct_change().dropna()
        expected_cum = returns.rolling(3).apply(lambda x: (1 + x).prod() - 1)
        np.testing.assert_allclose(cum["value"], expected_cum.dropna())

        sharpe = PerformanceMetrics.sharpe_ratio(prices, metric_win_size=3)
        excess = returns - 0 / TRADING_DAYS
        expected_sharpe = excess.rolling(3).apply(sharpe_func)
        np.testing.assert_allclose(sharpe["value"], expected_sharpe.dropna())

    def test_hit_ratio_and_max_drawdown(self):
        """Check hit ratio and maximum drawdown computations."""
        dates = pd.date_range("2020-01-01", periods=6, freq="D")
        prices = pd.DataFrame({"close": [1, 2, 1.5, 3, 2.5, 2]}, index=dates)
        win = 3

        hit = PerformanceMetrics.hit_ratio(prices, metric_win_size=win)
        returns = prices["close"].pct_change().dropna()
        expected_hit = returns.rolling(win).apply(hit_func)
        np.testing.assert_allclose(hit["value"], expected_hit.dropna())

        max_dd = PerformanceMetrics.max_drawdown(prices, metric_win_size=win)
        expected_md = returns.rolling(win).apply(md_func)
        np.testing.assert_allclose(max_dd["value"], expected_md.dropna())

    def test_additional_metrics(self):
        """Validate other performance statistics work correctly."""
        dates = pd.date_range("2020-01-01", periods=6, freq="D")
        prices = pd.DataFrame({"close": [1, 2, 3, 4, 5, 6]}, index=dates)
        win = 3
        ann = PerformanceMetrics.annualised_return(prices, metric_win_size=win)
        returns = prices["close"].pct_change().dropna()
        expected_ann = returns.rolling(win).apply(
            lambda x: ((1 + x).prod()) ** (TRADING_DAYS / len(x)) - 1
        )
        np.testing.assert_allclose(ann["value"], expected_ann.dropna())

        dd_series = PerformanceMetrics.drawdown_series(prices)
        cum = (1 + returns).cumprod()
        running_max = cum.cummax()
        drawdown = (cum - running_max) / running_max
        drawdown.index.name = "as_of_date"
        pd.testing.assert_series_equal(
            dd_series["drawdown"], drawdown, check_freq=False, check_names=False
        )

        sortino = PerformanceMetrics.sortino_ratio(prices, metric_win_size=win)
        excess = returns - 0 / TRADING_DAYS
        expected_sortino = excess.rolling(win).apply(sortino_func)
        np.testing.assert_allclose(sortino["value"], expected_sortino.dropna())

        dvol = PerformanceMetrics.downside_volatility(prices, metric_win_size=win)
        expected_dvol = returns.rolling(win).apply(dvol_func)
        np.testing.assert_allclose(dvol["value"], expected_dvol.dropna())

        calmar = PerformanceMetrics.calmar_ratio(prices, metric_win_size=win)
        ann_val = expected_ann.dropna()
        max_dd = returns.rolling(win).apply(
            lambda x: ((1 + x).cumprod() - (1 + x).cumprod().cummax())
            .div((1 + x).cumprod().cummax())
            .min()
        )
        expected_calmar = ann_val / abs(max_dd.dropna())
        np.testing.assert_allclose(calmar["value"], expected_calmar)

        omega = PerformanceMetrics.omega_ratio(prices, metric_win_size=win)
        expected_omega = (returns - 0 / TRADING_DAYS).rolling(win).apply(omega_func)
        np.testing.assert_allclose(omega["value"], expected_omega.dropna())
