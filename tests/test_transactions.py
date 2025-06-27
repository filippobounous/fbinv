import os
import importlib
import tempfile
import unittest
from unittest import mock

import pandas as pd

from tests.test_utils import FakeLocalDataSource

# environment
TEMP_DIR = tempfile.TemporaryDirectory()
BASE = TEMP_DIR.name
os.environ["BASE_PATH"] = BASE
os.environ["TRANSACTION_PATH"] = os.path.join(BASE, "transactions.xlsx")
os.environ["TRANSACTION_SHEET_NAME"] = "Sheet1"
os.environ["DEFAULT_NAME"] = "PORT"

import investment.config as config
importlib.reload(config)

from investment.core.transactions import Transactions

class TransactionsTests(unittest.TestCase):
    def setUp(self):
        patcher_ds = mock.patch('investment.core.transactions.Transactions._load_transactions')
        self.mock_load = patcher_ds.start()
        self.addCleanup(patcher_ds.stop)
        self.mock_load.return_value = pd.DataFrame()

    def test_extract_and_save_investment_transactions(self):
        """Extract investment transactions and save them to CSV."""
        data = pd.DataFrame({
            'Category': ['Investments', 'Investments'],
            'Description': ['AAA B 2 100 USD', 'BBB S 1 50 USD'],
            'Origin': ['Acc1GBP', 'Acc1GBP'],
            'Date': [pd.Timestamp('2021-01-01'), pd.Timestamp('2021-01-02')]
        })
        self.mock_load.return_value = data
        tr = Transactions(code='PORT', portfolio_path=BASE)
        tr.extract_and_save_investment_transactions()
        df = pd.read_csv(os.path.join(BASE, 'PORT-transactions.csv'), parse_dates=['as_of_date'])
        self.assertEqual(len(df), 2)
        self.assertIn('figi_code', df.columns)
        self.assertIn('account', df.columns)

    def test_load_and_save_cash_positions(self):
        """Aggregate and persist cash position information."""
        data = pd.DataFrame({
            'Date': [pd.Timestamp('2021-01-01'), pd.Timestamp('2021-01-02'), pd.Timestamp('2021-01-01'), pd.Timestamp('2021-01-02')],
            'Currency': ['USD', 'USD', 'EUR', 'EUR'],
            'Net Value': [100, 150, 200, 210]
        })
        self.mock_load.return_value = data
        tr = Transactions(code='PORT', portfolio_path=BASE)
        tr.load_and_save_cash_positions()
        df = pd.read_csv(os.path.join(BASE, 'PORT-cash.csv'), parse_dates=['as_of_date'])
        self.assertEqual(len(df), 4)
        self.assertIn('change', df.columns)

    def test_update_runs_helpers(self):
        """Update should call both extraction helper methods once."""
        tr = Transactions(code='PORT', portfolio_path=BASE)
        with mock.patch.object(tr, 'extract_and_save_investment_transactions') as m1, \
             mock.patch.object(tr, 'load_and_save_cash_positions') as m2:
            tr.update()
            m1.assert_called_once()
            m2.assert_called_once()

    def test_load_transactions_reads_excel(self):
        """_load_transactions reads data from Excel via pandas."""
        with mock.patch('pandas.read_excel', return_value=pd.DataFrame()) as re:
            tr = Transactions(code='PORT', file_path='file.xlsx', sheet_name='S1')
            df = tr._load_transactions()
            re.assert_called_once_with('file.xlsx', sheet_name='S1')
            self.assertTrue(isinstance(df, pd.DataFrame))

    def test_extract_transactions_empty(self):
        """No investment rows should yield an empty transactions file."""
        data = pd.DataFrame({'Category': ['Other'], 'Description': ['xxx'], 'Origin': ['Acc'], 'Date':[pd.Timestamp('2021-01-01')]})
        self.mock_load.return_value = data
        tr = Transactions(code='PORT', portfolio_path=BASE)
        tr.extract_and_save_investment_transactions()
        df = pd.read_csv(os.path.join(BASE, 'PORT-transactions.csv'))
        self.assertTrue(df.empty)
