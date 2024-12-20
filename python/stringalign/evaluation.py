from collections import Counter, deque
from collections.abc import Generator, Mapping
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
    predicted: str
    alignment: tuple[AlignmentOperation, ...]
    raw_alignment: tuple[AlignmentOperation, ...]
    unique_alignment: bool
    horisontal_segmentation_errors: tuple[AlignmentOperation, ...]
    character_duplication_errors: tuple[AlignmentOperation, ...]
    removed_duplicate_character_errors: tuple[AlignmentOperation, ...]
    case_errors: tuple[AlignmentOperation, ...]
    metadata: Mapping[str, str | int | float | tuple[str | bool | int | float, ...]] | None

    def summarise(self) -> dict[str, str | bool | int | float | tuple[str | bool | int | float, ...]]:
        metadata = self.metadata
        if metadata is None:
            metadata = {}

        return {
            "reference": self.reference,
            "predicted": self.predicted,
            "horisontal_segmentation_error": bool(self.horisontal_segmentation_errors),
            "character_duplication_error": bool(self.character_duplication_errors),
            "removed_duplicate_character_error": bool(self.removed_duplicate_character_errors),
            "case_error": bool(self.case_errors),
            **metadata,
        }

    @property
    def confusion_matrix(self) -> StringConfusionMatrix:
        return StringConfusionMatrix.from_strings_and_alignment(
            reference=self.reference,
            predicted=self.predicted,
            alignment=self.raw_alignment,
        )

    @classmethod
    def from_strings(
        cls,
        reference: str,
        predicted: str,
        tokenizer: Tokenizer | None,
        metadata: Mapping[str, str | int | float | tuple[str | int | float, ...]] | None = None,
    ) -> Self:
        raw_alignment, unique_alignment = align_strings(reference, predicted, tokenizer=tokenizer)
        alignment = tuple(aggregate_alignment(raw_alignment))
        window: deque[AlignmentOperation | None] = deque(maxlen=3)

        if not alignment:
            return cls(
                reference=reference,
                predicted=predicted,
                alignment=tuple(),
                raw_alignment=tuple(),
                unique_alignment=True,
                horisontal_segmentation_errors=tuple(),
                character_duplication_errors=tuple(),
                removed_duplicate_character_errors=tuple(),
                case_errors=tuple(),
                metadata=metadata,
            )

        alignment_iterator = iter(alignment)
        window.append(None)
        window.append(next(alignment_iterator))

        horisontal_segmentation_errors = []
        character_duplication_errors = []
        removed_duplicate_character_errors = []
        case_errors = []
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
            if check_operation_for_case_error(window[0], window[1], window[2]):
                case_errors.append(window[1])

        return cls(
            reference=reference,
            predicted=predicted,
            alignment=alignment,
            raw_alignment=tuple(raw_alignment),
            unique_alignment=unique_alignment,
            horisontal_segmentation_errors=tuple(horisontal_segmentation_errors),
            character_duplication_errors=tuple(character_duplication_errors),
            removed_duplicate_character_errors=tuple(removed_duplicate_character_errors),
            case_errors=tuple(case_errors),
            metadata=metadata,
        )

    def __str__(self) -> str:
        return f"LineError('{self.reference}', '{self.predicted}', metadata={self.metadata})"


@dataclass(frozen=True, slots=True)
class TranscriptionEvaluator:
    references: tuple[str, ...]
    predictions: tuple[str, ...]
    line_errors: tuple[LineError, ...]

    def dump(self) -> list[dict[str, tuple[str | bool | int | float, ...] | str | bool | int | float]]:
        return [le.summarise() for le in self.line_errors]

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
    def case_errors(self) -> Generator[LineError, None, None]:
        return (err for err in self.line_errors if err.case_errors)

    @property
    def not_unique_alignments(self) -> Generator[LineError]:
        return (err for err in self.line_errors if not err.unique_alignment)

    @property
    def alignment_operators(self) -> Counter[AlignmentOperation]:
        return Counter(op for err in self.line_errors for op in err.alignment)

    @property
    def confusion_matrix(self) -> StringConfusionMatrix:
        return sum((le.confusion_matrix for le in self.line_errors), start=StringConfusionMatrix.get_empty())

    @classmethod
    def from_strings(
        cls,
        references: Iterable[str],
        predictions: Iterable[str],
        tokenizer: Tokenizer | None = None,
        metadata: Iterable[Mapping[str, str | int | float | tuple[str | int | float, ...]] | None] | None = None,
    ) -> Self:
        references = tuple(references)
        predictions = tuple(predictions)
        if metadata is None:
            metadata = tuple(None for _ in references)

        line_errors = tuple(
            LineError.from_strings(reference, prediction, tokenizer, metadata=metadata)
            for reference, prediction, metadata in zip(references, predictions, metadata, strict=True)
        )

        return cls(
            references=references,
            predictions=predictions,
            line_errors=line_errors,
        )
