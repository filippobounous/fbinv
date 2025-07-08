"""Unit tests for the :mod:`investment.analytics.var` module."""

import unittest
from statistics import NormalDist

import numpy as np
import pandas as pd

from investment.analytics import VaRCalculator

def _cond_var(x: pd.Series) -> float:
    """Return the conditional VaR for a returns window."""
    var_thresh = -x.quantile(0.05)
    tail = x[x <= -var_thresh]
    return -tail.mean() if not tail.empty else var_thresh

class VaRCalculatorTests(unittest.TestCase):
    """Test cases for :class:`VaRCalculator`."""

    def setUp(self):
        dates = pd.date_range("2020-01-01", periods=6, freq="D")
        self.df = pd.DataFrame({"close": [100, 102, 101, 105, 107, 106]}, index=dates)

    def test_historical_var(self):
        """Historical VaR matches rolling quantiles."""
        var = VaRCalculator.historical_var(self.df, var_win_size=3, confidence_level=0.95)
        returns = self.df["close"].pct_change().dropna()
        expected = returns.rolling(3).apply(lambda x: -x.quantile(0.05))
        np.testing.assert_allclose(var["var"], expected.dropna())

    def test_parametric_and_conditional_var(self):
        """Parametric and conditional VaR calculations agree with formulas."""
        param = VaRCalculator.parametric_var(self.df, var_win_size=3, confidence_level=0.95)
        cond = VaRCalculator.conditional_var(self.df, var_win_size=3, confidence_level=0.95)

        returns = self.df["close"].pct_change().dropna()
        z = NormalDist().inv_cdf(1 - 0.95)
        exp_param = returns.rolling(3).apply(lambda x: -(x.mean() + z * x.std()))
        exp_cond = returns.rolling(3).apply(_cond_var)
        np.testing.assert_allclose(param["var"], exp_param.dropna())
        np.testing.assert_allclose(cond["var"], exp_cond.dropna())

    def test_conditional_var_no_losses(self):
        """Conditional VaR handles periods with no losses."""
        df_up = pd.DataFrame({"close": [1, 2, 3, 4, 5]}, index=pd.date_range("2020-01-01", periods=5))
        result = VaRCalculator.conditional_var(df_up, var_win_size=2, confidence_level=0.95)
        returns = df_up["close"].pct_change().dropna()

        expected = returns.rolling(2).apply(_cond_var)
        np.testing.assert_allclose(result["var"], expected.dropna())

