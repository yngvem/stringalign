import re
import unicodedata
from collections.abc import Iterable
from typing import Callable, Literal, Protocol

import stringalign._stringutils


class Tokenizer(Protocol):
    def __call__(self, text: str) -> list[str]: ...

    def join(self, text: Iterable[str]) -> str: ...


def _add_join(tokenizer: Callable[[str], list[str]], sep: str = " ") -> Tokenizer:
    """Function that `join` method to a tokenizer function.
    This allows the tokenizer to be used with the Tokenizer protocol.

    Arguments
    ---------
    tokenizer:
        A tokenizer function that takes a string and returns a list of tokens.
    sep (optional):
        The separator to use when joining tokens. Defaults to a single space.

    Returns
    -------
    Tokenizer:
        A wrapped tokenizer that has a `join` method.
    """

    class WrappedTokenizer:
        """Tokenizer that wraps a provided tokenizer function. See the docstrings of the __call__ and join methods."""

        def __call__(self, text: str) -> list[str]:
            """Function wrapping a provided tokenizer."""
            return tokenizer(text)

        def join(self, tokens: Iterable[str]) -> str:
            return sep.join(tokens)

        # Dynamically update docstrings for the methods. This must happen this way since Python docstrings
        # cannot be f-strings (they must be string literals).
        join.__doc__ = f"Join tokens with the specified separator ({sep!r})."
        if tokenizer.__doc__ and __call__.__doc__:  # (__call__.__doc__ is there for the type checker)
            __call__.__doc__ += f"See the tokenizer docstring below.\n\n{tokenizer.__doc__}"

    return WrappedTokenizer()


def add_join(sep: str = " ") -> Callable[[Callable[[str], list[str]]], Tokenizer]:
    """Decorator that `join` method to a tokenizer function.
    This allows the tokenizer to be used with the Tokenizer protocol.

    Arguments
    ---------
    tokenizer:
        A tokenizer function that takes a string and returns a list of tokens.
    sep (optional):
        The separator to use when joining tokens. Defaults to a single space.

    Returns
    -------
    Tokenizer:
        A wrapped tokenizer that has a `join` method.
    """

    def decorator(tokenizer: Callable[[str], list[str]]) -> Tokenizer:
        return _add_join(tokenizer, sep=sep)

    return decorator


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
        # According to Unicode, we should normalize strings before casefolding them.
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

        # Some of these operations, like casefolding, can make normalized text unnormalized.
        # So we normalize again to ensure the text is in the correct form.
        if self.normalization is not None:
            text = unicodedata.normalize(self.normalization, text)

        return text


class GraphemeClusterTokenizer:
    """Turn a text string into a list of extended grapheme clusters :cite:p:`unicode-annex-29`.

    This code uses the ```unicode_segmentation```_ Rust crate to do split the text string into
    extended grapheme clusters.

    Arguments
    ---------
    pre_clustering_normalizer:
        An optional :py:class:`StringNormalizer` to apply before splitting into extended grapheme clusters.
    post_clustering_normalizer:
        An optional :py:class:`StringNormalizer` to apply to each token after splitting.

    Examples
    --------
    >>> tokenizer = GraphemeClusterTokenizer()
    >>> tokenizer("abc🏳️‍🌈🏳️‍⚧️❤️‍🔥")
    ['a', 'b', 'c', '🏳️‍🌈', '🏳️‍⚧️', '❤️‍🔥']

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
    pre_clustering_normalizer:
        An optional :py:class:`StringNormalizer` to apply before splitting into words.
    post_clustering_normalizer:
        An optional :py:class:`StringNormalizer` to apply to each token after splitting.

    Examples
    --------
    >>> tokenizer = UnicodeWordTokenizer()
    >>> tokenizer("Hello World")
    ['Hello', 'World']
    >>> tokenizer("'Hello', (World)!")
    ['Hello', 'World']

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
    """Turn a text string into a list of tokens by splitting at word boundaries as described in :cite:p:`unicode-annex-29`.

    This code uses the ```unicode_segmentation```_ Rust crate to split the text string at word boundaries.

    Arguments
    ---------
    pre_clustering_normalizer:
        An optional :py:class:`StringNormalizer` to apply before splitting at word boundaries.
    post_clustering_normalizer:
        An optional :py:class:`StringNormalizer` to apply to each token after splitting.
    remove_whitespace:
        If True, remove tokens that are only whitespace after splitting.

    Examples
    --------
    >>> tokenizer = SplitAtWordBoundaryTokenizer()
    >>> tokenizer("Hello World")
    ['Hello', ' ', 'World']
    >>> tokenizer("'Hello', (World)!")
    ["'", 'Hello', "'", ',', ' ', '(', 'World', ')', '!']
    >>> tokenizer("Hello  World!")
    ['Hello', '  ', 'World', '!']
    >>> tokenizer = SplitAtWordBoundaryTokenizer(remove_whitespace=True)
    >>> tokenizer("Hello  World!")
    ['Hello', 'World', '!']

    .. _``unicode_segmentation``: https://docs.rs/unicode-segmentation/latest/unicode_segmentation/index.html
    """

    def __init__(
        self,
        pre_clustering_normalizer: StringNormalizer | None = None,
        post_clustering_normalizer: StringNormalizer | None = None,
        remove_whitespace: bool = False,
    ) -> None:
        self.pre_clustering_normalizer = pre_clustering_normalizer or StringNormalizer()
        self.post_clustering_normalizer = post_clustering_normalizer or StringNormalizer()
        self.remove_whitespace = remove_whitespace

    def __call__(self, text: str) -> list[str]:
        text = self.pre_clustering_normalizer(text)
        clusters: Iterable[str] = stringalign._stringutils.split_at_word_boundaries(text)
        clusters = (self.post_clustering_normalizer(cluster) for cluster in clusters)

        if self.remove_whitespace:
            clusters = (cluster for cluster in clusters if cluster.strip())

        return list(clusters)

    def join(self, tokens: Iterable[str]) -> str:
        return "".join(tokens)


class SplitAtWhitespaceTokenizer:
    """Turn a text string into a list of words by splitting at whitespace characters.

    This tokenizer will split at any whitespace character, including spaces, tabs, newlines and
    any other unicode whitespace character and some other characters also. See the Python documentation
    for ```str.isspace```_ for more information.

    Arguments
    ---------
    pre_clustering_normalizer:
        An optional :py:class:`StringNormalizer` to apply before splitting at whitespace.
    post_clustering_normalizer:
        An optional :py:class:`StringNormalizer` to apply to each token after splitting.


    Examples
    --------
    >>> tokenizer = SplitAtWhitespaceTokenizer()
    >>> tokenizer("Hello World")
    ['Hello', 'World']
    >>> tokenizer("'Hello', (World)!")
    ["'Hello',", '(World)!']

    .. _``str.isspace``: https://docs.python.org/3/library/stdtypes.html#str.isspace
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
        clusters = text.split()
        clusters = [self.post_clustering_normalizer(cluster) for cluster in clusters]
        return clusters

    def join(self, tokens: Iterable[str]) -> str:
        return " ".join(tokens)
