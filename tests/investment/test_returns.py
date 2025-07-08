"""Unit tests for the :mod:`investment.analytics.returns` module."""

import unittest
import numpy as np
import pandas as pd

from investment.analytics import ReturnsCalculator

class ReturnsCalculatorTests(unittest.TestCase):
    """Test cases for :class:`ReturnsCalculator`."""

    def test_calculate_simple_and_log_returns(self):
        """Return both simple and logarithmic returns."""
        dates = pd.date_range("2020-01-01", periods=4, freq="D")
        df = pd.DataFrame({"close": [100, 110, 105, 115]}, index=dates)
        calc = ReturnsCalculator(use_ln_ret=True, ret_win_size=1)
        result = calc.calculate(df)
        expected = np.log(df["close"]).diff().dropna()
        np.testing.assert_allclose(result["return"], expected)

    def test_input_validation_errors(self):
        """Invalid inputs should trigger :class:`ValueError`."""
        calc = ReturnsCalculator()
        with self.assertRaises(ValueError):
            calc.calculate(pd.DataFrame())

        bad_df = pd.DataFrame({"close": [1, 2, 3]})
        bad_df.index = [0, 1, 2]
        with self.assertRaises(ValueError):
            calc.calculate(bad_df)

        with self.assertRaises(ValueError):
            calc.calculate(pd.DataFrame({"open": [1, 2, 3]}, index=pd.date_range("2020", periods=3)))

    def test_multiple_windows(self):
        """Support multiple rolling return windows."""
        dates = pd.date_range("2020-01-01", periods=5, freq="D")
        df = pd.DataFrame({"close": [10, 12, 14, 13, 15]}, index=dates)
        calc = ReturnsCalculator(use_ln_ret=False, ret_win_size=[1, 2])
        result = calc.calculate(df)
        simple1 = df["close"].pct_change(1)
        simple2 = df["close"].pct_change(2)
        expected = pd.concat([
            pd.DataFrame({"as_of_date": dates, "is_ln_ret": False, "ret_win_size": 1, "return": simple1}),
            pd.DataFrame({"as_of_date": dates, "is_ln_ret": False, "ret_win_size": 2, "return": simple2}),
        ]).dropna().reset_index(drop=True)
        pd.testing.assert_frame_equal(result, expected)
