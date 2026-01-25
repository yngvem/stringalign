from __future__ import annotations

import html
import os
from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, cast, runtime_checkable

import numpy as np

import stringalign.tokenize
from stringalign._stringutils import create_cost_matrix as _create_cost_matrix

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Generator, Iterable
    from typing import Self

__all__ = [
    "AlignmentOperation",
    "MergableAlignmentOperation",
    "AlignmentTuple",
    "StringType",
    "Inserted",
    "Deleted",
    "Replaced",
    "Kept",
    "align_strings",
    "find_all_alignments",
    "combine_alignment_ops",
    "create_cost_matrix",
    "compute_levenshtein_distance_from_alignment",
    "levenshtein_distance",
]

_DEFAULT_RANDOM_SEED = int(os.getenv("STRINGALIGN_RANDOM_SEED", 42))
DEFAULT_RNG = np.random.default_rng(_DEFAULT_RANDOM_SEED)


@dataclass(frozen=True, slots=True)
class Deleted:
    """Class representing tokens that are deleted from the reference.

    For example, if the reference text is ``'hello'`` and the predicted text is ``'helo'``, then one ``'l'`` is deleted
    (if we're using character tokens).
    """

    substring: str

    def generalize(self) -> Replaced:
        return Replaced(reference=self.substring, predicted="")

    def simplify(self) -> Self:
        return self

    def to_html(self) -> tuple[str, str]:
        return (
            f'<span class="deleted reference">{html.escape(self.substring)}</span>',
            f'<span class="deleted predicted"></span>',
        )

    def __str__(self) -> str:
        return f"DELETED  '{self.substring}'"

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)


@dataclass(frozen=True, slots=True)
class Inserted:
    """Class representing tokens that are deleted from the reference.

    For example, if the reference text is ``'hello'`` and the predicted text is ``'helloo'``, then one ``'o'`` is
    inserted (if we're using character tokens).
    """

    substring: str

    def generalize(self) -> Replaced:
        return Replaced(reference="", predicted=self.substring)

    def simplify(self) -> Self:
        return self

    def to_html(self) -> tuple[str, str]:
        return (
            f'<span class="inserted reference"></span>',
            f'<span class="inserted predicted">{html.escape(self.substring)}</span>',
        )

    def __str__(self) -> str:
        return f"INSERTED '{self.substring}'"

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)


@dataclass(frozen=True, slots=True)
class Replaced:
    """Class representing tokens that are  from the reference.

    For example, if the reference text is ``'hello'`` and the predicted text is ``'hellø'``, then one ``'o'`` is
    replaced with a ``'ø'`` (if we're using character tokens).
    """

    reference: str
    predicted: str

    def generalize(self) -> Self:
        return self

    def simplify(self) -> AlignmentOperation:
        if not self.predicted:
            return Deleted(self.reference)
        if not self.reference:
            return Inserted(self.predicted)
        return self

    def merge(self, other: Replaced, tokenizer: stringalign.tokenize.Tokenizer) -> Replaced:
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can only merge Replace instance with other Replace instances, not {type(other)}")
        return Replaced(
            predicted=tokenizer.join((self.predicted, other.predicted)),
            reference=tokenizer.join((self.reference, other.reference)),
        )

    def to_html(self) -> tuple[str, str]:
        return (
            f'<span class="replaced reference">{html.escape(self.reference)}</span>',
            f'<span class="replaced predicted">{html.escape(self.predicted)}</span>',
        )

    def __str__(self) -> str:
        return f"REPLACED '{self.reference}' -> '{self.predicted}'"

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)


@dataclass(frozen=True, slots=True)
class Kept:
    """Class representing tokens that are kept from the reference.

    For example, if the reference text is ``'hi'`` and the predicted text is ``'h'``, then the ``'h'`` is
    kept while the ``'i'`` is not (if we're using character tokens).
    """

    substring: str

    @property
    def reference(self) -> str:
        return self.substring

    @property
    def predicted(self) -> str:
        return self.substring

    def generalize(self) -> Self:
        return self

    def simplify(self) -> Self:
        return self

    def merge(self, other: Kept, tokenizer: stringalign.tokenize.Tokenizer) -> Kept:
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can only merge Keep instance with other Keep instances, not {type(other)}")
        return Kept(substring=tokenizer.join((self.substring, other.substring)))

    def to_html(self) -> tuple[str, str]:
        return (
            f'<span class="kept reference">{html.escape(self.substring)}</span>',
            f'<span class="kept predicted">{html.escape(self.substring)}</span>',
        )

    def __str__(self) -> str:
        return f"KEPT     '{self.substring}'"

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)


