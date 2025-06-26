import unittest
import pandas as pd
import numpy as np

from investment.analytics.returns import ReturnsCalculator

class ReturnsCalculatorTest(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range('2020-01-01', periods=5, freq='D')
        self.df = pd.DataFrame({'close': [10, 12, 11, 15, 16]}, index=dates)

    def test_log_returns(self):
        calc = ReturnsCalculator()
        result = calc.calculate(self.df)
        expected_first = np.log(12/10)
        self.assertAlmostEqual(result['return'].iloc[0], expected_first)

    def test_simple_returns(self):
        calc = ReturnsCalculator(use_ln_ret=False)
        result = calc.calculate(self.df)
        expected_first = (12-10)/10
        self.assertAlmostEqual(result['return'].iloc[0], expected_first)

    def test_empty_dataframe(self):
        calc = ReturnsCalculator()
        with self.assertRaises(ValueError):
            calc.calculate(pd.DataFrame())

if __name__ == '__main__':
    unittest.main()
