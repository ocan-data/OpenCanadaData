import unittest
import os
import shutil
from opencanada.repo import Repo

RAIL_DATA_URL : str = 'https://www150.statcan.gc.ca/n1/tbl/csv/23100274-eng.zip'

class RepoTestCase(unittest.TestCase):

    def test_create_repo_here(self):
        if os.path.exists('repo'):
            shutil.rmtree('repo')
        repo: Repo = Repo.here()
        print(repo)
        self.assertIsNotNone(repo)
        self.assertTrue(repo.dataset.exists())
        self.assertTrue(repo.dataset.name.endswith('dataset'))

    def test_create_repo_at_home(self):
        repo: Repo = Repo.at_user_home()
        repo.repo.lstat()
        print(repo)

    def test_unzip_data(self):
        repo: Repo = Repo.here()
        files = repo.unzip(RAIL_DATA_URL)
        print(files)


if __name__ == '__main__':
    unittest.main()
