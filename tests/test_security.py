import unittest
from unittest.mock import patch

from investment.core.security.base import BaseSecurity
from investment.core.security.currency_cross import CurrencyCross
from investment.core.security.equity import Equity
from investment.core.security.etf import ETF
from investment.core.security.fund import Fund
from investment.core.security.composite import Composite
from investment.core.security.generic import Generic

class BaseSecurityTest(unittest.TestCase):
    def setUp(self):
        self.security = BaseSecurity.model_construct(
            entity_type='equity',
            code='TEST',
            figi_code='FIGI1',
            name='Test Security',
            reporting_currency='USD',
            currency='USD',
            yahoo_finance_code='TEST',
            bloomberg_code='TEST',
            multiplier=1.0
        )

    def test_get_file_path(self):
        path = self.security.get_file_path(
            datasource_name='yahoo_finance',
            intraday=False,
            series_type='price_history'
        )
        self.assertTrue(path.endswith('/TEST-daily-price_history.csv'))

    def test_convert_to_currency_same_currency(self):
        result = self.security.convert_to_currency('USD')
        self.assertIs(result, self.security)

    @patch('investment.core.security.base.Composite')
    def test_convert_to_currency_different_currency(self, MockComposite):
        composite_instance = MockComposite.return_value
        result = self.security.convert_to_currency('EUR')
        MockComposite.assert_called_once()
        self.assertEqual(result, composite_instance)

    @patch('investment.core.security.base.ReturnsCalculator')
    @patch.object(BaseSecurity, 'get_price_history')
    def test_get_returns_invokes_calculator(self, mock_ph, MockRC):
        df = mock_ph.return_value = unittest.mock.MagicMock()
        instance = MockRC.return_value
        self.security.get_returns()
        MockRC.assert_called_once()
        instance.calculate.assert_called_once_with(df=df)

    @patch('investment.core.security.base.RealisedVolatilityCalculator')
    @patch.object(BaseSecurity, 'get_price_history')
    def test_get_realised_volatility_invokes_calculator(self, mock_ph, MockRV):
        df = mock_ph.return_value = unittest.mock.MagicMock()
        instance = MockRV.return_value
        self.security.get_realised_volatility()
        MockRV.assert_called_once()
        instance.calculate.assert_called_once_with(df=df)

class SecuritySubclassTest(unittest.TestCase):
    def test_entity_types(self):
        eq = Equity.model_construct(entity_type='equity', code='EQ', figi_code='F1', name='E', reporting_currency='USD', currency='USD', yahoo_finance_code='EQ', bloomberg_code='EQ', multiplier=1.0, isin_code='ISIN1')
        etf = ETF.model_construct(entity_type='etf', code='ET', figi_code='F2', name='E2', reporting_currency='USD', currency='USD', yahoo_finance_code='ET', bloomberg_code='ET', multiplier=1.0, isin_code='ISIN2')
        fund = Fund.model_construct(entity_type='fund', code='FU', figi_code='F3', name='F', reporting_currency='USD', currency='USD', yahoo_finance_code='FU', bloomberg_code='FU', multiplier=1.0, isin_code='ISIN3')
        cc = CurrencyCross.model_construct(entity_type='currency_cross', code='EURUSD', name='EURUSD', reporting_currency='USD', currency='USD', currency_vs='USD')
        self.assertEqual(eq.entity_type, 'equity')
        self.assertEqual(etf.entity_type, 'etf')
        self.assertEqual(fund.entity_type, 'fund')
        self.assertEqual(cc.entity_type, 'currency_cross')

class CompositeTest(unittest.TestCase):
    def setUp(self):
        base = BaseSecurity.model_construct(
            entity_type='equity',
            code='BASE',
            figi_code='FIGI',
            name='Base',
            reporting_currency='USD',
            currency='USD',
            yahoo_finance_code='BASE',
            bloomberg_code='BASE',
            multiplier=1.0
        )
        cc = CurrencyCross.model_construct(
            entity_type='currency_cross',
            code='EURUSD',
            name='EURUSD',
            reporting_currency='USD',
            currency='USD',
            currency_vs='USD'
        )
        self.comp = Composite.model_construct(
            entity_type='composite',
            security=base,
            currency_cross=cc,
            code='BASE_USD',
            reporting_currency='USD',
            currency='USD',
            multiplier=1.0
        )

    def test_repr(self):
        rep = repr(self.comp)
        self.assertIn('Composite', rep)
        self.assertIn('security=BASE', rep)
        self.assertIn('currency_cross=EURUSD', rep)

    @patch.object(BaseSecurity, 'get_price_history')
    @patch.object(CurrencyCross, 'get_price_history')
    def test_get_price_history(self, mock_ccy, mock_sec):
        dates = pd.date_range('2020-01-01', periods=2)
        mock_sec.return_value = pd.DataFrame({'open':[1,2],'close':[1.1,2.2]}, index=dates)
        mock_ccy.return_value = pd.DataFrame({'open':[0.5,0.6],'close':[0.51,0.61]}, index=dates)
        df = self.comp.get_price_history()
        expected_open = mock_sec.return_value['open'] * mock_ccy.return_value['open']
        expected_close = mock_sec.return_value['close'] * mock_ccy.return_value['close']
        self.assertTrue((df['open'] == expected_open).all())
        self.assertTrue((df['close'] == expected_close).all())

class GenericTest(unittest.TestCase):
    @patch('investment.core.security.generic.LocalDataSource')
    def test_generic_loads_security(self, MockLocal):
        base = BaseSecurity.model_construct(
            entity_type='equity',
            code='GEN',
            figi_code='F4',
            name='Gen',
            reporting_currency='USD',
            currency='USD',
            yahoo_finance_code='GEN',
            bloomberg_code='GEN',
            multiplier=1.0
        )
        MockLocal.return_value.load_generic_security.return_value = base
        gen = Generic(code='GEN')
        MockLocal.return_value.load_generic_security.assert_called_once_with(code='GEN')
        self.assertIs(gen.security, base)

if __name__ == '__main__':
    unittest.main()
