from pathlib import Path
import re
from .io import unzip_data, hash
from .config import DOTPATH

_REPO_NAME = 'repo'


class Repo:

    def __init__(self, path):
        _path = Path(path).resolve()
        self.path: Path = _path / 'repo'
        self._ensure_dirs(self.path)

    def _ensure_dirs(self, path):
        path.mkdir(parents=True, exist_ok=True)
        for dirname in ['downloaded', 'extracted', 'dataset']:
            _dir = path / dirname
            _dir.mkdir(exist_ok=True)
            setattr(self, dirname, _dir)

    @classmethod
    def here(cls):
        return cls.at('.')

    @classmethod
    def at(cls, path):
        return cls(path=Path(path))

    @classmethod
    def at_user_home(cls, dotpath=DOTPATH):
        if not dotpath.startswith('.'):
            dotpath = '.' + dotpath
        root = Path.home() / dotpath
        return cls(root)

    def unzip(self, url, resource_id: str = None):
        if not resource_id:
            resource_id = hash(url)
        extract_dir = self.extracted / resource_id
        print('Extracting files to', extract_dir)
        files = unzip_data(url, extract_dir)
        return files

    def __repr__(self):
        return f'Repo at {self.path}'


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
