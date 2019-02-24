import requests, zipfile, io
import os
from functools import lru_cache


@lru_cache(maxsize=32)
def unzip_data(zip_url: str, path='.'):
    response = requests.get(zip_url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    zip_file.extractall(path=path)
    return tuple([os.path.join(path, f) for f in zip_file.namelist()])
