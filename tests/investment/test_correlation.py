"""Unit tests for the :mod:`investment.analytics.correlation` module."""

import unittest
from unittest import mock
import numpy as np
import pandas as pd

from investment.analytics import CorrelationCalculator

class CorrelationCalculatorTests(unittest.TestCase):
    """Test cases for :class:`CorrelationCalculator`."""

    def test_mean_correlation(self):
        """Return the mean correlation value from a matrix."""
        matrix = pd.DataFrame(
            [[1.0, 0.2, 0.3], [0.2, 1.0, 0.4], [0.3, 0.4, 1.0]],
            columns=["a", "b", "c"],
            index=["a", "b", "c"],
        )
        calc = CorrelationCalculator()
        mean_corr = calc.mean_correlation(matrix)
        expected = np.mean([0.2, 0.3, 0.4])
        self.assertAlmostEqual(mean_corr, expected)

    def test_partial_and_rolling_mean(self):
        """Validate partial correlations and rolling mean calculation."""
        df = pd.DataFrame(
            {
                "a": [1, 2, 3, 4, 5],
                "b": [2, 3, 2, 5, 4],
                "c": [5, 4, 3, 2, 1],
            }
        )
        calc = CorrelationCalculator()
        with mock.patch.object(calc, "_gather_series", return_value=df):
            partial = calc.partial()

        corr = df.corr()
        inv = np.linalg.pinv(corr.values)
        expected = -inv / np.sqrt(np.outer(np.diag(inv), np.diag(inv)))
        np.fill_diagonal(expected, 1.0)
        expected_df = pd.DataFrame(expected, index=corr.index, columns=corr.columns)
        pd.testing.assert_frame_equal(partial, expected_df)

        series_dict = {
            ("a", "b"): pd.Series([0.1, 0.2, 0.3]),
            ("a", "c"): pd.Series([0.0, 0.5, 0.1]),
        }
        roll_mean = calc.rolling_mean_correlation(series_dict)
        expected_mean = pd.concat(series_dict.values(), axis=1).mean(axis=1)
        pd.testing.assert_series_equal(roll_mean, expected_mean)

    def test_semi_and_lagged(self):
        """Compute semi-correlation and lagged correlations."""
        data = pd.DataFrame({
            "a": [1.0, 2.0, 3.0, 4.0],
            "b": [2.0, 1.0, 4.0, 3.0],
        })
        calc = CorrelationCalculator()
        with mock.patch.object(calc, "_gather_series", return_value=data):
            semi = calc.semi(use_returns=False, downside=True)
            lagged = calc.lagged([0, 1], use_returns=False)

        mask = (data["a"] < 0) & (data["b"] < 0)
        s1 = data["a"][mask]
        s2 = data["b"][mask]
        expected_semi = pd.DataFrame(index=["a", "b"], columns=["a", "b"], dtype=float)
        corr_val = s1.corr(s2)
        expected_semi.loc["a", "b"] = corr_val
        expected_semi.loc["b", "a"] = corr_val
        np.fill_diagonal(expected_semi.values, 1.0)
        corr0 = data.corr()
        corr1 = data.corr().shift(1)
        pd.testing.assert_frame_equal(semi, expected_semi)

        self.assertIn(0, lagged)
        self.assertIn(1, lagged)
        pd.testing.assert_frame_equal(lagged[0], corr0)
        expected_lag1 = pd.DataFrame(index=["a","b"], columns=["a","b"], dtype=float)
        val = data["a"].corr(data["b"].shift(1))
        expected_lag1.loc["a","b"] = val
        expected_lag1.loc["b","a"] = val
        np.fill_diagonal(expected_lag1.values, 1.0)
        pd.testing.assert_frame_equal(lagged[1], expected_lag1)
