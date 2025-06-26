import unittest
import pandas as pd
from investment.datasource.local import LocalDataSource
from investment.datasource.utils import get_datasource
from investment.datasource.registry import default_timeseries_datasource
from investment.utils.exceptions import SecurityMappingError

class LocalDataSourceLoadTest(unittest.TestCase):
    def test_load_single_row(self):
        df = pd.DataFrame([{'code': 'A', 'num': 1, 'unused': None}])
        result = LocalDataSource._load(df=df)
        self.assertEqual(result, {'code': 'A', 'num': 1})

    def test_load_duplicate(self):
        df = pd.DataFrame([{'code': 'A'}, {'code': 'B'}])
        dummy = type('E', (), {'entity_type': 'eq', 'code': 'A'})()
        with self.assertRaises(SecurityMappingError):
            LocalDataSource._load(df=df, entity=dummy)

    def test_load_missing(self):
        df = pd.DataFrame(columns=['code'])
        dummy = type('E', (), {'entity_type': 'eq', 'code': 'A'})()
        with self.assertRaises(SecurityMappingError):
            LocalDataSource._load(df=df, entity=dummy)

class GetDatasourceTest(unittest.TestCase):
    def test_default(self):
        self.assertIs(get_datasource(), default_timeseries_datasource)

    def test_custom(self):
        obj = object()
        self.assertIs(get_datasource(obj), obj)

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
