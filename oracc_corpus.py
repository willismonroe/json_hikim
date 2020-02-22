from oracc_text import ORACC_Text
from typing import Dict, List
from pathlib import Path
from oracc_reader import FileReader
import copy


def guess_filenames(directory: str):
    catalog_file = Path(directory) / "catalogue.json"
    metadata_file = Path(directory) / "metadata.json"
    corpus_file = Path(directory) / "corpus.json"
    return ORACC_Corpus(str(catalog_file), str(metadata_file), str(corpus_file))


class ORACC_Corpus:
    """
    This class represent a corpus or ORACC project.
    """

    def __init__(self, catalog_file: str, metadata_file: str, corpus_file: str) -> None:
        self.dir: Path = Path(catalog_file).parents[0]
        self.catalog_file: str = catalog_file
        self.metadata_file: str = metadata_file
        self.corpus_file: str = corpus_file
        self.texts: Dict[str, ORACC_Text] = {}
        self.name: str = ""
        self.blurb: str = ""
        self.pathname: str = ""
        self.filtered: bool = False
        self.load_corpus()

    def load_corpus(self) -> None:
        self.fi_catalog = FileReader(self.catalog_file)
        self.fi_metadata = FileReader(self.metadata_file)
        self.fi_corpus = FileReader(self.corpus_file)
        self.name = self.fi_metadata.data.get("config").get("name")
        self.blurb = self.fi_metadata.data.get("config").get("blurb")
        self.pathname = self.fi_metadata.data.get("config").get("pathname")
        for pnum, path in self.fi_corpus.data.get("members").items():
            fi_text = FileReader(str(self.dir / Path(path)))
            self.texts[pnum] = ORACC_Text(
                fi_text.data, self.fi_catalog.data.get("members").get(pnum)
            )

    def bow_norm(self) -> List[str]:
        bow: List[str] = []
        for text in self.texts:
            for word in self.texts[text].get_norm():
                bow.append(word)
        return bow

    def bow_translit(self) -> List[str]:
        bow: List[str] = []
        for text in self.texts:
            for word in self.texts[text].get_translit():
                bow.append(word)
        return bow

    def kwic(self, word: str, window: int = 2):
        # not super happy about bracketing the word
        lines = []
        for text in self.texts:
            norm = self.texts[text].get_norm()
            idxs = [i for i, x in enumerate(norm) if x == word]
            for i in idxs:
                start = i - window if i > window else 0
                end = i + window + 1
                lines.append(norm[start:end])
        return lines

    def pprint_kwic(self, word: str, window: int = 2) -> None:
        lines = [
            [f"[[{w}]]" if w == word else w for w in line]
            for line in self.kwic(word, window)
        ]
        print(f"KWIC for {word}:")
        print(f"{'-'*(10+len(word))}")
        for line in lines:
            print(" ".join(line))

    def filter(self, selected_texts: List[str]) -> None:
        if self.filtered:
            print("Already filtered, please .unfilter() first.")
        else:
            self.filtered = True
            self.alltexts = copy.deepcopy(self.texts)
            self.texts = {
                pnum: self.texts[pnum] for pnum in self.texts if pnum in selected_texts
            }

    def unfilter(self):
        if not self.filtered:
            print("Not filtered, has no effect")
        else:
            self.filtered = False
            self.texts = copy.deepcopy(self.alltexts)

    def toc_by_author(self) -> None:
        authors = {}
        for text in self.texts:
            author = self.texts[text].ancient_author
            authors.setdefault(author, []).append(text)
        max_len = len(max(authors.keys(), key=len)) + 3
        print("ToC by Author:")
        print("--------------")
        max_len = len(max(authors.keys(), key=len)) + 3
        for [i, (author, texts)] in enumerate(
            sorted(authors.items(), key=lambda x: len(x[1]), reverse=True)
        ):
            au_len = len(author) - max_len + 1
            spc = int(max_len / 2)
            if i % 5 == 0 and i > 0:
                print(f"{'- '*spc}")
            print(f"{author}:{len(texts):>{au_len}}")

    def get_texts_by_author(self, author: str):
        return [
            text for text in self.texts if self.texts[text].ancient_author == author
        ]

