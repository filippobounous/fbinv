"""Unit tests for investment datasource modules."""

import datetime
from unittest import mock
from unittest import TestCase

import pandas as pd

from investment.datasource import (
    AlphaVantageDataSource,
    BloombergDataSource,
    FinancialTimesDataSource,
    LocalDataSource,
    OpenFigiDataSource,
    TwelveDataDataSource,
    YahooFinanceDataSource,
)
from investment.core.security import CurrencyCross, Equity
from investment.datasource.test import TestDataSource
from investment.utils.exceptions import (
    DataSourceMethodException, AlphaVantageException, TwelveDataException,
)

class BaseDataSourceTestCase(TestCase):
    """Base class that patches the local datasource used by security objects."""

    def setUp(self):
        patcher = mock.patch(
            "investment.core.mapping.BaseMappingEntity._local_datasource",
            TestDataSource,
        )
        self.addCleanup(patcher.stop)
        patcher.start()

class AlphaVantageTests(BaseDataSourceTestCase):
    """Tests for :class:`AlphaVantageDataSource`."""

    def test_check_response_rate_limit(self):
        """Verify that rate limit messages raise :class:`AlphaVantageException`."""
        ds = AlphaVantageDataSource()
        with self.assertRaises(AlphaVantageException):
            ds._check_response({"Information": "standard API rate limit"})

    def test_check_response_premium(self):
        """Premium endpoint messages should also raise :class:`AlphaVantageException`."""
        ds = AlphaVantageDataSource()
        with self.assertRaises(AlphaVantageException):
            ds._check_response({"Information": "This is a premium endpoint."})

    def test_default_start_and_end_date(self):
        """Check the fallback start and end date calculation logic."""
        ds = AlphaVantageDataSource()
        df = pd.DataFrame({"as_of_date": pd.to_datetime(["2020-01-01", "2020-01-02"])})
        with mock.patch("investment.datasource.alpha_vantage.today_midnight", return_value=datetime.datetime(2020, 1, 10)):
            start, end = ds._default_start_and_end_date(df=df, symbol="AAA", intraday=False)
        self.assertEqual(start, pd.Timestamp("2020-01-01"))
        self.assertEqual(end, datetime.datetime(2020, 1, 9))

class PlaceholderDataSourceTests(BaseDataSourceTestCase):
    """Tests for datasources that only raise :class:`DataSourceMethodException`."""

    def setUp(self):
        super().setUp()
        self.cc = CurrencyCross("EURUSD")
        self.eq = Equity("AAA")
        self.start = datetime.datetime(2020, 1, 1)
        self.end = datetime.datetime(2020, 1, 2)

    def assert_all_methods_raise(self, ds, include_update=True):
        methods = [
            ds._get_currency_cross_price_history_from_remote,
            ds._get_equity_price_history_from_remote,
            ds._get_etf_price_history_from_remote,
            ds._get_fund_price_history_from_remote,
        ]
        for method in methods:
            with self.assertRaises(DataSourceMethodException):
                method(
                    security=self.eq if "equity" in method.__name__ else self.cc,
                    intraday=False,
                    start_date=self.start,
                    end_date=self.end,
                )
        if include_update:
            with self.assertRaises(DataSourceMethodException):
                ds._update_security_mapping(pd.DataFrame({"figi_code": ["AAA"]}))

    def test_bloomberg_methods_raise(self):
        """All Bloomberg methods should raise :class:`DataSourceMethodException`."""
        self.assert_all_methods_raise(BloombergDataSource())

    def test_financial_times_methods_raise(self):
        """Financial Times datasource methods should raise :class:`DataSourceMethodException`."""
        self.assert_all_methods_raise(FinancialTimesDataSource())

    def test_open_figi_methods_raise(self):
        """OpenFIGI methods, except mapping updates, raise :class:`DataSourceMethodException`."""
        self.assert_all_methods_raise(OpenFigiDataSource(), include_update=False)

class LocalDataSourceTests(BaseDataSourceTestCase):
    """Tests for :class:`LocalDataSource`."""

    def test_load_valid_row(self):
        """Loading a row removes null columns and returns the expected record."""
        ds = LocalDataSource()
        df = pd.DataFrame({"code": ["AAA"], "name": ["test"], "value": [1], "null": [pd.NA]})
        result = ds._load(df, Equity("AAA"))
        self.assertEqual(result["name"], "test")
        self.assertNotIn("null", result)

    def test_load_duplicate_rows(self):
        """Duplicate codes in the dataframe should result in an exception."""
        ds = LocalDataSource()
        df = pd.DataFrame({"code": ["AAA", "AAA"], "name": ["a", "b"]})
        with self.assertRaises(Exception):
            ds._load(df, Equity("AAA"))

    def test_load_missing_row(self):
        """Attempting to load an empty dataframe should raise an exception."""
        ds = LocalDataSource()
        df = pd.DataFrame({"code": [], "name": []})
        with self.assertRaises(Exception):
            ds._load(df, Equity("AAA"))

    def test_get_all_portfolios_and_securities(self):
        """Ensure helper methods return portfolio names and security codes."""
        ds = LocalDataSource()
        with mock.patch.object(ds, "_get_file_names_in_path", return_value={"AAA": datetime.datetime(2020,1,1)}):
            result = ds.get_all_portfolios()
        self.assertIn("AAA", result)
        with mock.patch.object(ds, "get_security_mapping", return_value=pd.DataFrame({"code": ["AAA"]})):
            result2 = ds.get_all_securities()
        self.assertEqual(result2, ["AAA"])

