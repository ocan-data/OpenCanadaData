import unittest
from ocandata.statscan import StatscanUrl


class MyTestCase(unittest.TestCase):
    def test_parse_zip_url(self):
        info = StatscanUrl.parse_from_filename(
            "https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip"
        )
        print(info)
        self.assertEqual("eng", info.language)
        self.assertEqual("23100274-eng.zip", info.file)
        self.assertEqual("23100274.csv", info.data)
        self.assertEqual("23100274_MetaData.csv", info.metadata)

        info = StatscanUrl.parse_from_filename(
            "https://www150.statcan.gc.ca/n1/tbl/csv/23100274-fra.zip"
        )
        self.assertEqual("fra", info.language)

    def test_parse_zip_url_no_language(self):
        info = StatscanUrl.parse_from_filename(
            "https://www150.statcan.gc.ca/n1/tbl/csv/23100274.zip"
        )
        self.assertIsNone(info.language)

    def test_id(self):
        url = StatscanUrl.parse_from_filename(
            "https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip"
        )
        self.assertEqual("https://www150.statcan.gc.ca/n1/tbl/csv/23100274", url.id())

    def test_get_url_partitions(self):
        url = StatscanUrl.parse_from_filename(
            "https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip"
        )
        self.assertEquals(['eng'], url.partitions)


if __name__ == "__main__":
    unittest.main()
