"""Test cases for :class:`~investment.core.transactions.Transactions`."""

import unittest
import warnings
from unittest import mock

import pandas as pd

from investment import config
from investment.core.transactions import Transactions


class TransactionsTestCase(unittest.TestCase):
    """Test cases for :class:`~investment.core.transactions.Transactions`."""

    def test_extract_and_save_investment_transactions_1(self):
        """Rows not matching the pattern are dropped with a warning."""
        raw_df = pd.DataFrame(
            {
                "Category": ["Investments", "Investments", "Investments"],
                "Description": [
                    "AAA B 10 100 GBP",
                    "BAD DATA",
                    "BBB S 2 50 USD",
                ],
                "Origin": ["ACC1000", "ACC1000", "ACC2000"],
                "Date": ["2020-01-01", "2020-01-03", "2020-01-02"],
            }
        )

        tx = Transactions()
        with mock.patch.object(
            Transactions, "_load_transactions", return_value=raw_df
        ), mock.patch.object(pd.DataFrame, "to_csv", autospec=True) as m_csv:
            with self.assertWarns(UserWarning):
                tx.extract_and_save_investment_transactions()

        saved_df = m_csv.call_args.args[0]
        path = m_csv.call_args.args[1]
        self.assertFalse(m_csv.call_args.kwargs.get("index", True))
        self.assertEqual(
            path,
            f"{config.PORTFOLIO_PATH}/{config.DEFAULT_NAME}-transactions.csv",
        )
        expected = pd.DataFrame(
            {
                "figi_code": ["AAA", "BBB"],
                "quantity": [10.0, -2.0],
                "price": [100.0, 50.0],
                "currency": ["GBP", "USD"],
                "account": ["ACC1", "ACC2"],
                "value": [1000.0, -100.0],
                "as_of_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            }
        )
        pd.testing.assert_frame_equal(saved_df.reset_index(drop=True), expected)

    def test_extract_and_save_investment_transactions_all_match(self):
        """All rows are kept when every description matches the pattern."""
        clean_df = pd.DataFrame(
            {
                "Category": ["Investments", "Investments"],
                "Description": [
                    "AAA B 10 100 GBP",
                    "BBB S 2 50 USD",
                ],
                "Origin": ["ACC1000", "ACC2000"],
                "Date": ["2020-01-01", "2020-01-02"],
            }
        )

        tx = Transactions()
        with mock.patch.object(
            Transactions, "_load_transactions", return_value=clean_df
        ), mock.patch.object(pd.DataFrame, "to_csv", autospec=True) as m_csv:
            with warnings.catch_warnings(record=True) as w:
                tx.extract_and_save_investment_transactions()
            self.assertEqual(len(w), 0)

        saved_df = m_csv.call_args.args[0]
        path = m_csv.call_args.args[1]
        self.assertFalse(m_csv.call_args.kwargs.get("index", True))
        self.assertEqual(
            path,
            f"{config.PORTFOLIO_PATH}/{config.DEFAULT_NAME}-transactions.csv",
        )
        expected = pd.DataFrame(
            {
                "figi_code": ["AAA", "BBB"],
                "quantity": [10.0, -2.0],
                "price": [100.0, 50.0],
                "currency": ["GBP", "USD"],
                "account": ["ACC1", "ACC2"],
                "value": [1000.0, -100.0],
                "as_of_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            }
        )
        pd.testing.assert_frame_equal(saved_df.reset_index(drop=True), expected)

    def _make_transactions(self, **kwargs) -> Transactions:
        """Return a ``Transactions`` instance bypassing validation."""
        with mock.patch.dict(Transactions.__fields__, clear=False):
            return Transactions.construct(**kwargs)

    def test_load_transactions(self):
        """Verify the helper correctly loads from Excel."""
        tr = self._make_transactions(file_path="/tmp/file.xlsx", sheet_name="Sheet1")
        df = pd.DataFrame()
        with mock.patch("pandas.read_excel", return_value=df) as re:
            result = tr._load_transactions()
        re.assert_called_once_with("/tmp/file.xlsx", sheet_name="Sheet1")
        self.assertIs(result, df)

    def test_extract_and_save_investment_transactions_2(self):
        """Investment rows are parsed and saved to CSV."""
        raw = pd.DataFrame(
            {
                "Category": [
                    "Investments",
                    "Investments",
                    "Investments",
                    "Other",
                ],
                "Description": [
                    "AAA B 10 2 GBP",
                    "BBB S 5 3 USD",
                    "BAD ROW",
                    "CCC B 1 1 USD",
                ],
                "Origin": ["ACC1XXX", "ACC1XXX", "ACC2XXX", "ACC1XXX"],
                "Date": [
                    pd.Timestamp("2020-01-01"),
                    pd.Timestamp("2020-01-02"),
                    pd.Timestamp("2020-01-03"),
                    pd.Timestamp("2020-01-04"),
                ],
            }
        )
        tr = self._make_transactions(code="TEST", portfolio_path="/tmp/portfolio")

        captured = {}

        def fake_to_csv(self, path, index=False):
            captured["df"] = self.copy()
            captured["path"] = path
            captured["index"] = index

        with mock.patch.object(tr, "_load_transactions", return_value=raw), mock.patch(
            "pandas.DataFrame.to_csv", new=fake_to_csv
        ):
            with self.assertWarns(UserWarning):
                tr.extract_and_save_investment_transactions()

        self.assertEqual(captured["path"], "/tmp/portfolio/TEST-transactions.csv")
        self.assertFalse(captured["index"])

        expected = pd.DataFrame(
            {
                "figi_code": ["AAA", "BBB"],
                "quantity": [10.0, -5.0],
                "price": [2.0, 3.0],
                "currency": ["GBP", "USD"],
                "account": ["ACC1", "ACC1"],
                "value": [20.0, -15.0],
                "as_of_date": [
                    pd.Timestamp("2020-01-01"),
                    pd.Timestamp("2020-01-02"),
                ],
            }
        )
        pd.testing.assert_frame_equal(captured["df"].reset_index(drop=True), expected)

    def test_load_and_save_cash_positions(self):
        """Cash positions are aggregated and saved to CSV."""
        raw = pd.DataFrame(
            {
                "Date": [
                    pd.Timestamp("2020-01-01"),
                    pd.Timestamp("2020-01-02"),
                    pd.Timestamp("2020-01-01"),
                ],
                "Currency": ["USD", "USD", "EUR"],
                "Net Value": [10, 5, 7],
            }
        )
        tr = self._make_transactions(code="TEST", portfolio_path="/tmp/portfolio")

        captured = {}

        def fake_to_csv(self, path, index=False):
            captured["df"] = self.copy()
            captured["path"] = path
            captured["index"] = index

        with mock.patch.object(tr, "_load_transactions", return_value=raw), mock.patch(
            "pandas.DataFrame.to_csv", new=fake_to_csv
        ):
            tr.load_and_save_cash_positions()

        self.assertEqual(captured["path"], "/tmp/portfolio/TEST-cash.csv")
        expected = pd.DataFrame(
            {
                "currency": ["EUR", "USD", "USD"],
                "as_of_date": [
                    pd.Timestamp("2020-01-01"),
                    pd.Timestamp("2020-01-01"),
                    pd.Timestamp("2020-01-02"),
                ],
                "value": [7.0, 10.0, 15.0],
                "change": [7.0, 10.0, 5.0],
            }
        )
        pd.testing.assert_frame_equal(captured["df"].reset_index(drop=True), expected)

    def test_update_calls_helpers(self):
        """``update`` invokes both extraction helpers."""
        tr = self._make_transactions()
        with mock.patch.object(
            Transactions,
            "extract_and_save_investment_transactions",
            autospec=True,
        ) as eit, mock.patch.object(
            Transactions, "load_and_save_cash_positions", autospec=True
        ) as lsc:
            tr.update()
        eit.assert_called_once_with(tr)
        lsc.assert_called_once_with(tr)

    def test_arbitrary_attribute_assignment(self):
        """Transactions allows setting extra attributes for tests."""
        tr = Transactions()
        tr.some_attr = 123
        self.assertEqual(tr.some_attr, 123)

    def test_load_transactions_defaults(self):
        """_load_transactions uses the instance file_path and sheet_name."""
        tr = Transactions()
        tr.file_path = "/tmp/sample.xlsx"
        tr.sheet_name = "SheetA"
        df = pd.DataFrame()
        with mock.patch("pandas.read_excel", return_value=df) as re:
            result = tr._load_transactions()
        re.assert_called_once_with("/tmp/sample.xlsx", sheet_name="SheetA")
        self.assertIs(result, df)