class OpenFigiDataSourceTests(BaseDataSourceTestCase):
    """Tests for :class:`OpenFigiDataSource`."""

    def test_update_security_mapping(self):
        """Security mapping update should include any returned ticker field."""
        ds = OpenFigiDataSource()
        df = pd.DataFrame({"figi_code": ["AAA"]})
        sample_response = [{"data": [{"ticker": "AAA"}]}]
        with mock.patch.object(ds, "_request", return_value=sample_response):
            result = ds._update_security_mapping(df)
        self.assertIn("ticker", result.columns)
        self.assertEqual(result.loc[0, "figi"], "AAA")

class YahooFinanceDataSourceTests(BaseDataSourceTestCase):
    """Tests for :class:`YahooFinanceDataSource`."""

    def test_format_price_history_from_remote(self):
        """Formatting converts the multi-indexed DataFrame to standard columns."""
        ds = YahooFinanceDataSource()
        df = pd.DataFrame({("Open", ""): [1], ("Close", ""): [2]}, index=pd.DatetimeIndex(["2020-01-01"], name="Date"))
        result = ds._format_price_history_from_remote(df)
        self.assertEqual(list(result.columns), ["as_of_date", "open", "close"])

    def test_time_series_uses_yfinance(self):
        """Verify that ``yfinance.download`` is invoked with the expected parameters."""
        ds = YahooFinanceDataSource()
        start = datetime.datetime(2020, 1, 1)
        end = datetime.datetime(2020, 1, 2)
        with mock.patch("yfinance.download", return_value=pd.DataFrame()) as dl:
            ds._time_series(symbol="AAA", intraday=False, start_date=start, end_date=end)
        dl.assert_called_once()
        args, kwargs = dl.call_args
        self.assertEqual(args[0], "AAA")
        self.assertEqual(kwargs["interval"], "1d")

    def test_default_start_and_end_date(self):
        """Date calculation should return previous day's end when data exists."""
        ds = YahooFinanceDataSource()
        df = pd.DataFrame({"as_of_date": pd.to_datetime(["2020-01-05", "2020-01-06"])})
        with mock.patch("investment.datasource.yahoo_finance.today_midnight", return_value=datetime.datetime(2020,1,10)):
            start, end = ds._default_start_and_end_date(df=df, symbol="AAA", intraday=False)
        self.assertEqual(start, pd.Timestamp("2020-01-05"))
        self.assertEqual(end, datetime.datetime(2020,1,9))

class TwelveDataDataSourceTests(BaseDataSourceTestCase):
    """Tests for :class:`TwelveDataDataSource`."""

    def test_interval_code(self):
        """Correct interval codes should be returned for intraday and daily."""
        ds = TwelveDataDataSource()
        self.assertEqual(ds._interval_code(True), "1min")
        self.assertEqual(ds._interval_code(False), "1day")

    def test_earliest_date_column(self):
        """The earliest date column should reflect the intraday flag."""
        ds = TwelveDataDataSource()
        self.assertEqual(ds._earliest_date_column(True), "earliest_date_intraday_True")

    def test_format_price_history_from_remote(self):
        """Formatting should add an ``as_of_date`` column."""
        ds = TwelveDataDataSource()
        df = pd.DataFrame(index=pd.DatetimeIndex(["2020-01-01"], name="datetime"))
        df["close"] = [1]
        result = ds._format_price_history_from_remote(df)
        self.assertIn("as_of_date", result.columns)

    def test_get_dates(self):
        """Date expansion should add a buffer to the end date."""
        ds = TwelveDataDataSource()
        start = datetime.datetime(2020,1,1)
        end = datetime.datetime(2020,1,3)
        result = ds._get_dates(start_date=start, end_date=end, intraday=False)
        self.assertEqual(result, [(start, end + datetime.timedelta(days=2))])

    def test_default_start_and_end_date_missing(self):
        """An error is raised if the earliest start date cannot be determined."""
        ds = TwelveDataDataSource()
        df = pd.DataFrame()
        with mock.patch.object(ds, "_check_start_date_for_security", return_value=None):
            with self.assertRaises(TwelveDataException):
                ds._default_start_and_end_date(df=df, symbol="AAA", intraday=False)

    def test_default_start_and_end_date_success(self):
        """Valid start date results in expected date range calculation."""
        ds = TwelveDataDataSource()
        df = pd.DataFrame()
        with mock.patch.object(ds, "_check_start_date_for_security", return_value=datetime.datetime(2020,1,1)), \
             mock.patch("investment.datasource.twelve_data.today_midnight", return_value=datetime.datetime(2020,1,10)):
            start, end = ds._default_start_and_end_date(df=df, symbol="AAA", intraday=False)
        self.assertEqual(start, datetime.datetime(2020,1,1))
        self.assertEqual(end, datetime.datetime(2020,1,9))

