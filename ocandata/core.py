from typing import Any
import requests


def get(url):
    res = requests.get(url)
    if res.status_code == 200:
        return res.text


def ifnone(a: Any, b: Any) -> Any:
    "`a` if `a` is not None, otherwise `b`."
    return b if a is None else a