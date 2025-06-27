import os
import importlib
import tempfile
import unittest
from unittest import mock

import pandas as pd

from test_utils import FakeLocalDataSource

# environment
TEMP_DIR = tempfile.TemporaryDirectory()
BASE = TEMP_DIR.name
os.environ["BASE_PATH"] = BASE
os.environ["TRANSACTION_PATH"] = os.path.join(BASE, "transactions.xlsx")
os.environ["TRANSACTION_SHEET_NAME"] = "Sheet1"
os.environ["DEFAULT_NAME"] = "PORT"

import investment.config as config
importlib.reload(config)

from investment.core.security import base as base_sec
from investment.core.security import composite, generic
from investment.core.security.registry import security_registry

class SecurityTests(unittest.TestCase):
    def setUp(self):
        patchers = [
            mock.patch('investment.core.mapping.BaseMappingEntity._local_datasource', FakeLocalDataSource),
            mock.patch('investment.datasource.local.LocalDataSource', FakeLocalDataSource),
            mock.patch('investment.datasource.registry.LocalDataSource', FakeLocalDataSource),
            mock.patch('investment.core.portfolio.LocalDataSource', FakeLocalDataSource),
        ]
        for p in patchers:
            p.start()
            self.addCleanup(p.stop)

    def test_get_file_path(self):
        """Security.get_file_path should build the expected CSV path."""
        sec = base_sec.BaseSecurity(entity_type='equity', code='AAA', name='AAA', figi_code='AAA111',
                                     reporting_currency='USD', currency='USD', multiplier=1.0)
        expected = f"{config.TIMESERIES_DATA_PATH}/price_history/local/equity/AAA-daily-price_history.csv"
        self.assertEqual(sec.get_file_path('local', False, 'price_history'), expected)

    def test_convert_to_currency(self):
        """Converting to another currency returns a Composite security."""
        sec = generic.Generic('AAA')
        # same currency
        self.assertIs(sec.convert_to_currency('USD'), sec)
        # different currency returns Composite
        result = sec.convert_to_currency('GBP')
        self.assertIsInstance(result, composite.Composite)
        self.assertEqual(result.currency_cross.code, 'USDGBP')

    def test_generic_returns_correct_class(self):
        """Generic security instantiation matches registry class."""
        obj = generic.Generic('AAA')
        self.assertEqual(type(obj), security_registry['equity'])

    def test_composite_price_history(self):
        """Composite price history multiplies security and FX series."""
        dates = pd.date_range('2021-01-01', periods=2)
        sec_df = pd.DataFrame({'open': [1.0, 2.0], 'close': [1.0, 2.0]}, index=dates)
        sec_df.index.name = 'as_of_date'
        ccy_df = pd.DataFrame({'open': [2.0, 2.0], 'close': [2.0, 2.0]}, index=dates)
        ccy_df.index.name = 'as_of_date'

        with mock.patch('investment.core.security.base.BaseSecurity.get_price_history', return_value=sec_df):
            with mock.patch('investment.core.security.currency_cross.CurrencyCross.get_price_history', return_value=ccy_df):
                sec = generic.Generic('AAA')
                comp = sec.convert_to_currency('GBP')
                df = comp.get_price_history()
                self.assertTrue((df['open'] == sec_df['open'] * ccy_df['open']).all())
                self.assertTrue((df['close'] == sec_df['close'] * ccy_df['close']).all())

    def test_get_price_history_uses_datasource(self):
        """Ensure datasource helper is consulted when fetching prices."""
        sec = generic.Generic("AAA")
        fake_ds = mock.Mock()
        fake_ds.get_price_history.return_value = pd.DataFrame()
        with mock.patch("investment.core.security.base.get_datasource", return_value=fake_ds) as m_ds:
            sec.get_price_history(datasource="dummy", local_only=False, intraday=True)
            m_ds.assert_called_once_with(datasource="dummy")
        fake_ds.get_price_history.assert_called_once_with(security=sec, intraday=True, local_only=False)

    def test_composite_repr(self):
        """Composite.__repr__ includes security and currency cross codes."""
        sec = generic.Generic("AAA")
        comp = sec.convert_to_currency("GBP")
        rep = repr(comp)
        self.assertEqual(rep, f"Composite(entity_type=composite, security={sec.code}, currency_cross={comp.currency_cross.code})")
