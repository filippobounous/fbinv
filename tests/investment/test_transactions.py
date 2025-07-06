"""Unit tests for :class:`~investment.core.transactions.Transactions`."""

import unittest
from unittest import mock
import pandas as pd

from investment.core.transactions import Transactions

class TransactionsTestCase(unittest.TestCase):
    """Unit tests for :class:`Transactions`."""

    def _make_transactions(self, **kwargs) -> Transactions:
        """Return a ``Transactions`` instance bypassing validation."""
        with mock.patch.dict(Transactions.__fields__, clear=False):
            return Transactions.construct(**kwargs)

    def test_load_transactions(self):
        """Verify the helper correctly loads from Excel."""
        tr = self._make_transactions(
            file_path="/tmp/file.xlsx", sheet_name="Sheet1"
        )
        df = pd.DataFrame()
        with mock.patch("pandas.read_excel", return_value=df) as re:
            result = tr._load_transactions()
        re.assert_called_once_with("/tmp/file.xlsx", sheet_name="Sheet1")
        self.assertIs(result, df)

    def test_extract_and_save_investment_transactions(self):
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
        tr = self._make_transactions(
            code="TEST", portfolio_path="/tmp/portfolio"
        )

        captured = {}

        def fake_to_csv(self, path, index=False):
            captured["df"] = self.copy()
            captured["path"] = path
            captured["index"] = index

        with mock.patch.object(
            tr, "_load_transactions", return_value=raw
        ), mock.patch("pandas.DataFrame.to_csv", new=fake_to_csv):
            with self.assertWarns(UserWarning):
                tr.extract_and_save_investment_transactions()

        self.assertEqual(
            captured["path"], "/tmp/portfolio/TEST-transactions.csv"
        )
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
        pd.testing.assert_frame_equal(
            captured["df"].reset_index(drop=True), expected
        )

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
        tr = self._make_transactions(
            code="TEST", portfolio_path="/tmp/portfolio"
        )

        captured = {}

        def fake_to_csv(self, path, index=False):
            captured["df"] = self.copy()
            captured["path"] = path
            captured["index"] = index

        with mock.patch.object(
            tr, "_load_transactions", return_value=raw
        ), mock.patch("pandas.DataFrame.to_csv", new=fake_to_csv):
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
        pd.testing.assert_frame_equal(
            captured["df"].reset_index(drop=True), expected
        )

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