@runtime_checkable
class AlignmentOperation(Protocol):
    """This class class is used as a union of :class:`Deleted`, :class:`Inserted`, :class:`Replaced`, and :class:`Kept`.

    We define it like this instead of using an explicit union type make the Sphinx documentation more readable.
    """

    def generalize(self) -> Kept | Replaced: ...

    def simplify(self) -> AlignmentOperation: ...

    def to_html(self) -> tuple[str, str]: ...


AlignmentTuple = tuple[AlignmentOperation, ...]
AlignmentList = list[AlignmentOperation]


def create_cost_matrix(reference_tokens: Iterable[str], predicted_tokens: Iterable[str]) -> np.ndarray:
    """Create the alignment cost matrix for the reference tokens and predicted tokens.

    Element `(i, j)` of this matrix corresponds to the cost of aligning the token with index `i` in the reference
    string with the token with index `j` in the predicted string. For more information, see e.g.
    :cite:p:`navarro2001guided` or :cite:p:`needleman1970general`.

    This is an internal function used by :func:`align_strings`, so you should probably not call this function directly.

    Parameters
    ----------
    reference_tokens:
        Iterable of tokens to align the predicted tokens against.
    predicted_tokens:
        Iterable of tokens to align against the reference tokens.

    Returns
    -------
    cost_matrix : np.ndarray
        Two dimensional numpy array of ints with shape `(len(reference_tokens), len(predicted_tokens))`.
    """
    return _create_cost_matrix(list(reference_tokens), list(predicted_tokens))


_ALIGNMENT_DIRECTIONS = {Kept: (1, 1), Replaced: (1, 1), Deleted: (1, 0), Inserted: (0, 1)}


def _backtrack(
    row: int, col: int, reference_clusters: list[str], predicted_clusters: list[str], cost_matrix: np.ndarray
) -> Generator[AlignmentOperation, None, None]:
    """Generator that yields all optimal alignment operations at the current position in the cost matrix."""
    if row > 0 and col > 0 and reference_clusters[row - 1] == predicted_clusters[col - 1]:
        yield Kept(reference_clusters[row - 1])
    if row > 0 and (col == 0 or cost_matrix[row, col] == cost_matrix[row - 1, col] + 1):
        yield Deleted(reference_clusters[row - 1])
    if col > 0 and (row == 0 or cost_matrix[row, col] == cost_matrix[row, col - 1] + 1):
        yield Inserted(predicted_clusters[col - 1])
    if row > 0 and col > 0 and cost_matrix[row, col] == cost_matrix[row - 1, col - 1] + 1:
        yield Replaced(reference_clusters[row - 1], predicted_clusters[col - 1])


class InvalidRngError(TypeError):
    def __init__(self, rng):
        t = type(rng)
        super().__init__(f"Invalid random state. Should be a numpy random number generator, an int or None, not {t}")


