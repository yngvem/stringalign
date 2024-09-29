import unicodedata
from typing import Protocol

import stringalign._stringutils


class Tokenizer(Protocol):
    def __call__(self, text: str) -> list[str]: ...


def grapheme_cluster_tokenizer(text) -> list[str]:
    return stringalign._stringutils.grapheme_clusters(unicodedata.normalize("NFC", text))
