import requests, zipfile, io
import os


def unzip_data(zip_url: str, path='.'):
    response = requests.get(zip_url)
    zip = zipfile.ZipFile(io.BytesIO(response.content))
    zip.extractall(path=path)
    return tuple([os.path.join(path, f) for f in zip.namelist()])