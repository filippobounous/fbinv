from unittest import TestCase
from unittest import mock

import pandas as pd

from investment import config
from investment.datasource.test import TestDataSource

class SecurityTestCase(TestCase):
    def setUp(self):
        self.ds_patch = mock.patch(
            "investment.core.mapping.BaseMappingEntity._local_datasource",
            TestDataSource,
        )
        self.ds_patch.start()

    def tearDown(self):
        self.ds_patch.stop()

    def test_get_file_path(self):
        from investment.core.security import Equity

        sec = Equity("TEST")
        path = sec.get_file_path(
            datasource_name="local", intraday=False, series_type="price_history"
        )
        expected = (
            f"{config.TIMESERIES_DATA_PATH}/price_history/local/"
            f"equity/code-daily-price_history.csv"
        )
        self.assertEqual(path, expected)

    def test_convert_to_currency(self):
        from investment.core.security import Equity

        sec = Equity("TEST")
        self.assertIs(sec.convert_to_currency("USD"), sec)
        with mock.patch(
            "investment.core.security.composite.Composite"
        ) as MockComposite:
            comp_instance = MockComposite.return_value
            result = sec.convert_to_currency("EUR")
            MockComposite.assert_called_once_with(security=sec, composite_currency="EUR")
            self.assertIs(result, comp_instance)

    def test_get_price_history_self_currency(self):
        from investment.core.security import Equity

        sec = Equity("TEST")
        df = pd.DataFrame({
            "as_of_date": [pd.Timestamp("2020-01-01")],
            "open": [1],
            "close": [2],
        })
        ds = TestDataSource()
        with mock.patch(
            "investment.core.security.base.get_datasource", return_value=ds
        ) as mock_gds, mock.patch.object(ds, "get_price_history", return_value=df) as gp:
            result = sec.get_price_history(datasource=ds)
        mock_gds.assert_called_once_with(datasource=ds)
        gp.assert_called_once_with(security=sec, intraday=False, local_only=True)
        self.assertTrue(result.equals(df))

    def test_get_price_history_other_currency(self):
        from investment.core.security import Equity

        sec = Equity("TEST")
        comp_df = pd.DataFrame({"open": [2], "close": [3]})
        comp = mock.Mock()
        comp.get_price_history.return_value = comp_df
        with mock.patch.object(sec, "convert_to_currency", return_value=comp) as mc:
            result = sec.get_price_history(currency="EUR")
        mc.assert_called_once_with(currency="EUR")
        comp.get_price_history.assert_called_once_with(
            datasource=None, local_only=True, intraday=False
        )
        self.assertIs(result, comp_df)

    def test_composite_get_price_history(self):
        from investment.core.security import Equity, CurrencyCross
        from investment.core.security.composite import Composite

        sec = Equity("AAA")
        cc = CurrencyCross("USDEUR")
        ph_sec = pd.DataFrame(
            {
                "as_of_date": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-02")],
                "open": [1.0, 2.0],
                "close": [2.0, 3.0],
            }
        )
        ph_cc = pd.DataFrame(
            {
                "as_of_date": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-02")],
                "open": [10.0, 20.0],
                "close": [10.0, 20.0],
            }
        )
        sec.get_price_history = mock.Mock(return_value=ph_sec)
        cc.get_price_history = mock.Mock(return_value=ph_cc)
        comp = Composite.construct(
            security=sec,
            currency_cross=cc,
            entity_type="composite",
            code="AAA_EUR",
        )
        result = comp.get_price_history()
        expected = pd.DataFrame(
            {
                "open": [10.0, 40.0],
                "close": [20.0, 60.0],
            },
            index=pd.to_datetime(["2020-01-01", "2020-01-02"]),
        )
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))

    def test_generic_factory(self):
        from investment.core.security import Generic, Equity
        with mock.patch(
            "investment.datasource.local.LocalDataSource.load_generic_security",
            return_value=Equity("TEST"),
        ) as lg:
            sec = Generic("TEST")
        lg.assert_called_once()
        self.assertIsInstance(sec, Equity)

    def test_security_registry(self):
        from investment.core.security.registry import security_registry
        from investment.core.security import Equity, ETF, Fund, CurrencyCross, Composite

        self.assertIs(security_registry["equity"], Equity)
        self.assertIs(security_registry["etf"], ETF)
        self.assertIs(security_registry["fund"], Fund)
        self.assertIs(security_registry["currency_cross"], CurrencyCross)
        self.assertIs(security_registry["composite"], Composite)


