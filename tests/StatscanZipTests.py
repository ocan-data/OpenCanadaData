import unittest
from canadadata.statscan import StatscanZip


RAIL_DATA_URL : str = 'https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip'

class StatscanZipTests(unittest.TestCase):

    def test_repr(self):
        zip = StatscanZip(RAIL_DATA_URL)
        print(zip)
        self.assertTrue('Statscan' in str(zip))

    def test_assert_for_nonzipfiles(self):
        self.assertRaises(AssertionError, StatscanZip, url='notazip')

    def test_get_data(self):
        zip = StatscanZip(RAIL_DATA_URL)
        data = zip.get_data()
        self.assertTrue('Companies' in data.columns)
        self.assertTrue('Terminal dwell-time' in data.columns)
        self.assertTrue(len(data) > 60)

    def test_get_data_multiple_times(self):
        zip = StatscanZip(RAIL_DATA_URL)
        data = zip.get_data()
        self.assertTrue('Companies' in data.columns)
        zip.get_data()


if __name__ == '__main__':
    unittest.main()
