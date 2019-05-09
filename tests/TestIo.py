import unittest
from opencanada.io import get_filename_from_url, download_file
import os
from opencanada.config import CACHE_DIR

class IOTests(unittest.TestCase):

    def test_get_filename(self):
        url = 'https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip'
        filename = get_filename_from_url(url)
        self.assertEqual('23100274-eng.zip', filename)

    def test_download_files(self):
        url = 'https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip'
        local_file = download_file(url)
        self.assertIsNotNone(local_file)
        self.assertTrue(os.path.exists(local_file))
        os.remove(local_file)

    def test_download_file_todir(self):
        url = 'https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip'
        data_dir = '../data'
        local_file = download_file(url, data_dir)
        self.assertIsNotNone(local_file)
        self.assertTrue(os.path.exists(local_file))
        self.assertTrue(os.path.exists(os.path.join(data_dir, '23100274-eng.zip')))
        os.remove(local_file)

if __name__ == '__main__':
    unittest.main()