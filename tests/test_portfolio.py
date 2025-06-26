import unittest
from unittest.mock import patch, PropertyMock
import pandas as pd

from investment.core.portfolio import Portfolio

class PortfolioTest(unittest.TestCase):
    def setUp(self):
        self.portfolio = Portfolio.model_construct(
            code='TEST', owner='me', has_cash=False
        )
        dates = pd.date_range('2020-01-01', periods=3, freq='D')
        self.transactions_df = pd.DataFrame({
            'as_of_date': dates.tolist()*1,
            'figi_code': ['AAA', 'AAA', 'AAA'],
            'quantity': [1, 1, 1],
            'value': [10, 10, 10],
            'currency': ['USD', 'USD', 'USD'],
            'account': ['ACC', 'ACC', 'ACC']
        })
        self.mapping_df = pd.DataFrame({'figi_code': ['AAA'], 'code': ['A']})

    @patch('investment.core.portfolio.LocalDataSource')
    def test_get_holdings(self, MockLocal):
        MockLocal.return_value.get_security_mapping.return_value = self.mapping_df
        with patch.object(Portfolio, 'transactions', new_callable=PropertyMock, return_value=self.transactions_df):
            self.portfolio._get_holdings()
            self.assertEqual(self.portfolio.holdings['quantity'].iloc[-1], 3)
            self.assertIn('base_value', self.portfolio.holdings.columns)

    @patch('investment.core.portfolio.LocalDataSource')
    def test_prepare_holdings_timeseries(self, MockLocal):
        MockLocal.return_value.get_security_mapping.return_value = self.mapping_df
        with patch.object(Portfolio, 'transactions', new_callable=PropertyMock, return_value=self.transactions_df):
            self.portfolio._get_holdings()
            df = self.portfolio._prepare_holdings_timeseries()
            self.assertFalse(df.empty)
            self.assertIn('quantity', df.columns)

if __name__ == '__main__':
    unittest.main()
