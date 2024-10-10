from collections import Counter, deque
from collections.abc import Generator
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Literal, Self, TypeVar

from stringalign.align import (
    AlignmentOperation,
    Keep,
    Replace,
    aggregate_alignment,
    align_strings,
)
from stringalign.error_classification.case_error import count_case_errors
from stringalign.error_classification.duplication_error import check_ngram_duplication_errors
from stringalign.statistics import StringConfusionMatrix
from stringalign.tokenize import Tokenizer

T = TypeVar("T")


def join_windows(
    center_string: str, previous_operation: AlignmentOperation | None, next_operation: AlignmentOperation | None
) -> str:
    window_text = ""
    if previous_operation is not None:
        window_text += previous_operation.substring
    window_text += center_string
    if next_operation is not None:
        window_text += next_operation.substring
    return window_text


def check_operation_for_case_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
) -> int:
    if not isinstance(current_operation, Replace):
        return False
    current_operation = current_operation.generalize()
    assert isinstance(current_operation, Replace)
    return count_case_errors(current_operation.replacement, current_operation.substring)


def check_operation_for_horizontal_segmentation_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
) -> bool:
    is_boundary = (previous_operation is None) or (next_operation is None)
    return is_boundary and not isinstance(current_operation, Keep)


def check_operation_for_ngram_duplication_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
    *,
    n: int,
    type: Literal["insert", "delete"] = "insert",
) -> bool:
    if isinstance(current_operation, Keep):
        return False
    current_operation = current_operation.generalize()
    assert isinstance(current_operation, Replace)

    window_text_reference = join_windows(current_operation.replacement, previous_operation, next_operation)
    window_text_prediction = join_windows(current_operation.substring, previous_operation, next_operation)
    return check_ngram_duplication_errors(window_text_reference, window_text_prediction, n=n, type=type)


@dataclass(frozen=True, slots=True)
class LineError:
    reference: str
    prediction: str
    alignment: tuple[AlignmentOperation, ...]
    horisontal_segmentation_errors: tuple[AlignmentOperation, ...]
    character_duplication_errors: tuple[AlignmentOperation, ...]
    removed_duplicate_character_errors: tuple[AlignmentOperation, ...]

    @classmethod
    def from_strings(cls, reference: str, prediction: str, tokenizer: Tokenizer | None) -> Self:
        alignment = tuple(aggregate_alignment(align_strings(reference, prediction, tokenizer=tokenizer)))
        window: deque[AlignmentOperation | None] = deque(maxlen=3)

        if not alignment:
            return cls(
                reference=reference,
                prediction=prediction,
                alignment=tuple(),
                horisontal_segmentation_errors=tuple(),
                character_duplication_errors=tuple(),
                removed_duplicate_character_errors=tuple(),
            )

        alignment_iterator = iter(alignment)
        window.append(None)
        window.append(next(alignment_iterator))

        horisontal_segmentation_errors = []
        character_duplication_errors = []
        removed_duplicate_character_errors = []
        op: AlignmentOperation | None
        for op in chain(alignment_iterator, (None, None)):
            window.append(op)
            if window[1] is None:
                break

            if check_operation_for_horizontal_segmentation_error(window[0], window[1], window[2]):
                horisontal_segmentation_errors.append(window[1])
            if check_operation_for_ngram_duplication_error(window[0], window[1], window[2], n=1, type="insert"):
                character_duplication_errors.append(window[1])
            if check_operation_for_ngram_duplication_error(window[0], window[1], window[2], n=1, type="delete"):
                removed_duplicate_character_errors.append(window[1])

        return cls(
            reference=reference,
            prediction=prediction,
            alignment=alignment,
            horisontal_segmentation_errors=tuple(horisontal_segmentation_errors),
            character_duplication_errors=tuple(character_duplication_errors),
            removed_duplicate_character_errors=tuple(removed_duplicate_character_errors),
        )


@dataclass(frozen=True, slots=True)
class TranscriptionEvaluator:
    references: tuple[str, ...]
    predictions: tuple[str, ...]
    line_errors: tuple[LineError, ...]

    @property
    def horisontal_segmentation_errors(self) -> Generator[LineError, None, None]:
        return (err for err in self.line_errors if err.horisontal_segmentation_errors)

    @property
    def character_duplication_errors(self) -> Generator[LineError, None, None]:
        return (err for err in self.line_errors if err.character_duplication_errors)

    @property
    def removed_duplicate_character_errors(self) -> Generator[LineError, None, None]:
        return (err for err in self.line_errors if err.removed_duplicate_character_errors)

    @property
    def alignment_operators(self) -> Counter[AlignmentOperation]:
        return Counter(op for err in self.line_errors for op in err.alignment)

    @classmethod
    def from_strings(cls, references: Iterable[str], predictions: Iterable[str], tokenizer: Tokenizer | None) -> Self:
        references = tuple(references)
        predictions = tuple(predictions)

        line_errors = tuple(
            LineError.from_strings(reference, prediction, tokenizer)
            for reference, prediction in zip(references, predictions, strict=True)
        )

        return cls(
            references=references,
            predictions=predictions,
            line_errors=line_errors,
        )
