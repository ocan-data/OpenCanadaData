import unittest
from opencanada.statscan import StatscanUrlInfo


class MyTestCase(unittest.TestCase):

    def test_parse_zip_url(self):
        info = StatscanUrlInfo.parse_from_filename(
            "https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip"
        )
        print(info)
        self.assertEqual("eng", info.language)
        self.assertEqual("23100274-eng.zip", info.file)
        self.assertEqual("23100274.csv", info.data)
        self.assertEqual("23100274_MetaData.csv", info.metadata)

        info = StatscanUrlInfo.parse_from_filename(
            "https://www150.statcan.gc.ca/n1/tbl/csv/23100274-fra.zip"
        )
        self.assertEqual("fra", info.language)

    def test_parse_zip_url_no_language(self):
        info = StatscanUrlInfo.parse_from_filename(
            "https://www150.statcan.gc.ca/n1/tbl/csv/23100274.zip"
        )
        self.assertIsNone(info.language)


if __name__ == '__main__':
    unittest.main()
