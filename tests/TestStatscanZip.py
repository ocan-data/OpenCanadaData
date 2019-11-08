import unittest
import pandas as pd
from ocandata.statscan import StatscanZip, StatscanUrl, StatscanMetadata
pd.set_option('display.max_columns', 20)

RAIL_DATA_URL: str = "https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip"


class StatscanZipTests(unittest.TestCase):
    def test_repr(self):
        zip = StatscanZip(RAIL_DATA_URL)
        print(zip)
        self.assertTrue("Statscan" in str(zip))

    def test_assert_for_nonzipfiles(self):
        self.assertRaises(AssertionError, StatscanZip, url="notazip")

    def test_get_data(self):
        zip = StatscanZip(RAIL_DATA_URL)
        data = zip.get_data()
        self.assertTrue("Companies" in data.columns)
        self.assertTrue("Terminal dwell-time" in data.columns)
        self.assertTrue(len(data) > 60)

    def test_ref_date(self):
        zip = StatscanZip('https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip')
        data = zip.get_data()
        self.assertEqual(data.Date.dtype, '<M8[ns]')

    def test_get_metadata(self):
        zip = StatscanZip(RAIL_DATA_URL)
        metadata = zip.get_metadata()
        self.assertIsNotNone(metadata)
        self.assertIsNotNone(zip.metadata)

    def test_get_dimensions(self):
        zip = StatscanZip(RAIL_DATA_URL)
        metadata: StatscanMetadata = zip.get_metadata()
        print(metadata.dimensions)

    def test_get_pivot_column(self):
        zip = StatscanZip(RAIL_DATA_URL)
        metadata: StatscanMetadata = zip.get_metadata()
        pivot_column = metadata.pivot_column()
        self.assertEqual('Indicator', pivot_column)

    def test_get_data_multiple_times(self):
        zip = StatscanZip(RAIL_DATA_URL)
        data = zip.get_data()
        self.assertTrue("Companies" in data.columns)
        zip.get_data()

    def test_english_and_french_resource_ids(self):
        eng_url = 'https://www150.statcan.gc.ca/n1/tbl/csv/25100055-eng.zip'
        fre_url = 'https://www150.statcan.gc.ca/n1/tbl/csv/25100055-fra.zip'
        eng_id = StatscanUrl.parse_from_filename(eng_url)
        fre_id = StatscanUrl.parse_from_filename(fre_url)
        self.assertEqual(eng_id.id(), fre_id.id())
        self.assertEqual(hash(eng_id.id()), hash(fre_id.id()))

    def test_parse_url(self):
        url = "https://www150.statcan.gc.ca/n1/tbl/csv/23100274.zip"
        print(url.index("23100274.zip"))

    def test_create_from_url_with_params(self):
        dataset: StatscanZip = StatscanZip('https://www150.statcan.gc.ca/n1/en/tbl/csv/38100092-eng.zip?st=yQYQGvmD')
        self.assertIsNotNone(dataset)

    def test_get_data_calls_fetch_once(self):
        url = "https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip"
        zip: StatscanZip = StatscanZip(url)
        data = zip.get_data()
        self.assertGreater(len(data), 10)

    def test_read_csv(self):
        data = pd.read_csv('23100274_MetaData.csv')
        print(data)
        print(data.columns)

if __name__ == "__main__":
    unittest.main()
