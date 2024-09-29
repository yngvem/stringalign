from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, runtime_checkable

import numpy as np

import stringalign.tokenize

if TYPE_CHECKING:  # pragma: nocov
    from collections.abc import Generator, Iterable, Sequence
    from typing import Self


@runtime_checkable
class AlignmentOperation(Protocol):
    def generalize(self) -> MergableAlignmentOperation: ...
    def simplify(self) -> AlignmentOperation: ...


@runtime_checkable
class MergableAlignmentOperation(AlignmentOperation, Protocol):
    def merge(self, other: Self) -> Self: ...


AlignmentList = list[AlignmentOperation]


@dataclass(frozen=True, slots=True)
class Insert:
    substring: str

    def generalize(self) -> Replace:
        return Replace("", self.substring)

    def simplify(self) -> Self:
        return self


@dataclass(frozen=True, slots=True)
class Delete:
    substring: str

    def generalize(self) -> Replace:
        return Replace(self.substring, "")

    def simplify(self) -> Self:
        return self


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


def create_cost_matrix(reference: Sequence[str], predicted: Sequence[str]) -> np.ndarray:
    m, n = len(reference), len(predicted)
    cost_matrix = np.zeros((m + 1, n + 1))

    cost_matrix[:, 0] = np.arange(m + 1)
    cost_matrix[0, :] = np.arange(n + 1)

    for row in range(m):
        for col in range(n):
            if reference[row] == predicted[col]:
                cost_matrix[row + 1][col + 1] = cost_matrix[row][col]
            else:
                cost_matrix[row + 1][col + 1] = 1 + min(
                    cost_matrix[row][col + 1],
                    cost_matrix[row + 1][col],
                    cost_matrix[row][col],
                )
    return cost_matrix


def align_strings(
    reference: str, predicted: str, tokenizer: stringalign.tokenize.Tokenizer | None = None
) -> AlignmentList:
    if tokenizer is None:
        tokenizer = stringalign.tokenize.grapheme_cluster_tokenizer

    reference_clusters, predicted_clusters = tokenizer(reference), tokenizer(predicted)
    cost_matrix = create_cost_matrix(reference_clusters, predicted_clusters)

    alignment: AlignmentList = []
    row, col = cost_matrix.shape[0] - 1, cost_matrix.shape[1] - 1
    while row > 0 or col > 0:
        if row > 0 and col > 0 and reference_clusters[row - 1] == predicted_clusters[col - 1]:
            alignment.append(Keep(reference_clusters[row - 1]))
            row -= 1
            col -= 1
        elif row > 0 and (col == 0 or cost_matrix[row][col] == cost_matrix[row - 1][col] + 1):
            alignment.append(Insert(reference_clusters[row - 1]))
            row -= 1
        elif col > 0 and (row == 0 or cost_matrix[row][col] == cost_matrix[row][col - 1] + 1):
            alignment.append(Delete(predicted_clusters[col - 1]))
            col -= 1
        else:
            alignment.append(Replace(predicted_clusters[col - 1], reference_clusters[row - 1]))
            row -= 1
            col -= 1

    return alignment[::-1]


class _EmptyAlignment:
    def generalize(self) -> Self:
        return self

    def simplify(self) -> Self:
        return self

    def merge(self) -> Self:
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
