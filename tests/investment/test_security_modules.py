import unittest
from unittest import mock

from investment.datasource.test import TestDataSource
from investment.core.security import CurrencyCross, Equity, ETF, Fund
from investment.core.security.isin import ISINSecurity


class SecurityModulesTestCase(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch(
            "investment.core.mapping.BaseMappingEntity._local_datasource",
            TestDataSource,
        )
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_equity_instantiation(self):
        sec = Equity("AAA")
        self.assertEqual(sec.code, "AAA")
        self.assertIsInstance(sec, ISINSecurity)
        self.assertEqual(sec.entity_type, "equity")

    def test_currency_cross_instantiation(self):
        cc = CurrencyCross("USDGBP")
        self.assertEqual(cc.code, "USDGBP")
        self.assertEqual(cc.entity_type, "currency_cross")

    def test_etf_instantiation(self):
        etf = ETF("ETF1")
        self.assertEqual(etf.entity_type, "etf")

    def test_fund_instantiation(self):
        fund = Fund("FUND1")
        self.assertEqual(fund.entity_type, "fund")


if __name__ == "__main__":
    unittest.main()
