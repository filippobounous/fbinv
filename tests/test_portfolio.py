import os
import importlib
import tempfile
import unittest
from unittest import mock

import pandas as pd

from test_utils import FakeLocalDataSource

TEMP_DIR = tempfile.TemporaryDirectory()
BASE = TEMP_DIR.name
os.environ["BASE_PATH"] = BASE
os.environ["TRANSACTION_PATH"] = os.path.join(BASE, "transactions.xlsx")
os.environ["TRANSACTION_SHEET_NAME"] = "Sheet1"
os.environ["DEFAULT_NAME"] = "PORT"

import investment.config as config
importlib.reload(config)

from investment.core.portfolio import Portfolio

class PortfolioTests(unittest.TestCase):
    def setUp(self):
        patchers = [
            mock.patch('investment.core.mapping.BaseMappingEntity._local_datasource', FakeLocalDataSource),
            mock.patch('investment.datasource.local.LocalDataSource', FakeLocalDataSource),
            mock.patch('investment.core.portfolio.LocalDataSource', FakeLocalDataSource),
        ]
        for p in patchers:
            p.start()
            self.addCleanup(p.stop)

        # create transactions csv
        tx = pd.DataFrame({
            'figi_code': ['AAA', 'BBB'],
            'quantity': [2, -1],
            'price': [100, 50],
            'account': ['Acc1', 'Acc1'],
            'value': [200, -50],
            'currency': ['USD', 'USD'],
            'as_of_date': [pd.Timestamp('2021-01-01'), pd.Timestamp('2021-01-02')]
        })
        tx.to_csv(os.path.join(BASE, 'PORT-transactions.csv'), index=False)

    def test_holdings_loaded(self):
        """Holdings dataframe loads correctly from transactions file."""
        p = Portfolio('PORT')
        self.assertFalse(p.holdings.empty)
        self.assertIn('code', p.holdings.columns)

    def test_prepare_holdings_timeseries(self):
        """Prepared holdings timeseries includes expected columns."""
        p = Portfolio('PORT')
        df = p._prepare_holdings_timeseries()
        self.assertIn('quantity', df.columns)
        self.assertEqual(df.iloc[0]['figi_code'], 'AAA')

    def test_get_price_history_warns_intraday(self):
        """Requesting intraday data emits a UserWarning."""
        p = Portfolio('PORT')
        with self.assertWarns(UserWarning):
            p.get_price_history(intraday=True)

    def test_get_path(self):
        """_get_path builds the path to the transactions CSV."""
        p = Portfolio("PORT")
        expected = f"{config.PORTFOLIO_PATH}/PORT-transactions.csv"
        self.assertEqual(p._get_path("transactions"), expected)

    def test_update_raises_when_code_mismatch(self):
        """Portfolio.update raises if Transactions code differs."""
        p = Portfolio("PORT")
        with mock.patch("investment.core.portfolio.Transactions") as MockTr:
            MockTr.return_value.code = "OTHER"
            with self.assertRaises(Exception):
                p.update()
            MockTr.return_value.update.assert_not_called()

    def test_combine_security_price_history(self):
        """Combining holdings with security prices calculates values."""
        p = Portfolio("PORT")
        df_holdings = pd.DataFrame({
            "as_of_date": [pd.Timestamp("2021-01-01")],
            "currency": ["USD"],
            "figi_code": ["AAA"],
            "code": ["AAA"],
            "quantity": [2.0],
            "average": [100.0],
            "entry_value": [200.0],
        })
        ph = pd.DataFrame({"open": [10.0], "close": [12.0]}, index=[pd.Timestamp("2021-01-01")])
        ph.index.name = "as_of_date"
        mock_sec = mock.Mock(code="AAA")
        mock_sec.get_price_history.return_value = ph
        with mock.patch.object(p, "all_securities", [mock_sec]):
            result = p._combine_with_security_price_history(df_holdings)
            row = result.reset_index().iloc[0]
            self.assertEqual(row["open_value"], 20.0)
            self.assertEqual(row["close_value"], 24.0)
            self.assertEqual(row["net_value"], 24.0 - 200.0)

