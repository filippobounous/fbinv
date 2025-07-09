import unittest
from unittest import mock

import pandas as pd

from inventory.core.house import House


class LocalDataSourceTests(unittest.TestCase):
    """Tests for the inventory LocalDataSource helper loading."""

    def test_load_latest_non_deleted_version(self):
        """Latest non-deleted row should initialise the entity."""
        df = pd.DataFrame(
            {
                "code": ["H1", "H1", "H1"],
                "name": ["old", "new", "gone"],
                "version": [1, 2, 3],
                "is_deleted": [False, False, True],
            }
        )
        with mock.patch("inventory.datasource.local.pd.read_csv", return_value=df):
            house = House(
                code="H1",
                name="placeholder",
                address="addr",
                city="city",
                country="GB",
                postal_code="Z1",
                beneficiary="Ben",
                latitude=0.0,
                longitude=0.0,
            )
        self.assertEqual(house.name, "new")
        self.assertEqual(house.version, 2)
        self.assertFalse(house.is_deleted)

