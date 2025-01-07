import re
import unicodedata
from collections.abc import Iterable
from typing import Literal, Protocol

import stringalign._stringutils


class Tokenizer(Protocol):
    def __call__(self, text: str) -> list[str]: ...

    def join(self, text: Iterable[str]) -> str: ...


class StringNormalizer:
    """Simple string normalizer, used to remove "irrelevant" differences when comparing strings.

    Arguments
    ---------
    normalization:
        Which unicode normalization to use
    case_insensitive:
        If true, run `str.casefold` to make all letters lowercase
    normalize_whitespace:
        Turn any occurance of one or more whitespaces into exactly one regular space
    remove_whitespace:
        Turn any occurance of one or more whitespaces into exactly one regular space
    remove_non_word_characters:
        Remove any character non-alphabetic and non-numeric unicode characters except spaces.
    """

    def __init__(
        self,
        normalization: Literal["NFC", "NFD", "NFKC", "NFKD", None] = "NFC",
        case_insensitive: bool = False,
        normalize_whitespace: bool = False,
        remove_whitespace: bool = False,
        remove_non_word_characters: bool = False,
    ) -> None:
        self.normalization = normalization
        self.case_insensitive = case_insensitive
        self.normalize_whitespace = normalize_whitespace
        self.remove_whitespace = remove_whitespace
        self.remove_non_word_characters = remove_non_word_characters

    def __call__(self, text: str) -> str:
        if self.normalization is not None:
            text = unicodedata.normalize(self.normalization, text)
        if self.case_insensitive:
            text = text.casefold()
        if self.normalize_whitespace:
            text = re.sub(r"\s+", " ", text)
        if self.remove_whitespace:
            text = re.sub(r"\s", "", text)
        if self.remove_non_word_characters:
            text = re.sub(r"[^\w\s]|_", "", text)

        return text


class GraphemeClusterTokenizer:
    """Turn a text string into a list of extended grapheme clusters :cite:p:`unicode-annex-29`.

    This code uses the ```unicode_segmentation```_ Rust crate to do split the text string into
    extended grapheme clusters.

    Arguments
    ---------
    normalization:
        Which unicode normalization to use
    case_insensitive:
        If true, run `str.casefold` to make all letters lowercase
    normalize_whitespace:
        Turn any occurance of one or more whitespaces into exactly one regular space
    remove_non_word_characters:
        Remove any character that isn't a Unicode word character as well as underscores.

    .. _``unicode_segmentation``: https://docs.rs/unicode-segmentation/latest/unicode_segmentation/index.html
    """

    def __init__(
        self,
        pre_clustering_normalizer: StringNormalizer | None = None,
        post_clustering_normalizer: StringNormalizer | None = None,
    ) -> None:
        self.pre_clustering_normalizer = pre_clustering_normalizer or StringNormalizer()
        self.post_clustering_normalizer = post_clustering_normalizer or StringNormalizer()

    def __call__(self, text: str) -> list[str]:
        text = self.pre_clustering_normalizer(text)
        clusters = stringalign._stringutils.grapheme_clusters(text)
        clusters = [self.post_clustering_normalizer(cluster) for cluster in clusters]
        return clusters

    def join(self, tokens: Iterable[str]) -> str:
        return "".join(tokens)


class UnicodeWordTokenizer:
    """Turn a text string into a list of extracted words as described in :cite:p:`unicode-annex-29`.

    This code uses the ```unicode_segmentation```_ Rust crate to do split the text string into
    words. Note that all punctuation is removed.

    Arguments
    ---------
    normalization:
        Which unicode normalization to use
    case_insensitive:
        If true, run `str.casefold` to make all letters lowercase
    normalize_whitespace:
        Turn any occurance of one or more whitespaces into exactly one regular space
    remove_non_word_characters:
        Remove any character that isn't a Unicode word character as well as underscores.

    .. _``unicode_segmentation``: https://docs.rs/unicode-segmentation/latest/unicode_segmentation/index.html
    """

    def __init__(
        self,
        pre_clustering_normalizer: StringNormalizer | None = None,
        post_clustering_normalizer: StringNormalizer | None = None,
    ) -> None:
        self.pre_clustering_normalizer = pre_clustering_normalizer or StringNormalizer()
        self.post_clustering_normalizer = post_clustering_normalizer or StringNormalizer()

    def __call__(self, text: str) -> list[str]:
        text = self.pre_clustering_normalizer(text)
        clusters = stringalign._stringutils.unicode_words(text)
        clusters = [self.post_clustering_normalizer(cluster) for cluster in clusters]
        return clusters

    def join(self, tokens: Iterable[str]) -> str:
        return " ".join(tokens)


class SplitAtWordBoundaryTokenizer:
    """Turn a text string into a list of words by splitting at word boundaries as described in :cite:p:`unicode-annex-29`.

    This code uses the ```unicode_segmentation```_ Rust crate to do split the text string into
    words.

    Arguments
    ---------
    normalization:
        Which unicode normalization to use
    case_insensitive:
        If true, run `str.casefold` to make all letters lowercase
    normalize_whitespace:
        Turn any occurance of one or more whitespaces into exactly one regular space
    remove_non_word_characters:
        Remove any character that isn't a Unicode word character as well as underscores.

    .. _``unicode_segmentation``: https://docs.rs/unicode-segmentation/latest/unicode_segmentation/index.html
    """

    def __init__(
        self,
        pre_clustering_normalizer: StringNormalizer | None = None,
        post_clustering_normalizer: StringNormalizer | None = None,
    ) -> None:
        self.pre_clustering_normalizer = pre_clustering_normalizer or StringNormalizer()
        self.post_clustering_normalizer = post_clustering_normalizer or StringNormalizer()

    def __call__(self, text: str) -> list[str]:
        text = self.pre_clustering_normalizer(text)
        clusters = stringalign._stringutils.split_at_word_boundaries(text)
        clusters = [self.post_clustering_normalizer(cluster) for cluster in clusters]
        return clusters

    def join(self, tokens: Iterable[str]) -> str:
        return " ".join(tokens)
