import unittest
import pandas as pd
import numpy as np

from investment.analytics.realised_volatility import RealisedVolatilityCalculator

class RealisedVolatilityCalculatorTest(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range('2020-01-01', periods=5, freq='D')
        self.df = pd.DataFrame({
            'open': [10, 12, 11, 15, 16],
            'high': [11, 13, 12, 16, 17],
            'low': [9, 11, 10, 14, 15],
            'close': [10, 12, 11, 15, 16]
        }, index=dates)
        self.calc = RealisedVolatilityCalculator(rv_win_size=2)

    def test_close_to_close(self):
        result = self.calc._close_to_close(self.df, rv_win_size=2)
        log_ret = np.log(self.df['close']).diff()
        expected = log_ret.rolling(2).std() * np.sqrt(self.calc.dt)
        pd.testing.assert_series_equal(result, expected)

    def test_parkinson(self):
        result = self.calc._parkinson(self.df, rv_win_size=2)
        rs = (1.0 / (4.0 * np.log(2))) * (np.log(self.df['high'] / self.df['low']) ** 2)
        expected = np.sqrt(rs.rolling(2).mean()) * np.sqrt(self.calc.dt)
        pd.testing.assert_series_equal(result, expected)

    def test_garman_klass(self):
        result = self.calc._garman_klass(self.df, rv_win_size=2)
        term1 = 0.5 * (np.log(self.df['high'] / self.df['low']) ** 2)
        term2 = (2 * np.log(2) - 1) * (np.log(self.df['close'] / self.df['open']) ** 2)
        rs = term1 - term2
        expected = np.sqrt(rs.rolling(2).mean()) * np.sqrt(self.calc.dt)
        pd.testing.assert_series_equal(result, expected)

    def test_calculate_multiple_models(self):
        calc = RealisedVolatilityCalculator(rv_win_size=2, rv_model=['close_to_close', 'parkinson'])
        df = calc.calculate(self.df)
        self.assertIn('volatility', df.columns)
        self.assertEqual(set(df['rv_model'].unique()), {'close_to_close', 'parkinson'})

if __name__ == '__main__':
    unittest.main()
