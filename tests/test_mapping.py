import os
import tempfile
import importlib
import unittest

import pandas as pd
from typing import Optional

from tests.test_utils import FakeLocalDataSource

# prepare environment before importing modules
TEMP_DIR = tempfile.TemporaryDirectory()
BASE = TEMP_DIR.name
os.environ["BASE_PATH"] = BASE
os.environ["TRANSACTION_PATH"] = os.path.join(BASE, "transactions.xlsx")
os.environ["TRANSACTION_SHEET_NAME"] = "Sheet1"
os.environ["DEFAULT_NAME"] = "PORT"

import investment.config as config
importlib.reload(config)

from investment.core import mapping

class MappingTests(unittest.TestCase):
    def setUp(self):
        patcher1 = unittest.mock.patch(
            'investment.core.mapping.BaseMappingEntity._local_datasource',
            FakeLocalDataSource
        )
        patcher2 = unittest.mock.patch(
            'investment.datasource.local.LocalDataSource',
            FakeLocalDataSource
        )
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        patcher1.start()
        patcher2.start()

    def test_unknown_entity_type_raises(self):
        """Creating with an unknown entity type should raise KeyError."""
        class Dummy(mapping.BaseMappingEntity):
            entity_type: str = 'unknown'
        with self.assertRaises(KeyError):
            Dummy(code='X')

    def test_portfolio_mapping_loads_attributes(self):
        """Portfolio mapping populates owner attributes as expected."""
        from investment.core.portfolio import Portfolio
        p = Portfolio('PORT')
        self.assertEqual(p.owner, 'Tester')
        self.assertFalse(p.has_cash)

    def test_returns_and_volatility(self):
        """Return and volatility helpers operate on price history."""
        class Dummy(mapping.BaseMappingEntity):
            entity_type: str = 'portfolio'
            owner: Optional[str] = None
            has_cash: Optional[bool] = None

            def get_price_history(self, datasource=None, local_only=True, intraday=False):
                dates = pd.date_range('2024-01-01', periods=25)
                df = pd.DataFrame({
                    'open': range(1, 26),
                    'high': range(2, 27),
                    'low': range(0, 25),
                    'close': range(1, 26),
                }, index=dates)
                df.index.name = 'as_of_date'
                return df

        obj = Dummy(code='PORT')
        rets = obj.get_returns(ret_win_size=1)
        self.assertFalse(rets.empty)
        self.assertIn('return', rets.columns)
        vol = obj.get_realised_volatility(rv_win_size=2)
        self.assertFalse(vol.empty)
        self.assertIn('volatility', vol.columns)

    def test_calculation_helpers_called_with_expected_args(self):
        """Verify ReturnsCalculator and RealisedVolatilityCalculator usage."""
        class Dummy(mapping.BaseMappingEntity):
            entity_type: str = 'portfolio'
            def get_price_history(self, datasource=None, local_only=True, intraday=False):
                return pd.DataFrame({'close': [1.0, 2.0], 'open': [1.0, 2.0], 'high': [1.0,2.0], 'low':[1.0,2.0]}, index=pd.date_range('2024-01-01', periods=2))
        obj = Dummy(code='PORT')
        with mock.patch.object(obj, 'get_price_history', wraps=obj.get_price_history) as ph, \
             mock.patch('investment.core.mapping.ReturnsCalculator') as RC, \
             mock.patch('investment.core.mapping.RealisedVolatilityCalculator') as VC:
            RC.return_value.calculate.return_value = pd.DataFrame()
            VC.return_value.calculate.return_value = pd.DataFrame()
            obj.get_returns(use_ln_ret=False, ret_win_size=2)
            ph.assert_called_with(datasource=None, local_only=True, intraday=False)
            RC.assert_called_once_with(ret_win_size=2, use_ln_ret=False)
            RC.return_value.calculate.assert_called_once()
            obj.get_realised_volatility(rv_win_size=2)
            VC.assert_called_once()
            VC.return_value.calculate.assert_called_once()

    def test_portfolio_init_uses_local_datasource(self):
        """Portfolio initialization loads mapping from the local datasource."""
        with mock.patch.object(FakeLocalDataSource, 'load_portfolio', wraps=FakeLocalDataSource.load_portfolio) as lp:
            from investment.core.portfolio import Portfolio
            Portfolio('PORT')
            lp.assert_called_once()
