"""Unit tests covering security submodule initialisation."""

import unittest
from unittest import mock

from investment.core.security import ETF, CurrencyCross, Equity, Fund, ISINSecurity
from investment.datasource.test import TestDataSource


class SecurityModulesTestCase(unittest.TestCase):
    """Test cases for security module initialisation."""

    def setUp(self):
        """Set up the test case environment."""
        # Mock the local datasource to use the test data source
        # This allows us to avoid external dependencies during tests
        patcher = mock.patch(
            "investment.core.mapping.BaseMappingEntity._local_datasource",
            TestDataSource,
        )
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_equity_instantiation(self):
        """Test instantiation of Equity security."""
        sec = Equity("AAA")
        self.assertEqual(sec.code, "AAA")
        self.assertIsInstance(sec, ISINSecurity)
        self.assertEqual(sec.entity_type, "equity")

    def test_currency_cross_instantiation(self):
        """Test instantiation of CurrencyCross security."""
        cc = CurrencyCross("GBPUSD")
        self.assertEqual(cc.code, "GBPUSD")
        self.assertEqual(cc.entity_type, "currency_cross")

    def test_etf_instantiation(self):
        """Test instantiation of ETF security."""
        etf = ETF("ETF1")
        self.assertEqual(etf.entity_type, "etf")

    def test_fund_instantiation(self):
        """Test instantiation of Fund security."""
        fund = Fund("FUND1")
        self.assertEqual(fund.entity_type, "fund")