def align_strings(
    reference: str,
    predicted: str,
    tokenizer: stringalign.tokenize.Tokenizer | None = None,
    randomize_alignment: bool = False,
    random_state: np.random.Generator | int | None = None,
) -> tuple[AlignmentTuple, bool]:
    """Find one optimal alignment for the two strings and whether the alignment is unique or not.

    It uses the Needleman-Wunsch algorithm for optimal string alignment :cite:p:`needleman1970general`, which is a
    dynamic programming algorithm with :math:`O(mn)` time and memory complexity, where :math:`m` and :math:`n` are the
    length of the reference and predicted strings. This algorithm has been discovered many times, for a more thorough
    description, see e.g. :cite:p:`navarro2001guided`.

    Parameters
    ----------
    reference
        The reference string, also known as gold standard or ground truth.
    predicted
        The string to align with the reference.
    tokenizer : optional
        A tokenizer that turns a string into an iterable of tokens. For this function, it is sufficient that it is a
        callable that turns a string into an iterable of tokens. If not provided, then
        ``stringalign.tokenize.DEFAULT_TOKENIZER`` is used instead, which by default is a grapheme cluster (character)
        tokenizer.
    randomize_alignment
        If ``True``, then a random optimal alignment is chosen (slightly slower if enabled)
    random_state
        The NumPy RNG or a seed to create a NumPy RNG used for picking the optimal alignment. If ``None``, then the
        default RNG will be used instead.

    Returns
    -------
    alignment : AlignmentTuple
        A tuple of alignment operations.
    unique : bool
        A boolean flag that is True if alignment is unique and False otherwise.
    """
    if tokenizer is None:
        tokenizer = stringalign.tokenize.DEFAULT_TOKENIZER
    if randomize_alignment and random_state is None:
        random_state = DEFAULT_RNG
    elif randomize_alignment and isinstance(random_state, int):
        random_state = np.random.default_rng(random_state)
    if randomize_alignment and not isinstance(random_state, np.random.Generator):
        raise InvalidRngError(random_state)

    reference_clusters, predicted_clusters = tokenizer(reference), tokenizer(predicted)
    cost_matrix = create_cost_matrix(reference_clusters, predicted_clusters)

    alignment: AlignmentList = []
    row, col = cost_matrix.shape[0] - 1, cost_matrix.shape[1] - 1
    unique = True
    while row > 0 or col > 0:
        next_alignment_ops = _backtrack(row, col, reference_clusters, predicted_clusters, cost_matrix)

        if randomize_alignment:
            # Mypy doesn't understand that this is an RNG despite the exception throwing above, so we just cast it to
            # silence the false positive type error.
            random_state = cast(np.random.Generator, random_state)
            next_op = random_state.choice(list(next_alignment_ops))
        else:
            next_op = next(next_alignment_ops)

        alignment.append(next_op)
        unique = unique and (next(next_alignment_ops, None) is None)

        # Decrement row and/or col
        dr, dc = _ALIGNMENT_DIRECTIONS[next_op.__class__]
        row, col = row - dr, col - dc

    return tuple(alignment[::-1]), unique


def find_all_alignments(
    reference: str, predicted: str, tokenizer: stringalign.tokenize.Tokenizer | None = None
) -> Generator[AlignmentTuple, None, None]:
    """Works similarly to align_strings, but returns all possible alignments.

    It's implemented as a generator that yields all possible alignments. It holds a queue of alignments
    and every time the dynamic programming backtracking encounters a branching point, it creates adds
    the new branches to the queue.

    The backtracking is completed for one alignment before the next is started (with no caching, so the same
    subpaths might be traversed multiple times).

    This function has exponential worst-time time-complexity since the number of possible string alignments
    grows exponentially with the length of the strings.

    Parameters
    ----------
    reference
        The reference string, also known as gold standard or ground truth.
    predicted
        The string to align with the reference.
    tokenizer : optional
        A tokenizer that turns a string into an iterable of tokens. For this function, it is sufficient that it is a
        callable that turns a string into an iterable of tokens. If not provided, then
        ``stringalign.tokenize.DEFAULT_TOKENIZER`` is used instead, which by default is a grapheme cluster (character)
        tokenizer.

    Yields
    ------
    alignment : AlignmentTuple
        A tuple of alignment operations.
    """
    if tokenizer is None:
        tokenizer = stringalign.tokenize.DEFAULT_TOKENIZER

    reference_clusters, predicted_clusters = tokenizer(reference), tokenizer(predicted)
    cost_matrix = create_cost_matrix(reference_clusters, predicted_clusters)

    alignment_queue: deque[AlignmentList] = deque([[]])
    node_queue = deque([(cost_matrix.shape[0] - 1, cost_matrix.shape[1] - 1)])
    while node_queue:
        row, col = node_queue.popleft()
        alignment = alignment_queue.popleft()

        while row > 0 or col > 0:
            next_alignment_ops = _backtrack(row, col, reference_clusters, predicted_clusters, cost_matrix)
            next_op = next(next_alignment_ops)

            for alignment_op in next_alignment_ops:
                dr, dc = _ALIGNMENT_DIRECTIONS[alignment_op.__class__]
                alignment_queue.append(alignment + [alignment_op])
                node_queue.append((row - dr, col - dc))

            alignment.append(next_op)
            dr, dc = _ALIGNMENT_DIRECTIONS[next_op.__class__]
            row, col = row - dr, col - dc

        yield tuple(alignment[::-1])


def compute_levenshtein_distance_from_alignment(alignment: Iterable[AlignmentOperation]) -> int:
    """Compute the Levenshtein distance between two strings based on an optimal alignment between them.

    See :ref:`levenshtein_distance` for more information about the Levenshtein distance.

    Parameters
    ----------
    alignment
        An iterable representing the optimal alignment of two strings. Typically a tuple returned by :func:`align_strings`.

    Returns
    -------
    distance : int
        The Levenshtein distance between the two strings.
    """
    return len(tuple(op for op in alignment if not isinstance(op, Kept)))


