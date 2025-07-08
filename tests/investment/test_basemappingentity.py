import unittest
from unittest import mock

import pandas as pd

from investment.core.security import Equity
from investment.datasource.test import TestDataSource

class BaseMappingEntityTestCase(unittest.TestCase):
    """Tests for :class:`investment.core.mapping.BaseMappingEntity`."""

    def setUp(self):
        patcher = mock.patch(
            "investment.core.mapping.BaseMappingEntity._local_datasource",
            TestDataSource,
        )
        self.addCleanup(patcher.stop)
        patcher.start()
        self.entity = Equity("AAA")

    def _price_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            {"close": [1.0, 2.0], "open": [1.0, 2.0], "high": [2.0, 3.0], "low": [0.5, 1.0]},
            index=pd.to_datetime(["2020-01-01", "2020-01-02"]),
        )

    def test_get_returns_uses_calculator(self):
        df_price = self._price_df()
        df_ret = pd.DataFrame()
        self.entity.get_price_history = mock.Mock(return_value=df_price)
        with mock.patch("investment.core.mapping.ReturnsCalculator") as rc:
            rc.return_value.calculate.return_value = df_ret
            result = self.entity.get_returns(use_ln_ret=False, ret_win_size=5)
        rc.assert_called_once_with(ret_win_size=5, use_ln_ret=False)
        rc.return_value.calculate.assert_called_once_with(df=df_price)
        self.assertIs(result, df_ret)

    def test_get_realised_volatility_uses_calculator(self):
        df_price = self._price_df()
        df_vol = pd.DataFrame()
        self.entity.get_price_history = mock.Mock(return_value=df_price)
        with mock.patch("investment.core.mapping.RealisedVolatilityCalculator") as rv:
            rv.return_value.calculate.return_value = df_vol
            result = self.entity.get_realised_volatility(rv_model="close_to_close", rv_win_size=10)
        rv.assert_called_once_with(rv_win_size=10, rv_model="close_to_close")
        rv.return_value.calculate.assert_called_once_with(df=df_price)
        self.assertIs(result, df_vol)

    def test_get_performance_metrics_concatenates_results(self):
        df_price = self._price_df()
        self.entity.get_price_history = mock.Mock(return_value=df_price)
        dfs = [pd.DataFrame({"metric": [i]}) for i in range(5)]
        with mock.patch("investment.core.mapping.PerformanceMetrics.cumulative_return", return_value=dfs[0]) as m1, \
             mock.patch("investment.core.mapping.PerformanceMetrics.annualised_return", return_value=dfs[1]) as m2, \
             mock.patch("investment.core.mapping.PerformanceMetrics.max_drawdown", return_value=dfs[2]) as m3, \
             mock.patch("investment.core.mapping.PerformanceMetrics.sharpe_ratio", return_value=dfs[3]) as m4, \
             mock.patch("investment.core.mapping.PerformanceMetrics.sortino_ratio", return_value=dfs[4]) as m5:
            result = self.entity.get_performance_metrics(metric_win_size=7, risk_free_rate=0.01, periods_per_year=252)
        m1.assert_called_once_with(df_price, metric_win_size=7)
        m2.assert_called_once_with(df_price, periods_per_year=252, metric_win_size=7)
        m3.assert_called_once_with(df_price, metric_win_size=7)
        m4.assert_called_once_with(df_price, risk_free_rate=0.01, periods_per_year=252, metric_win_size=7)
        m5.assert_called_once_with(df_price, risk_free_rate=0.01, periods_per_year=252, metric_win_size=7)
        expected = pd.concat(dfs).reset_index(drop=True)
        pd.testing.assert_frame_equal(result, expected)

    def test_get_var_uses_registry_method(self):
        df_price = self._price_df()
        df_var = pd.DataFrame()
        self.entity.get_price_history = mock.Mock(return_value=df_price)
        mock_calc = mock.Mock(return_value=df_var)
        with mock.patch("investment.core.mapping.VaRCalculator.registry", return_value={"hist": mock_calc}) as reg:
            result = self.entity.get_var(method="hist", var_win_size=3, confidence_level=0.95)
        reg.assert_called_once()
        mock_calc.assert_called_once_with(
            df_price,
            confidence_level=0.95,
            var_win_size=3,
        )
        self.assertIs(result, df_var)

    def test_get_var_bad_method_raises(self):
        df_price = self._price_df()
        self.entity.get_price_history = mock.Mock(return_value=df_price)
        with mock.patch("investment.core.mapping.VaRCalculator.registry", return_value={}):
            with self.assertRaises(KeyError):
                self.entity.get_var(method="missing")
