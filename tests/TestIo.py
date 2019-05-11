import unittest
from opencanada.io import get_filename_from_url, download_file, unzip_data
import os
from opencanada.config import CACHE_DIR
from environs import Env

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


    def test_unzip_file_todir(self):
        url = 'https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip'
        download_dir = '../data/cache'
        files = unzip_data(url, path=download_dir)
        self.assertTrue(all([f.startswith(download_dir) for f in files]))

    def test_unzip_file_to_default(self):
        url = 'https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip'
        files = unzip_data(url)
        print(files)

    def test_default_download_dir(self):
        env: Env = Env()
        env.read_env()
        env('LALA', 'a')

if __name__ == '__main__':
    unittest.main()