"""Unit tests for the security module and related classes."""

from unittest import TestCase
from unittest import mock

import pandas as pd

from investment import config
from investment.core.security import (
    Composite,
    CurrencyCross,
    Equity,
    ETF,
    Fund,
    Generic,
    security_registry,
)
from investment.datasource.test import TestDataSource

class SecurityTestCase(TestCase):
    """Test cases for security classes and their methods."""
    def setUp(self):
        """Set up the test case environment."""
        # Mock the local datasource to use the test data source
        # This allows us to avoid external dependencies during tests
        # and ensures that the tests are isolated from external data sources.
        # This is particularly useful for testing methods that interact with
        # the datasource, such as getting price history.
        self.ds_patch = mock.patch(
            "investment.core.mapping.BaseMappingEntity._local_datasource",
            TestDataSource,
        )
        self.ds_patch.start()

    def tearDown(self):
        """Clean up after each test case."""
        self.ds_patch.stop()

    def test_get_file_path(self):
        """Test the file path generation for a security."""
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
        """Test converting a security to a different currency."""
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
        """Test getting price history in the security's own currency."""
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
        """Test getting price history in a different currency."""
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
        """Test getting price history for a composite security."""
        sec = Equity("AAA")
        cc = CurrencyCross("EURUSD")
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
        pd.testing.assert_frame_equal(
            result.reset_index(drop=True),
            expected.reset_index(drop=True)
        )

    def test_generic_factory(self):
        """Test the factory method for creating a generic security."""
        with mock.patch(
            "investment.datasource.local.LocalDataSource.load_generic_security",
            return_value=Equity("TEST"),
        ) as lg:
            sec = Generic("TEST")
        lg.assert_called_once()
        self.assertIsInstance(sec, Equity)

    def test_security_registry(self):
        """Test the security registry contains all expected security types."""
        self.assertIs(security_registry["equity"], Equity)
        self.assertIs(security_registry["etf"], ETF)
        self.assertIs(security_registry["fund"], Fund)
        self.assertIs(security_registry["currency_cross"], CurrencyCross)
        self.assertIs(security_registry["composite"], Composite)

    def test_missing_attributes_raises(self):
        """Initialisation fails if datasource data lacks required fields."""
        with mock.patch.object(TestDataSource, "load_security", return_value={}):
            with self.assertRaises(ValueError):
                Equity("MISSING")

    def test_composite_repr(self):
        """Composite __repr__ includes underlying codes."""
        sec = Equity("AAA")
        cc = CurrencyCross("EURUSD")
        comp = Composite(security=sec, currency_cross=cc)
        self.assertEqual(
            repr(comp),
            "Composite(entity_type=composite, security=AAA, currency_cross=EURUSD)"
        )

    def test_get_file_path_open_figi(self):
        """OpenFIGI path uses figi_code and supports intraday."""
        sec = Equity("TEST")
        path = sec.get_file_path(
            datasource_name="open_figi", intraday=True, series_type="price_history"
        )
        expected = (
            f"{config.TIMESERIES_DATA_PATH}/price_history/open_figi/"
            f"equity/figi_code-intraday-price_history.csv"
        )
        self.assertEqual(path, expected)

    def test_composite_price_history_missing_columns(self):
        """Composite returns empty DataFrame if inputs lack OHLC columns."""
        sec = Equity("AAA")
        cc = CurrencyCross("EURUSD")
        sec.get_price_history = mock.Mock(return_value=pd.DataFrame({"open": [1.0]}))
        cc.get_price_history = mock.Mock(return_value=pd.DataFrame({"open": [1.0]}))
        comp = Composite.construct(
            security=sec,
            currency_cross=cc,
            entity_type="composite",
            code="AAA_EUR",
        )
        result = comp.get_price_history()
        self.assertTrue(result.empty)
