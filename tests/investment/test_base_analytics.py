"""Tests for BaseAnalytics input validation."""

import unittest

import pandas as pd

from investment.analytics.base import BaseAnalytics


class DummyAnalytics(BaseAnalytics):
    """Minimal subclass implementing registry for testing."""

    @staticmethod
    def registry() -> dict[str, callable]:
        return {}


class BaseAnalyticsValidateTests(unittest.TestCase):
    """Test cases for :meth:`BaseAnalytics._validate`."""

    def test_validate_success(self):
        """Validate returns computed pct changes."""
        dates = pd.date_range("2024-01-01", periods=4, freq="D")
        df = pd.DataFrame({"close": [1.0, 2.0, 4.0, 8.0]}, index=dates)
        result = DummyAnalytics._validate(df)
        expected = df["close"].pct_change().dropna()
        expected.index.name = "as_of_date"
        pd.testing.assert_series_equal(
            result, expected, check_freq=False, check_names=False
        )

    def test_validate_errors(self):
        """Invalid input frames raise :class:`ValueError`."""
        dates = pd.date_range("2024-01-01", periods=3, freq="D")
        df = pd.DataFrame({"close": [1, 2, 3]}, index=[0, 1, 2])
        with self.assertRaises(ValueError):
            DummyAnalytics._validate(df)
        with self.assertRaises(ValueError):
            DummyAnalytics._validate(pd.DataFrame())
        with self.assertRaises(ValueError):
            DummyAnalytics._validate(pd.DataFrame({"open": [1, 2, 3]}, index=dates))
