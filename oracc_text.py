from typing import Dict, List, Any

import requests
from bs4 import BeautifulSoup


def grab_translation(project: str, pnum: str):
    translation: List[str] = []
    r = requests.get(f"http://oracc.org/{project}/{pnum}")
    soup = BeautifulSoup(r.text)
    for line in soup.find_all("p", class_="tr"):
        s = BeautifulSoup(str(line))
        # seems like SAA10 at least is in Windows-1252 (gross!)
        # https://www.i18nqa.com/debug/utf8-debug.html
        # TODO: add line detection
        # you just need to s.find(class_='xtr-label').get_text()
        s = bytes(s.get_text(), encoding="cp1252").decode()
        translation.append(s)
    return translation


def grab_all(input_json, type: str, split_lines: bool = False) -> List[str]:
    def recursive_walk(json, type):
        if isinstance(json, dict):
            if split_lines:
                if json.get("node") == "d":
                    if json.get("type") == "line-start":
                        yield f"**{json.get('label')}"
            for k, v in json.items():
                if k == type:
                    yield v
                else:
                    yield from recursive_walk(v, type)
        elif isinstance(json, list):
            for item in json:
                yield from recursive_walk(item, type)

    output: list = [token for token in recursive_walk(input_json, type)]
    if split_lines:
        output = " ".join(output).split("**")
    return output


class ORACC_Text:
    """
    This class represent a text from an ORACC corpus.
    """

    def __init__(self, json: dict, metadata: dict = {}):
        self.pnum: str = json["textid"]
        self.json: Dict[str, Any] = json
        self.metadata: Dict[str, Any] = metadata
        self.ancient_author: str = self.metadata["ancient_author"]
        self.norm: List[str] = []
        self.translit: List[str] = []

    def get_norm(self) -> List[str]:
        # I'm not sure of these if/else statements actually do anything with
        # such small texts.
        if len(self.norm) > 0:
            return self.norm
        else:
            self.norm = grab_all(self.json, type="norm")
            return self.norm

    def pprint_norm(self) -> None:
        for line in grab_all(self.json, "norm", split_lines=True):
            print(line)

    def get_translit(self) -> List[str]:
        if len(self.translit) > 0:
            return self.translit
        else:
            self.translit = grab_all(self.json, type="frag")
            return self.translit

    def pprint_translit(self) -> None:
        for line in grab_all(self.json, "frag", split_lines=True):
            print(line)

    # TODO: add 'sense'
