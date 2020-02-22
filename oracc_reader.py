import json as JSON
from typing import Dict, Any

import requests


class FileReader:
    """
    This class reads in a file object and converts it from json into a native
    python object.
    It should be identical in functionality to an API reader.
    """

    def __init__(self, filename: str):
        self.filename = filename
        with open(self.filename) as f:
            self.data: Dict[str, Any] = JSON.loads(f.read())


class APIReader:
    """
    This class reads in a URL json file from the ORACC API and turns it into a
    native python object.
    It should be identical in functionality to the file reader.
    The ORACC API is currently non-functional.
    """

    def __init__(self, url: str):
        self.url = url
        r = requests.get(url)
        self.data: Dict[str, any] = JSON.loads(r.content)
        # TODO: request and process url
