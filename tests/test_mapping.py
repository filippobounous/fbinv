import unittest
from unittest.mock import Mock, patch
from investment.core.mapping import BaseMappingEntity

class MappingEntityTest(unittest.TestCase):
    def test_invalid_entity_type(self):
        with patch.object(BaseMappingEntity, '_local_datasource', return_value=Mock()):
            with self.assertRaises(KeyError):
                BaseMappingEntity(entity_type='unknown', code='XXX')

    def test_load_sets_attributes(self):
        class Dummy(BaseMappingEntity):
            owner: str = None
            has_cash: bool = None
        mock_lds = Mock()
        mock_lds.load_portfolio.return_value = {'owner': 'me', 'has_cash': True}
        with patch.object(BaseMappingEntity, '_local_datasource', return_value=mock_lds):
            inst = Dummy(entity_type='portfolio', code='AAA')
        self.assertEqual(inst.owner, 'me')
        self.assertTrue(inst.has_cash)

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
