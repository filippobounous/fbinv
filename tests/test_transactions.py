import unittest
from unittest.mock import patch
import pandas as pd
from investment.core.transactions import Transactions

class TransactionsTest(unittest.TestCase):
    def setUp(self):
        self.tr = Transactions(code='TEST', file_path='dummy.xlsx')

    def test_extract_and_save_investment_transactions(self):
        df = pd.DataFrame({
            'Category': ['Investments'],
            'Description': ['AAA B 2 10 USD'],
            'Origin': ['ACC001'],
            'Date': ['2024-01-01']
        })
        captured = {}
        def fake_to_csv(self, path, index=False):
            captured['df'] = self.copy()
            captured['path'] = path
        with patch.object(Transactions, '_load_transactions', return_value=df), \
             patch('pandas.DataFrame.to_csv', new=fake_to_csv):
            self.tr.extract_and_save_investment_transactions()
        self.assertIn('figi_code', captured['df'].columns)
        self.assertEqual(captured['path'], f'{self.tr.portfolio_path}/{self.tr.code}-transactions.csv')

    def test_load_and_save_cash_positions(self):
        df = pd.DataFrame({
            'Currency': ['USD', 'USD'],
            'Net Value': [1, 2],
            'Date': ['2024-01-01', '2024-01-02']
        })
        captured = {}
        def fake_to_csv(self, path, index=False):
            captured['df'] = self.copy()
            captured['path'] = path
        with patch.object(Transactions, '_load_transactions', return_value=df), \
             patch('pandas.DataFrame.to_csv', new=fake_to_csv):
            self.tr.load_and_save_cash_positions()
        self.assertIn('currency', captured['df'].columns)
        self.assertEqual(captured['path'], f'{self.tr.portfolio_path}/{self.tr.code}-cash.csv')

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
