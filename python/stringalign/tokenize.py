import unicodedata
from typing import Literal, Protocol

import stringalign._stringutils


class Tokenizer(Protocol):
    def __call__(self, text: str) -> list[str]: ...


class GrahpemeClusterTokenizer:
    def __init__(
        self, normalization: Literal["NFC", "NFD", "NFKC", "NFKD", None] = "NFC", case_insensitive: bool = False
    ) -> None:
        self.normalization = normalization
        self.case_insensitive = case_insensitive

    def __call__(self, text: str) -> list[str]:
        if self.normalization is not None:
            text = unicodedata.normalize(self.normalization, text)
        if self.case_insensitive:
            text = text.casefold()

        return stringalign._stringutils.grapheme_clusters(text)
