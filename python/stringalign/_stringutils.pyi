from collections.abc import Sequence
from typing import Protocol, Self

import numpy as np

class GraphemeClusterIterator(Protocol):
    def __new__(self, s: str, extended: bool) -> Self: ...
    def __init__(self, s: str, extended: bool) -> None: ...
    def __iter__(self) -> Self: ...
    def __next__(self) -> str: ...

def grapheme_clusters(s: str, extended: bool = True) -> list[str]: ...
def unicode_words(s: str) -> list[str]: ...
def split_at_word_boundaries(s: str) -> list[str]: ...
def create_cost_matrix(reference: Sequence[str], predicted: Sequence[str]) -> np.ndarray: ...
