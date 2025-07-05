import unittest
import warnings
from unittest import mock

import pandas as pd

from investment import config
from investment.core.transactions import Transactions

class TransactionsTestCase(unittest.TestCase):
    """Test cases for :class:`~investment.core.transactions.Transactions`."""

    def test_extract_and_save_investment_transactions(self):
        """Rows not matching the pattern are dropped with a warning."""
        raw_df = pd.DataFrame({
            "Category": ["Investments", "Investments", "Investments"],
            "Description": [
                "AAA B 10 100 GBP",
                "BAD DATA",
                "BBB S 2 50 USD",
            ],
            "Origin": ["ACC1000", "ACC1000", "ACC2000"],
            "Date": ["2020-01-01", "2020-01-03", "2020-01-02"],
        })

        tx = Transactions()
        with mock.patch.object(Transactions, "_load_transactions", return_value=raw_df), \
             mock.patch.object(pd.DataFrame, "to_csv", autospec=True) as m_csv:
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
        clean_df = pd.DataFrame({
            "Category": ["Investments", "Investments"],
            "Description": [
                "AAA B 10 100 GBP",
                "BBB S 2 50 USD",
            ],
            "Origin": ["ACC1000", "ACC2000"],
            "Date": ["2020-01-01", "2020-01-02"],
        })

        tx = Transactions()
        with mock.patch.object(Transactions, "_load_transactions", return_value=clean_df), \
             mock.patch.object(pd.DataFrame, "to_csv", autospec=True) as m_csv:
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

