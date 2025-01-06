from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Protocol, runtime_checkable

import stringalign.tokenize
from stringalign._stringutils import create_cost_matrix as _create_cost_matrix

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Generator, Iterable
    from typing import Self

    import numpy as np

__all__ = [
    "AlignmentOperation",
    "MergableAlignmentOperation",
    "AlignmentTuple",
    "StringType",
    "Insert",
    "Delete",
    "Replace",
    "Keep",
    "align_strings",
    "aggregate_alignment",
    "create_cost_matrix",
]


@runtime_checkable
class AlignmentOperation(Protocol):
    @property
    def substring(self) -> str: ...

    def generalize(self) -> MergableAlignmentOperation: ...
    def simplify(self) -> AlignmentOperation: ...


@runtime_checkable
class MergableAlignmentOperation(AlignmentOperation, Protocol):
    def merge(self, other: Self) -> Self: ...


AlignmentTuple = tuple[AlignmentOperation, ...]
AlignmentList = list[AlignmentOperation]


@dataclass(frozen=True, slots=True)
class Insert:
    substring: str

    def generalize(self) -> Replace:
        return Replace("", self.substring)

    def simplify(self) -> Self:
        return self

    def to_html(self) -> tuple[str, str]:
        return (
            f'<span class="insert reference">{self.substring}</span>',
            f'<span class="insert predicted"></span>',
        )


@dataclass(frozen=True, slots=True)
class Delete:
    substring: str

    def generalize(self) -> Replace:
        return Replace(self.substring, "")

    def simplify(self) -> Self:
        return self

    def to_html(self) -> tuple[str, str]:
        return (
            f'<span class="delete reference"></span>',
            f'<span class="delete predicted">{self.substring}</span>',
        )


@dataclass(frozen=True, slots=True)
class Replace:
    substring: str
    replacement: str

    def generalize(self) -> Self:
        return self

    def simplify(self) -> AlignmentOperation:
        if not self.substring:
            return Insert(self.replacement)
        if not self.replacement:
            return Delete(self.substring)
        return self

    def merge(self, other: Replace) -> Replace:
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can only merge Replace instance with other Replace instances, not {type(other)}")
        return Replace(
            substring=self.substring + other.substring,
            replacement=self.replacement + other.replacement,
        )

    def to_html(self) -> tuple[str, str]:
        return (
            f'<span class="replace reference">{self.replacement}</span>',
            f'<span class="replace predicted">{self.substring}</span>',
        )


@dataclass(frozen=True, slots=True)
class Keep:
    substring: str

    def generalize(self) -> Self:
        return self

    def simplify(self) -> Self:
        return self

    def merge(self, other: Keep) -> Keep:
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can only merge Keep instance with other Keep instances, not {type(other)}")
        return Keep(substring=self.substring + other.substring)

    def to_html(self) -> tuple[str, str]:
        return (
            f'<span class="keep reference">{self.substring}</span>',
            f'<span class="keep predicted">{self.substring}</span>',
        )


def create_cost_matrix(reference_tokens: Iterable[str], predicted_tokens: Iterable[str]) -> np.ndarray:
    return _create_cost_matrix(list(reference_tokens), list(predicted_tokens))


_ALIGNMENT_DIRECTIONS = {Keep: (1, 1), Replace: (1, 1), Insert: (1, 0), Delete: (0, 1)}


def _backtrack(
    row: int, col: int, reference_clusters: list[str], predicted_clusters: list[str], cost_matrix: np.ndarray
) -> Generator[AlignmentOperation, None, None]:
    """Generator that yields all optimal alignment operations at the current position in the cost matrix."""
    if row > 0 and col > 0 and reference_clusters[row - 1] == predicted_clusters[col - 1]:
        yield Keep(reference_clusters[row - 1])
    if row > 0 and (col == 0 or cost_matrix[row, col] == cost_matrix[row - 1, col] + 1):
        yield Insert(reference_clusters[row - 1])
    if col > 0 and (row == 0 or cost_matrix[row, col] == cost_matrix[row, col - 1] + 1):
        yield Delete(predicted_clusters[col - 1])
    if row > 0 and col > 0 and cost_matrix[row, col] == cost_matrix[row - 1, col - 1] + 1:
        yield Replace(predicted_clusters[col - 1], reference_clusters[row - 1])


def align_strings(
    reference: str, predicted: str, tokenizer: stringalign.tokenize.Tokenizer | None = None
) -> tuple[AlignmentTuple, bool]:
    if tokenizer is None:
        tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()

    reference_clusters, predicted_clusters = tokenizer(reference), tokenizer(predicted)
    cost_matrix = create_cost_matrix(reference_clusters, predicted_clusters)

    alignment: AlignmentList = []
    row, col = cost_matrix.shape[0] - 1, cost_matrix.shape[1] - 1
    unique = True
    while row > 0 or col > 0:
        next_alignment_ops = _backtrack(row, col, reference_clusters, predicted_clusters, cost_matrix)
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

    It's implemented as a generator that yields all possible alignments. It holds a que of alignments
    and every time the dynamic programming backtracking encounters a branching point, it creates adds
    the new branches to the queue.

    The backtracking is completed for one alignment before the next is started (with no caching, so the same
    subpaths might be traversed multiple times).
    """
    if tokenizer is None:
        tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()

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


def compute_levenshtein_distance_from_alignment(alignment: AlignmentTuple) -> int:
    return len(tuple(op for op in alignment if not isinstance(op, Keep)))


def levenshtein_distance(
    reference: str, predicted: str, tokenizer: stringalign.tokenize.Tokenizer | None = None
) -> int:
    return compute_levenshtein_distance_from_alignment(align_strings(reference, predicted, tokenizer)[0])


class _EmptyAlignment:
    """Used as a sentinel object that will make mypy happy."""

    def generalize(self) -> Self:  # pragma: no cover
        return self

    def simplify(self) -> Self:  # pragma: no cover
        return self

    def merge(self) -> Self:  # pragma: no cover
        return self


_EMPTY_ALIGNMENT = _EmptyAlignment()


def aggregate_alignment(
    alignment: Iterable[AlignmentOperation],
) -> Generator[AlignmentOperation, None, None]:
    alignment_iter = iter(alignment)

    # Get first operation and return if there alignment iterable is empty
    current_operation = next(alignment_iter, _EMPTY_ALIGNMENT).generalize()
    if isinstance(current_operation, _EmptyAlignment):
        return

    # Iterate over the rest alignment operations, merging Keep blocks with other Keep blocks and
    # Replace/Delete/Insert blocks with other Replace/Delete/Insert blocks
    for operation in alignment_iter:
        # We cannot aggregate Keep-blocks with non-Keep blocks, so if either the current_operation
        # or the operation variable is a Keep block, and the other is not, then we yield our current
        # alignment operation and continue.
        if (not isinstance(current_operation, Keep) and isinstance(operation, Keep)) or (
            isinstance(current_operation, Keep) and not isinstance(operation, Keep)
        ):
            yield current_operation.simplify()
            current_operation = operation.generalize()
            continue

        current_operation = current_operation.merge(operation.generalize())

    yield current_operation.simplify()
