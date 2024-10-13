from collections.abc import Generator, Iterable, Sequence
from itertools import groupby
from typing import Literal, TypeVar

from stringalign.compat import batched

T = TypeVar("T")


def run_length_encode(iterable: Iterable[str]) -> tuple[tuple[str, int], ...]:
    """Run-length encode an iterable.

    Example:
    >>> run_length_encode("aaabbbcccc")
    (('a', 3), ('b', 3), ('c', 4))
    >>> run_length_encode("Hello!")
    (('H', 1), ('e', 1), ('l', 2), ('o', 1), ('!', 1))
    >>> run_length_encode("abbcaaadddc")
    (('a', 1), ('b', 2), ('c', 1), ('a', 3), ('d', 3), ('c', 1))
    >>> run_length_encode(["ba", "na", "na"])
    (('ba', 1), ('na', 2))
    """
    return tuple((key, len(tuple(group))) for key, group in groupby(iterable))


def get_offsetted_batched(seq: Sequence[T], n: int, offset: int) -> Generator[tuple[T, ...], None, None]:
    """Get n-batches of a string with an offset.

    Example:
    >>> list(get_offsetted_batched("Hello", 2, offset=1))
    [('H',), ('e', 'l'), ('l', 'o')]
    >>> list(get_offsetted_batched("Hello", 2, offset=0))
    [('H', 'e'), ('l', 'l'), ('o',)]
    """
    if offset:
        yield tuple(seq[:offset])
    yield from batched(seq[offset:], n)


def get_all_n_batches(string: str, n: int) -> Generator[tuple[str, ...], None, None]:
    """Get all n-batches of a string.


    Examples:
    ---------
    >>> tuple(get_all_n_batches("Hello", 1))
    (('H', 'e', 'l', 'l', 'o'),)
    >>> tuple(get_all_n_batches("bananas", 2))
    (('ba', 'na', 'na', 's'), ('b', 'an', 'an', 'as'))
    """

    return (tuple("".join(batch) for batch in get_offsetted_batched(string, n, offset)) for offset in range(n))


def get_all_n_run_length_encodings(string: str, n: int) -> Generator[tuple[tuple[str, int], ...], None, None]:
    """Get all n-run length encodings of a string.

    Examples:
    ---------
    >>> tuple(get_all_n_run_length_ecodings("Hello", 1))
    ((('H', 1), ('e', 1), ('l', 2), ('o', 1)),)
    >>> tuple(get_all_n_run_length_ecodings("bananas", 2))
    ((('ba', 1), ('na', 2), ('s', 1)), (('b', 1), ('an', 2), ('as', 1)))
    """

    return (run_length_encode(batch) for batch in get_all_n_batches(string, n))


def check_ngram_duplication_errors(
    reference: str, predicted: str, *, n: int, type: Literal["insert", "delete"]
) -> bool:
    if not (type := type.lower()) in ("insert", "delete"):  # type: ignore
        raise ValueError(f"Invalid duplication error type: {type}, must be either 'insert' or 'delete'")
    run_length_encodings_reference = get_all_n_run_length_encodings(reference, n)
    run_length_encodings_prediction = get_all_n_run_length_encodings(predicted, n)

    out = False
    for encoding_n1, encoding_n2 in zip(run_length_encodings_reference, run_length_encodings_prediction):
        if len(encoding_n1) != len(encoding_n2):
            return False

        for encoding1, encoding2 in zip(encoding_n1, encoding_n2):
            if encoding1[0] != encoding2[0]:
                return False
            elif encoding1[1] < encoding2[1] and type == "insert":
                out = True
            elif encoding1[1] > encoding2[1] and type == "delete":
                out = True

    return out
