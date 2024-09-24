from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self, Sequence

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass(frozen=True, slots=True)
class Insert:
    substring: str

    def as_replace(self) -> Replace:
        return Replace('', self.substring)
    
    def simplify(self) -> Self:
        return self


@dataclass(frozen=True, slots=True)
class Delete:
    substring: str

    def as_replace(self) -> Replace:
        return Replace(self.substring, '')
    
    def simplify(self) -> Self:
        return self


@dataclass(frozen=True, slots=True)
class Replace:
    replace_string: str
    replacement: str

    def as_replace(self) -> Self:
        return self

    def simplify(self) -> Replace | Insert | Delete:
        if not self.replace_string:
            return Insert(self.replacement)
        if not self.replacement:
            return Delete(self.replace_string)
        return self

    def merge(self, other: Replace) -> Replace:
        return Replace(
            replace_string=self.replace_string + other.replace_string,
            replacement=self.replacement + other.replacement
        )


AlignmentOperation = Insert | Delete | Replace
AlignmentList = list[AlignmentOperation | None]


def create_cost_matrix(reference: str, predicted: str) -> np.ndarray:
    m, n = len(reference), len(predicted)
    cost_matrix = np.zeros((m+1, n+1))
    
    cost_matrix[:, 0] = np.arange(m + 1)
    cost_matrix[0, :] = np.arange(n + 1)
    
    for row in range(m):
        for col in range(n):
            if reference[row] == predicted[col]:
                cost_matrix[row+1][col+1] = cost_matrix[row][col]
            else:
                cost_matrix[row+1][col+1] = 1 + min(
                    cost_matrix[row][col+1],
                    cost_matrix[row+1][col],
                    cost_matrix[row][col]
                )
    return cost_matrix


def character_align_strings(reference: str, predicted: str) -> np.ndarray:
    cost_matrix = create_cost_matrix(reference, predicted)
    
    alignment = []
    row, col = cost_matrix.shape[0] - 1, cost_matrix.shape[1] - 1
    while row > 0 or col > 0:
        if row > 0 and col > 0 and reference[row-1] == predicted[col-1]:
            alignment.append(None)
            row -= 1
            col -= 1
        elif row > 0 and (col == 0 or cost_matrix[row][col] == cost_matrix[row-1][col] + 1):
            alignment.append(Insert(reference[row-1]))
            row -= 1
        elif col > 0 and (row == 0 or cost_matrix[row][col] == cost_matrix[row][col-1] + 1):
            alignment.append(Delete(predicted[col-1]))
            col -= 1
        else:
            alignment.append(Replace(predicted[col-1], reference[row-1]))
            row -= 1
            col -= 1
    
    return alignment[::-1]


def aggregate_character_alignment(
    alignment: Sequence[AlignmentOperation | None]
) -> Generator[AlignmentOperation | None, None, None]:
    if not alignment:
        return

    current_operation = alignment[0]
    if current_operation is not None:
        current_operation = current_operation.as_replace()

    for operation in alignment[1:]:
        if operation is None and current_operation is None:
            yield None
            continue
        elif operation is None:  # and current_operation is not None
            yield current_operation.simplify()
            current_operation = None
            continue
        elif current_operation is None:  # and operation is not None
            current_operation = operation.as_replace()
            yield None
            continue

        # Now, we know that both `current_operation` is not None and `operation` is not None.
        # What we want to do now is to merge these two into one operation.
        current_operation = current_operation.merge(operation.as_replace())
    
    if current_operation:
        yield current_operation.simplify()
