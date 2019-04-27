import os
from pathlib import Path
import re
from datetime import datetime


class Repo:

    def __init__(self, root: str):
        #assert os.path.exists(root), f"Root directory {root} does not exist"
        self.root = root

    @classmethod
    def at(cls, root: str):
        repo = cls(root)
        return repo


class OpenDataCanada(Repo):

    def __init__(self):
        super().__init__('https://open.canada.ca')



_DEFAULT_LOCALE = 'en'

DATASET_PATTERN = re.compile(r'(https?)://([a-zA-z0-9\.]+)/(data/)?([a-z]{2})?/dataset/([^\^ ]{3,})')


class Dataset:

    def __init__(self,
                 ref_number: str,
                 title: str = None,
                 description: str = None,
                 id: str = None,
                 locale: str = None):
        self.ref_number = ref_number
        self.id = id
        self.locale = locale
        self.title = title
        self.description = description

    def __repr__(self):
        return f'<Dataset: {self.ref_number} {self.title}>'


class IdAndLocale:

    def __init__(self, id: str, locale: str = None):
        self.id = id
        self.locale = locale or _DEFAULT_LOCALE

    def path(self):
        return f'{self.locale}/dataset/{self.id}'

    def __repr__(self):
        return f'<Dataset id:{self.id} locale:{self.locale}>'

    @classmethod
    def parse(cls, url):
        match = DATASET_PATTERN.match(url)
        if not match:
            print(url + " doesn't match <URL>/<HOST>/data/<LOCALE>/dataset/<DATASET_ID>")
            return None
        assert match, url + " doesn't match <URL>/<HOST>/data/<LOCALE>/dataset/<DATASET_ID>"
        locale, dataset_id = match.group(4), match.group(5)
        return cls(dataset_id, locale)