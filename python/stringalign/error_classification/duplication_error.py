from collections.abc import Generator, Iterable, Sequence
from itertools import groupby
from typing import Literal, TypeVar

from stringalign.compat import batched
from stringalign.tokenize import Tokenizer

T = TypeVar("T")


def run_length_encode(iterable: Iterable[T]) -> tuple[tuple[T, int], ...]:
    """Run-length encode an iterable.

    Parameters
    ----------
    iterable
        The iterable to run-length encode.

    Returns
    -------
        Tuple where each element is a tuple containing a token and how many times to repeat it.

    Examples
    --------
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


def get_offsetted_batched(seq: Sequence[str], n: int, offset: int) -> Generator[tuple[str, ...], None, None]:
    """Get n-batches of a sequence with an offset.

    Parameters
    ----------
    seq
        Sequence of tokens to get run-length-encoding for.
    n
        Number of tokens to combine prior to to computing the run-length encoding.
    offset
        Number of tokens in the first batch.

    Yields
    ------
    tuple[T, ...]
        ``n``-tuples of tokens representing batches of consecutive tokens (if offset is different from 0, then the first yielded tuple has ``offset`` tokens).

    Examples
    --------
    >>> list(get_offsetted_batched("Hello", 2, offset=1))
    [('H',), ('e', 'l'), ('l', 'o')]
    >>> list(get_offsetted_batched("Hello", 2, offset=0))
    [('H', 'e'), ('l', 'l'), ('o',)]
    """
    if offset:
        yield tuple(seq[:offset])
    yield from batched(seq[offset:], n)


def get_all_n_batches(seq: Sequence[str], n: int) -> Generator[tuple[str, ...], None, None]:
    """Get all n-batches of a sequence.

    Parameters
    ----------
    seq
        Sequence of tokens to get run-length-encoding for.
    n
        Number of tokens to combine prior to to computing the run-length encoding.

    Yields
    ------
    tuple[T, ...]
        All ``n``-batches of tokens with all offsets up to ``n``.

    Examples
    --------
    >>> tuple(get_all_n_batches("Hello", 1))
    (('H', 'e', 'l', 'l', 'o'),)
    >>> tuple(get_all_n_batches("bananas", 2))
    (('ba', 'na', 'na', 's'), ('b', 'an', 'an', 'as'))
    """

    return (tuple("".join(batch) for batch in get_offsetted_batched(seq, n, offset)) for offset in range(n))


def get_all_n_run_length_encodings(seq: Sequence[str], n: int) -> Generator[tuple[tuple[str, int], ...], None, None]:
    """Get all n-run length encodings of a sequence.

    Parameters
    ----------
    seq
        Sequence of tokens to get run-length-encoding for.
    n
        Number of tokens to combine prior to to computing the run-length encoding.

    Yields
    ------
    tuple[tuple[T, int], ...]
        The first yielded element is the ``n``-run-length encoding with offset 0, the second has offset 1
        and so on up to ``n``.

    Examples
    --------
    >>> tuple(get_all_n_run_length_encodings("Hello", 1))
    ((('H', 1), ('e', 1), ('l', 2), ('o', 1)),)
    >>> tuple(get_all_n_run_length_encodings("bananas", 2))
    ((('ba', 1), ('na', 2), ('s', 1)), (('b', 1), ('an', 2), ('as', 1)))
    """

    return (run_length_encode(batch) for batch in get_all_n_batches(seq, n))


def check_ngram_duplication_errors(
    reference: str,
    predicted: str,
    *,
    n: int,
    error_type: Literal["inserted", "deleted"],
    tokenizer: Tokenizer,
) -> bool:
    """Check if the only difference between the reference and the predicted string is from character duplication errors.

    If the ``error_type`` is ``"inserted"``, then it checks if the only difference between the two strings is due to the
    run length of one or more n-grams is larger in the predicted string compared to the reference string. Similarly, if
    the error type is ``"deleted"``, it checks if the only difference between the two strings is that the run length one
    or more n-grams of the predicted string is smaller than that of the reference string.

    Parameters
    ----------
    reference
        The reference string, also known as gold standard or ground truth.
    predicted
        The predicted string to compare against the reference.
    n
        The length of the n-grams.
    error_type
        ``"inserted"`` or ``"deleted"``, specifies if the function checks for increasing or decreasing n-gram run lengths.
    tokenizer
        The tokenizer.

    Returns
    -------
    bool
        True if the only reason the reference and predicted string is different is a change in token run lengths.

    Examples
    --------
    >>> import stringalign.tokenize
    >>> tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()
    >>> check_ngram_duplication_errors("hello", "helo", n=1, error_type="deleted", tokenizer=tokenizer)
    True
    >>> check_ngram_duplication_errors("hello", "helo", n=1, error_type="inserted", tokenizer=tokenizer)
    False
    >>> check_ngram_duplication_errors("hello", "helllo", n=1, error_type="deleted", tokenizer=tokenizer)
    False
    >>> check_ngram_duplication_errors("hello", "helllo", n=1, error_type="inserted", tokenizer=tokenizer)
    True

    We can also check for multi-token n-gram errors

    >>> check_ngram_duplication_errors("hello", "hellolo", n=2, error_type="inserted", tokenizer=tokenizer)
    True
    >>> check_ngram_duplication_errors("hellolo", "hello", n=2, error_type="deleted", tokenizer=tokenizer)
    True

    And with other tokenizers

    >>> tokenizer = stringalign.tokenize.UnicodeWordTokenizer()
    >>> check_ngram_duplication_errors("hello bye", "hello bye bye", n=1, error_type="inserted", tokenizer=tokenizer)
    True
    >>> check_ngram_duplication_errors("hello bye bye", "hello bye", n=1, error_type="deleted", tokenizer=tokenizer)
    True


    """
    if not (error_type := error_type.lower()) in ("inserted", "deleted"):  # type: ignore
        raise ValueError(f"Invalid duplication error type: {error_type}, must be either 'inserted' or 'deleted'")

    run_length_encodings_reference = get_all_n_run_length_encodings(tokenizer(reference), n)
    run_length_encodings_prediction = get_all_n_run_length_encodings(tokenizer(predicted), n)

    out = False
    for encoding_n1, encoding_n2 in zip(run_length_encodings_reference, run_length_encodings_prediction):
        if len(encoding_n1) != len(encoding_n2):
            continue

        for encoding1, encoding2 in zip(encoding_n1, encoding_n2):
            if encoding1[0] != encoding2[0]:
                break
            elif encoding1[1] < encoding2[1] and error_type == "inserted":
                out = True
            elif encoding1[1] > encoding2[1] and error_type == "deleted":
                out = True

    return out
