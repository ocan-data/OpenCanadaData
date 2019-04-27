import requests, zipfile, io
import os
import hashlib


def hash(data: str):
    return hashlib.sha1(data.encode()).hexdigest()


def unzip_data(zip_url: str, path='.'):
    response = requests.get(zip_url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    zip_file.extractall(path=path)
    return tuple([os.path.join(path, f) for f in zip_file.namelist()])


def get_filename_from_url(path:str):
    """
    Get filename from path
    """
    return path.split('/')[-1]


def download_file(url: str, path='.'):
    response = requests.get(url)
    filename = get_filename_from_url(url)
    if path:
        filename = os.path.join(path, filename)
    with open(filename, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)
    return filename
