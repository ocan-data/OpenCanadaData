import unittest
import os
import shutil
from opencanada.repo import Repo


class RepoTestCase(unittest.TestCase):

    def test_create_repo_here(self):
        if os.path.exists('repo'):
            shutil.rmtree('repo')
        repo: Repo = Repo.here()
        print(repo)
        self.assertIsNotNone(repo)
        self.assertTrue(repo.dataset.exists())
        self.assertTrue(repo.dataset.name.endswith('dataset'))


if __name__ == '__main__':
    unittest.main()
