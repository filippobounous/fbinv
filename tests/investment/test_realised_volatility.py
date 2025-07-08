"""Unit tests for the :mod:`investment.analytics.realised_volatility` module."""

import unittest
import numpy as np
import pandas as pd

from investment.analytics import RealisedVolatilityCalculator
from investment.utils.consts import TRADING_DAYS

class RealisedVolatilityTests(unittest.TestCase):
    """Test cases for :class:`RealisedVolatilityCalculator`."""

    def test_close_to_close_volatility(self):
        """Compute close-to-close volatility from prices."""
        dates = pd.date_range("2020-01-01", periods=5, freq="D")
        prices = pd.DataFrame({"close": [10, 11, 12, 13, 14]}, index=dates)
        calc = RealisedVolatilityCalculator(rv_win_size=2, rv_model="close_to_close")
        result = calc.calculate(prices)
        log_ret = np.log(prices["close"]).diff()
        expected = log_ret.rolling(2).std() * np.sqrt(TRADING_DAYS)
        np.testing.assert_allclose(result["volatility"], expected.dropna())

    def test_other_volatility_models(self):
        """Validate Parkinson and Garman-Klass estimators."""
        dates = pd.date_range("2020-01-01", periods=4, freq="D")
        prices = pd.DataFrame(
            {
                "open": [10, 11, 12, 13],
                "high": [11, 12, 13, 14],
                "low": [9, 10, 11, 12],
                "close": [10.5, 11.5, 12.5, 13.5],
            },
            index=dates,
        )
        calc = RealisedVolatilityCalculator(
            rv_win_size=2, rv_model=["parkinson", "garman_klass"]
        )
        result = calc.calculate(prices)

        pk = (1 / (4 * np.log(2))) * (np.log(prices["high"] / prices["low"]) ** 2)
        expected_pk = np.sqrt(pk.rolling(2).mean()) * np.sqrt(TRADING_DAYS)
        res_pk = result[result["rv_model"] == "parkinson"]["volatility"]
        np.testing.assert_allclose(res_pk.reset_index(drop=True), expected_pk.dropna().reset_index(drop=True))

        term1 = 0.5 * (np.log(prices["high"] / prices["low"]) ** 2)
        term2 = (2 * np.log(2) - 1) * (np.log(prices["close"] / prices["open"]) ** 2)
        gk = term1 - term2
        expected_gk = np.sqrt(gk.rolling(2).mean()) * np.sqrt(TRADING_DAYS)
        res_gk = result[result["rv_model"] == "garman_klass"]["volatility"]
        np.testing.assert_allclose(res_gk.reset_index(drop=True), expected_gk.dropna().reset_index(drop=True))

    def test_additional_models(self):
        """Verify Rogers–Satchell and Yang–Zhang variants."""
        dates = pd.date_range("2020-01-01", periods=5, freq="D")
        prices = pd.DataFrame(
            {
                "open": [10, 11, 12, 13, 14],
                "high": [11, 12, 13, 14, 15],
                "low": [9, 10, 11, 12, 13],
                "close": [10.5, 11.5, 12.5, 13.5, 14.5],
            },
            index=dates,
        )
        calc = RealisedVolatilityCalculator(
            rv_win_size=2,
            rv_model=["rogers_satchell", "gk_yang_zhang", "yang_zhang"],
        )
        result = calc.calculate(prices)

        ho = np.log(prices["high"] / prices["open"])
        lo = np.log(prices["low"] / prices["open"])
        co = np.log(prices["close"] / prices["open"])
        rs = ho * (ho - co) + lo * (lo - co)
        exp_rs = np.sqrt(rs.rolling(2).mean()) * np.sqrt(TRADING_DAYS)
        res_rs = result[result["rv_model"] == "rogers_satchell"]["volatility"]
        np.testing.assert_allclose(res_rs.reset_index(drop=True), exp_rs.dropna().reset_index(drop=True))

        gk_term1 = 0.5 * (np.log(prices["high"] / prices["low"]) ** 2)
        gk_term2 = (2 * np.log(2) - 1) * (np.log(prices["close"] / prices["open"]) ** 2)
        gk_init = gk_term1 - gk_term2
        yz = np.log(prices["open"] / prices["close"].shift(1)) ** 2
        gk_yz = yz + gk_init
        exp_gkyz = np.sqrt(gk_yz.rolling(2).mean()) * np.sqrt(TRADING_DAYS)
        res_gkyz = result[result["rv_model"] == "gk_yang_zhang"]["volatility"]
        np.testing.assert_allclose(res_gkyz.reset_index(drop=True), exp_gkyz.dropna().reset_index(drop=True))

        log_open = np.log(prices["open"])
        log_close = np.log(prices["close"])
        log_oc = log_open - log_close.shift(1)
        log_co = log_close - log_open
        var_on = log_oc.rolling(2).var()
        var_day = log_co.rolling(2).var()
        rs2 = exp_rs ** 2  # rogers-satchell already annualised
        k = 0.34 / (1.34 + (2 + 1) / (2 - 1))
        exp_yz = np.sqrt(var_on + k * var_day + (1 - k) * rs2)
        res_yz = result[result["rv_model"] == "yang_zhang"]["volatility"]
        np.testing.assert_allclose(res_yz.reset_index(drop=True), exp_yz.dropna().reset_index(drop=True))
