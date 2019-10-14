import unittest
from ocandata import Inventory
import pandas as pd

INVENTORY_URL = 'https://open.canada.ca/data/dataset/4ed351cf-95d8-4c10-97ac-6b3511f359b7/resource/d0df95a8-31a9-46c9-853b-6952819ec7b4/download/inventory.csv'
INVENTORY_CSV='../data/inventory.csv'

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_colwidth', 50)

class InventoryTestCase(unittest.TestCase):

    def test_invetory_from_url(self):
        inventory: Inventory = Inventory.from_url(INVENTORY_URL)
        self.assertIsNotNone(inventory)
        self.assertIsNotNone(inventory.data)

    def test_inventory_from_dataframe(self):
        df = pd.read_csv(INVENTORY_CSV)
        inventory: Inventory = Inventory.from_dataframe(df)
        self.assertIsNotNone(inventory)
        self.assertIsNotNone(inventory.data)

    def test_inventory_from_csv(self):
        inventory: Inventory = Inventory.from_csv(INVENTORY_CSV)
        self.assertIsNotNone(inventory)
        self.assertIsNotNone(inventory.data)

    def test_inventory_statscan(self):
        inventory: Inventory = Inventory.from_csv(INVENTORY_CSV)
        print(inventory.statscan)

    def test_load(self):
        inventory: Inventory = Inventory.load()
        print(inventory.statscan)


if __name__ == '__main__':
    unittest.main()
