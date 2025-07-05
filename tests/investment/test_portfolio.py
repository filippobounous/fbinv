import unittest
from unittest import mock
import pandas as pd

from investment import config
from investment.core.portfolio import Portfolio, Generic
from investment.datasource.test import TestDataSource
from investment.utils import consts

class PortfolioTestCase(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch(
            "investment.core.mapping.BaseMappingEntity._local_datasource",
            TestDataSource,
        )
        self.addCleanup(patcher.stop)
        patcher.start()

    def _make_portfolio(self, **kwargs):
        """Create a Portfolio instance without running validation."""
        with mock.patch(
            "investment.core.mapping.BaseMappingEntity._local_datasource",
            TestDataSource,
        ):
            return Portfolio.construct(code="TEST", entity_type="portfolio", **kwargs)

    def test_get_path(self):
        pf = self._make_portfolio()
        expected = f"{config.PORTFOLIO_PATH}/TEST-transactions.csv"
        self.assertEqual(pf._get_path("transactions"), expected)

    def test_transactions_missing_file(self):
        pf = self._make_portfolio()
        with mock.patch("pandas.read_csv", side_effect=FileNotFoundError):
            with self.assertRaises(Exception):
                _ = pf.transactions

    def test_get_holdings(self):
        tr_df = pd.DataFrame({
            "as_of_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "figi_code": ["AAA", "AAA"],
            "quantity": [10, -5],
            "value": [1000, -550],
            "account": ["ACC1", "ACC1"],
            "currency": ["GBP", "GBP"],
        })
        mapping_df = pd.DataFrame({"figi_code": ["AAA"], "code": ["AAA"]})
        pf = self._make_portfolio()
        with mock.patch("pandas.read_csv", return_value=tr_df), \
             mock.patch("investment.core.portfolio.LocalDataSource.get_security_mapping", return_value=mapping_df):
            pf._get_holdings()
        expected = tr_df.copy()
        expected["cum_quantity"] = expected.groupby("figi_code")["quantity"].cumsum()
        expected["cum_value"] = expected.groupby("figi_code")["value"].cumsum()
        expected["average"] = expected["cum_value"] / expected["cum_quantity"]
        expected = expected[["as_of_date", "figi_code", "cum_quantity", "average", "currency"]]
        expected = expected.rename(columns={"cum_quantity": "quantity"})
        expected["entry_value"] = expected["quantity"] * expected["average"]
        expected = expected.merge(mapping_df, on="figi_code", how="left")
        pd.testing.assert_frame_equal(pf.holdings.reset_index(drop=True), expected.reset_index(drop=True))

    def test_get_cash_filters(self):
        cash_df = pd.DataFrame({
            "as_of_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "account": ["ACC1", "ACC2"],
            "currency": ["GBP", "GBP"],
            "value": [100, 200],
        })
        pf = self._make_portfolio(has_cash=True, account="ACC1", currency="GBP")
        with mock.patch("pandas.read_csv", return_value=cash_df):
            pf._get_cash()
        expected = cash_df.iloc[[0]].reset_index(drop=True)
        pd.testing.assert_frame_equal(pf.cash.reset_index(drop=True), expected)

    def test_prepare_holdings_timeseries(self):
        holdings = pd.DataFrame({
            "as_of_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "figi_code": ["AAA", "AAA"],
            "quantity": [10, 5],
            "average": [100.0, 90.0],
            "currency": ["GBP", "GBP"],
            "entry_value": [1000.0, 450.0],
            "code": ["AAA", "AAA"],
        })
        pf = self._make_portfolio()
        pf.holdings = holdings
        with mock.patch("investment.core.portfolio.today_midnight", return_value=pd.Timestamp("2020-01-02")):
            result = pf._prepare_holdings_timeseries()
        self.assertEqual(len(result), 2)
        self.assertIn("quantity", result.columns)
        self.assertIn("entry_value", result.columns)

    def test_get_holdings_price_history_no_prices(self):
        pf = self._make_portfolio()
        base_df = pd.DataFrame({
            "as_of_date": [pd.Timestamp("2020-01-01")],
            "currency": ["GBP"],
            "figi_code": ["AAA"],
            "code": ["AAA"],
            "quantity": [10.0],
            "average": [100.0],
            "entry_value": [1000.0],
        })
        with mock.patch.object(Portfolio, "_prepare_holdings_timeseries", return_value=base_df), \
             mock.patch.object(Portfolio, "_combine_with_security_price_history", return_value=base_df):
            result = pf.get_holdings_price_history()
        pd.testing.assert_frame_equal(result, base_df)

    def test_get_holdings_price_history_with_prices(self):
        pf = self._make_portfolio()
        base = pd.DataFrame({
            "as_of_date": [pd.Timestamp("2020-01-01")],
            "currency": ["GBP"],
            "figi_code": ["AAA"],
            "code": ["AAA"],
            "quantity": [10.0],
            "average": [100.0],
            "entry_value": [1000.0],
            "open": [101.0],
            "close": [102.0],
            "high": [103.0],
            "low": [99.0],
        })
        base_no_price = base.drop(columns=consts.OHLC)
        with mock.patch.object(Portfolio, "_prepare_holdings_timeseries", return_value=base_no_price), \
             mock.patch.object(Portfolio, "_combine_with_security_price_history", return_value=base):
            result = pf.get_holdings_price_history()
        self.assertIn("open_value", result.columns)
        self.assertEqual(result.loc[0, "open_value"], 1010.0)
        self.assertEqual(result.loc[0, "net_value"], 20.0)

    def test_get_price_history(self):
        pf = self._make_portfolio()
        ph = pd.DataFrame({
            "as_of_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "open_value": [100.0, 200.0],
            "close_value": [110.0, 210.0],
            "net_value": [10.0, 20.0],
            "entry_value": [90.0, 195.0],
        })
        with mock.patch.object(Portfolio, "get_holdings_price_history", return_value=ph):
            result = pf.get_price_history()
        expected = ph.groupby("as_of_date")[[f"{i}_value" for i in consts.OC + ["net", "entry"]]].sum().rename(columns={
            "open_value": "open",
            "close_value": "close",
            "net_value": "net",
            "entry_value": "entry",
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_all_securities(self):
        pf = self._make_portfolio()
        pf.holdings = pd.DataFrame({"code": ["AAA", "BBB"]})
        with mock.patch("investment.core.portfolio.Generic", side_effect=lambda code: f"SEC-{code}") as mg:
            result = pf.all_securities
        self.assertEqual(result, ["SEC-AAA", "SEC-BBB"])
        mg.assert_any_call("AAA")
        mg.assert_any_call("BBB")

    def test_init_triggers_loading(self):
        with mock.patch.object(Portfolio, "_load_cash_and_holdings") as mch:
            pf = Portfolio("TEST")
        mch.assert_called_once()
        self.assertEqual(pf.code, "TEST")

    def test_load_cash_and_holdings_calls(self):
        pf = self._make_portfolio(has_cash=True)
        with mock.patch.object(pf, "_get_holdings") as gh, \
             mock.patch.object(pf, "_get_cash") as gc:
            pf._load_cash_and_holdings()
        gh.assert_called_once()
        gc.assert_called_once()

        pf = self._make_portfolio(has_cash=True, ignore_cash=True)
        with mock.patch.object(pf, "_get_holdings") as gh, \
             mock.patch.object(pf, "_get_cash") as gc:
            pf._load_cash_and_holdings()
        gh.assert_called_once()
        gc.assert_not_called()

    def test_update_calls_transactions_update(self):
        pf = self._make_portfolio()
        with mock.patch("investment.core.portfolio.Transactions.update") as tu, \
             mock.patch.object(pf, "_load_cash_and_holdings") as lch:
            pf.update()
        tu.assert_called_once()
        lch.assert_called_once()

    def test_update_invalid_code(self):
        pf = self._make_portfolio(code="OTHER")
        with mock.patch("investment.core.portfolio.Transactions.update") as tu, \
             mock.patch.object(pf, "_load_cash_and_holdings") as lch:
            with self.assertRaises(Exception):
                pf.update()
        tu.assert_not_called()
        lch.assert_not_called()

    def test_combine_with_security_price_history(self):
        pf = self._make_portfolio()
        df = pd.DataFrame({
            "as_of_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "currency": ["GBP", "GBP"],
            "figi_code": ["AAA", "AAA"],
            "code": ["AAA", "AAA"],
            "quantity": [1.0, 1.0],
            "average": [100.0, 100.0],
            "entry_value": [100.0, 100.0],
        })
        ph = pd.DataFrame({
            "as_of_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "close": [10.0, 20.0],
        }).set_index("as_of_date")
        sec = mock.Mock()
        sec.code = "AAA"
        sec.get_price_history.return_value = ph
        with mock.patch.object(Portfolio, "all_securities", new_callable=mock.PropertyMock, return_value=[sec]):
            result = pf._combine_with_security_price_history(df, currency="GBP")

        expected = df.merge(
            ph.reset_index().assign(code="AAA"),
            on=["as_of_date", "code"],
            how="left",
        )
        expected = expected.sort_values(by=["code", "figi_code", "as_of_date"])
        expected = expected.set_index(["code", "figi_code"]).groupby(level=0, group_keys=False).ffill()
        expected = expected.set_index("as_of_date", append=True)

        pd.testing.assert_frame_equal(result, expected)
        sec.get_price_history.assert_called_once_with(datasource=None, local_only=True, currency="GBP")