def levenshtein_distance(
    reference: str, predicted: str, tokenizer: stringalign.tokenize.Tokenizer | None = None
) -> int:
    """Compute the Levenshtein distance between two strings given a tokenizer.

    See :ref:`levenshtein_distance` for more information about the Levenshtein distance.

    .. note::

        This function will first align the strings and then compute the Levenshtein distance.
        If you already have computed the alignment, you can use :func:`compute_levenshtein_distance_from_alignment`
        instead.

    Parameters
    ----------
    reference
        The reference string, also known as gold standard or ground truth.
    predicted
        The string to align with the reference.
    tokenizer
        A tokenizer that turns a string into an iterable of tokens. For this function, it is sufficient that it is a
        callable that turns a string into an iterable of tokens.

    Returns
    -------
    distance : int
        The Levenshtein distance between the two strings.
    """
    return compute_levenshtein_distance_from_alignment(align_strings(reference, predicted, tokenizer)[0])


def combine_alignment_ops(
    alignment: Iterable[AlignmentOperation], tokenizer: stringalign.tokenize.Tokenizer | None = None
) -> Generator[AlignmentOperation, None, None]:
    """Combine alignment operations to cover multiple tokens where possible.

    Sometimes, it can be useful to combine multiple alignment operations into single ones to e.g. find common
    multi-token insertions, deletions or replacements. For example, in handwritten text recognition, the letters
    ``'ll'`` might be replaced with a ``'u'`` or ``'rn'`` might be replaced with an ``'m'``. Such replacements are
    easily missed if we just consider single-token replacements.

    This generator will combine contiguous :class:`Kept` operations and contiguous "edit" operations (:class:`Deleted`,
    :class:`Inserted` and :class:`Replaced`) into single operations instead.

    Parameters
    ----------
    alignment
        Iterable of single-token alignment operations to combine.
    tokenizer : optional
        A tokenizer. The :meth:`Tokenizer.join` method is used to combine tokens to create multi-token alignment
        operations. If not provided, then
        ``stringalign.tokenize.DEFAULT_TOKENIZER`` is used instead, which by default is a grapheme cluster (character)
        tokenizer.

    Yields
    ------
    alignment_operation : AlignmentOperation
        Each alignment operation represents a contiguous block of either :class:`Kept` operations or "edit" operations.

    Examples
    --------

    Contiguous :class:`Kept` and edit operations are combined into single operations:

    >>> alignment = [Kept("h"), Kept("e"), Replaced("l", "u"), Deleted("l"), Kept("o")]
    >>> tuple(combine_alignment_ops(alignment))
    (Kept(substring='he'), Replaced(reference='ll', predicted='u'), Kept(substring='o'))

    Contiguous :class:`Deleted` and :class:`Inserted` operations keep their semantics when merged.

    >>> alignment = [Kept("h"), Kept("e"), Deleted("l"), Deleted("l"), Kept("o"), Inserted("!")]
    >>> tuple(combine_alignment_ops(alignment))
    (Kept(substring='he'), Deleted(substring='ll'), Kept(substring='o'), Inserted(substring='!'))
    """
    if tokenizer is None:
        tokenizer = stringalign.tokenize.DEFAULT_TOKENIZER
    alignment_iter = iter(alignment)

    # Get first operation and return if there alignment iterable is empty
    current_operation = next(alignment_iter, None)
    if current_operation is None:
        return
    current_operation = current_operation.generalize()

    # Iterate over the rest alignment operations, merging Keep blocks with other Keep blocks and
    # Replaced/Deleted/Inserted blocks with other Replaced/Deleted/Inserted blocks
    for operation in alignment_iter:
        operation = operation.generalize()

        # We cannot combine Keep-blocks with non-Keep blocks, so if either the current_operation
        # or the operation variable is a Keep block, and the other is not, then we yield our current
        # alignment operation and continue.
        if (isinstance(current_operation, Replaced) and isinstance(operation, Kept)) or (
            isinstance(current_operation, Kept) and isinstance(operation, Replaced)
        ):
            yield current_operation.simplify()
            current_operation = operation.generalize()
            continue

        # We ignore type issues here since we know that operation must be of the same type as current_operation
        current_operation = current_operation.merge(operation, tokenizer=tokenizer)  # type: ignore[arg-type]

    yield current_operation.simplify()
