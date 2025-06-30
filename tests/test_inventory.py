from inventory.core import Item, House, Room, BaseMappingEntity
from inventory.datasource import LocalDataSource, BaseDataSource


def test_core_entities():
    assert isinstance(Item(), BaseMappingEntity)
    assert isinstance(House(), BaseMappingEntity)
    assert isinstance(Room(), BaseMappingEntity)


def test_local_datasource():
    ds = LocalDataSource()
    assert isinstance(ds, BaseDataSource)
    assert ds.load() == {}
