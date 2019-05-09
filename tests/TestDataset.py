import unittest
from opencanada.repo import IdAndLocale, Dataset
import pandas as pd

pd.set_option('display.max_colwidth', 80)


class DatasetTestCase(unittest.TestCase):

    def test_create_dataset(self):
        dataset = IdAndLocale(id="winter")
        self.assertEqual('winter', dataset.id)

        dataset = IdAndLocale(id="winter", locale='en')
        self.assertEqual('winter', dataset.id)
        self.assertEqual("en", dataset.locale)

    def test_locale(self):
        dataset = IdAndLocale(id="winter", locale='en')
        self.assertEqual('en', dataset.locale)

        dataset = IdAndLocale(id="winter", locale='fr')
        self.assertEqual('fr', dataset.locale)

        dataset = IdAndLocale(id="winter")
        self.assertEqual('en', dataset.locale)

    def test_dataset_path(self):
        dataset = IdAndLocale(id="winter", locale='en')
        self.assertEqual('en/dataset/winter', dataset.path())

    def test_inventory_dataset(self):
        COLS = ['portal_url_en', 'portal_url_en', 'title_en']
        inventory = pd.read_csv('../data/inventory.csv', usecols=COLS)
        print(inventory[COLS])

    def test_parse_dataset_url(self):
        url = 'https://open.canada.ca/data/en/dataset/6adaeb1f-438b-4d74-b72b-d1b554f3a316'
        dataset = IdAndLocale.parse(url)
        print(dataset)

    def test_dataset_from_csv(self):
        inventory = pd.read_csv('../data/inventory.csv')
        ids = inventory.apply(lambda d: Dataset(d.ref_number, d.title_en, d.description_en), axis=1)
        print(ids)

if __name__ == '__main__':
    unittest.main()
