from collections import Counter, defaultdict, deque
from collections.abc import Generator, Hashable, Iterator, Mapping
from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from typing import Any, Iterable, Literal, Self, TypeVar

import stringalign
from stringalign.align import (
    AlignmentOperation,
    AlignmentTuple,
    Kept,
    Replaced,
    align_strings,
    combine_alignment_ops,
)
from stringalign.error_classification.case_error import count_case_errors
from stringalign.error_classification.confusable_error import count_confusable_errors
from stringalign.error_classification.diacritic_error import count_diacritic_errors
from stringalign.error_classification.duplication_error import check_ngram_duplication_errors
from stringalign.normalize import StringNormalizer
from stringalign.statistics import StringConfusionMatrix
from stringalign.tokenize import Tokenizer
from stringalign.visualize import HtmlString, create_alignment_html

T = TypeVar("T")


def join_windows(center_string: str, previous_operation: Kept | None, next_operation: Kept | None) -> str:
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
    if not isinstance(current_operation, Replaced):
        return False
    current_operation = current_operation.generalize()
    assert isinstance(current_operation, Replaced)
    return count_case_errors(current_operation.reference, current_operation.predicted)


def check_operation_for_diacritic_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
) -> int:
    current_operation = current_operation.generalize()
    if isinstance(current_operation, Kept):
        return False

    return count_diacritic_errors(current_operation.reference, current_operation.predicted)


def check_operation_for_confusable_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
    *,
    tokenizer: Tokenizer,
) -> int:
    current_operation = current_operation.generalize()
    if isinstance(current_operation, Kept):
        return False
    return count_confusable_errors(
        current_operation.reference,
        current_operation.predicted,
        tokenizer=tokenizer,
        consider_confusables="confusables",
    )


def check_operation_for_horizontal_segmentation_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
) -> bool:
    is_boundary = (previous_operation is None) or (next_operation is None)
    return is_boundary and not isinstance(current_operation, Kept)


def check_operation_for_ngram_duplication_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
    *,
    n: int,
    error_type: Literal["insert", "delete"] = "insert",
) -> bool:
    if isinstance(current_operation, Kept):
        return False
    current_operation = current_operation.generalize()
    assert isinstance(current_operation, Replaced)
    assert isinstance(next_operation, (Kept, type(None)))
    assert isinstance(previous_operation, (Kept, type(None)))

    window_text_reference = join_windows(current_operation.reference, previous_operation, next_operation)
    window_text_prediction = join_windows(current_operation.predicted, previous_operation, next_operation)
    return check_ngram_duplication_errors(window_text_reference, window_text_prediction, n=n, error_type=error_type)


def _safe_hash(value: Any) -> int:
    try:
        return hash(value)
    except TypeError:
        import pickle

        return hash(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))


class FrozenDict(Mapping[Hashable, Any]):
    def __init__(self, data: Mapping[Hashable, Any] | None = None):
        if not data:
            data = {}
        self._data = deepcopy(data)
        self._hash: int | None = None

    def __getitem__(self, key: Hashable) -> Any:
        return self._data[key]

    def __iter__(self) -> Iterator[Hashable]:
        return iter(self._data)

    def __contains__(self, value: Any) -> bool:
        return value in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __hash__(self) -> int:
        if self._hash is not None:
            return self._hash

        keys = tuple(self.keys())
        values = tuple(_safe_hash(v) for v in self.values())
        self._hash = hash((keys, values))
        return self._hash

    def __repr__(self):
        return f"{type(self).__name__}({self._data!r})"


@dataclass(frozen=True, slots=False)
class LineError:
    reference: str
    predicted: str
    alignment: AlignmentTuple
    raw_alignment: AlignmentTuple
    unique_alignment: bool
    horisontal_segmentation_errors: AlignmentTuple
    character_duplication_errors: AlignmentTuple
    removed_duplicate_character_errors: AlignmentTuple
    diacritic_errors: AlignmentTuple
    confusable_errors: AlignmentTuple
    case_errors: AlignmentTuple
    metadata: FrozenDict | None
    tokenizer: Tokenizer | None

    def summarise(self) -> dict[Hashable, Hashable]:
        metadata = self.metadata
        if metadata is None:
            metadata = FrozenDict()

        return {
            "reference": self.reference,
            "predicted": self.predicted,
            "horisontal_segmentation_error": bool(self.horisontal_segmentation_errors),
            "character_duplication_error": bool(self.character_duplication_errors),
            "removed_duplicate_character_error": bool(self.removed_duplicate_character_errors),
            "diacritic_error": bool(self.diacritic_errors),
            "confusable_error": bool(self.confusable_errors),
            "case_error": bool(self.case_errors),
            **metadata,
        }

    @cached_property
    def confusion_matrix(self) -> StringConfusionMatrix:
        return StringConfusionMatrix.from_strings_and_alignment(
            reference=self.reference, predicted=self.predicted, alignment=self.raw_alignment, tokenizer=self.tokenizer
        )

    @classmethod
    def from_strings(
        cls,
        reference: str,
        predicted: str,
        tokenizer: Tokenizer | None,
        metadata: Mapping[Hashable, Hashable] | None = None,
    ) -> Self:
        if tokenizer is None:
            tokenizer = stringalign.tokenize.DEFAULT_TOKENIZER

        raw_alignment, unique_alignment = align_strings(reference, predicted, tokenizer=tokenizer)
        alignment = tuple(combine_alignment_ops(raw_alignment, tokenizer=tokenizer))
        if metadata is not None:
            frozen_metadata = FrozenDict(metadata)
        else:
            frozen_metadata = None

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
                diacritic_errors=tuple(),
                confusable_errors=tuple(),
                case_errors=tuple(),
                metadata=frozen_metadata,
                tokenizer=tokenizer,
            )

        alignment_iterator = iter(alignment)
        window: deque[AlignmentOperation | None] = deque(maxlen=3)
        window.append(None)
        window.append(next(alignment_iterator))

        horisontal_segmentation_errors = []
        character_duplication_errors = []
        removed_duplicate_character_errors = []
        diacritic_errors = []
        confusable_errors = []
        case_errors = []
        op: AlignmentOperation | None
        for op in chain(alignment_iterator, (None, None)):
            window.append(op)
            if window[1] is None:
                break

            if check_operation_for_horizontal_segmentation_error(window[0], window[1], window[2]):
                horisontal_segmentation_errors.append(window[1])
            if check_operation_for_ngram_duplication_error(window[0], window[1], window[2], n=1, error_type="insert"):
                character_duplication_errors.append(window[1])
            if check_operation_for_ngram_duplication_error(window[0], window[1], window[2], n=1, error_type="delete"):
                removed_duplicate_character_errors.append(window[1])
            if check_operation_for_diacritic_error(window[0], window[1], window[2]):
                diacritic_errors.append(window[1])
            if check_operation_for_confusable_error(window[0], window[1], window[2], tokenizer=tokenizer):
                confusable_errors.append(window[1])
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
            diacritic_errors=tuple(diacritic_errors),
            confusable_errors=tuple(confusable_errors),
            case_errors=tuple(case_errors),
            metadata=frozen_metadata,
            tokenizer=tokenizer,
        )

    def visualize(self, which: Literal["raw", "combined"] = "raw", space_tokens: bool = False) -> HtmlString:
        if which == "raw":
            alignment = self.raw_alignment
        else:
            alignment = self.alignment

        return create_alignment_html(alignment=alignment, space_tokens=space_tokens)

    def __repr__(self) -> str:
        return f"LineError('{self.reference}', '{self.predicted}', metadata={self.metadata})"

    __str__ = __repr__


@dataclass(frozen=True, slots=False)
class TranscriptionEvaluator:
    references: tuple[str, ...]
    predictions: tuple[str, ...]
    line_errors: tuple[LineError, ...]

    def dump(self) -> list[dict[Hashable, Hashable]]:
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
    def diacritic_errors(self) -> Generator[LineError, None, None]:
        return (err for err in self.line_errors if err.diacritic_errors)

    @property
    def confusable_errors(self) -> Generator[LineError, None, None]:
        return (err for err in self.line_errors if err.confusable_errors)

    @property
    def case_errors(self) -> Generator[LineError, None, None]:
        return (err for err in self.line_errors if err.case_errors)

    @property
    def not_unique_alignments(self) -> Generator[LineError]:
        return (err for err in self.line_errors if not err.unique_alignment)

    @cached_property
    def alignment_operators(self) -> Counter[AlignmentOperation]:
        return Counter(op for err in self.line_errors for op in err.alignment)

    @cached_property
    def confusion_matrix(self) -> StringConfusionMatrix:
        return sum((le.confusion_matrix for le in self.line_errors), start=StringConfusionMatrix.get_empty())

    @cached_property
    def line_error_raw_lookup(self) -> dict[AlignmentOperation, frozenset[LineError]]:
        out = defaultdict(set)
        for line_error in self.line_errors:
            for alignment_op in line_error.raw_alignment:
                out[alignment_op].add(line_error)

        return {k: frozenset(v) for k, v in out.items()}

    @cached_property
    def line_error_combined_lookup(self) -> dict[AlignmentOperation, frozenset[LineError]]:
        out = defaultdict(set)
        for line_error in self.line_errors:
            for alignment_op in line_error.alignment:
                out[alignment_op].add(line_error)

        return {k: frozenset(v) for k, v in out.items()}

    @cached_property
    def false_positive_lookup(self) -> dict[str, frozenset[LineError]]:
        out = defaultdict(set)
        for line_error in self.line_errors:
            for token in line_error.confusion_matrix.false_positives:
                out[token].add(line_error)

        return {k: frozenset(v) for k, v in out.items()}

    @cached_property
    def false_negative_lookup(self) -> dict[str, frozenset[LineError]]:
        out = defaultdict(set)
        for line_error in self.line_errors:
            for token in line_error.confusion_matrix.false_negatives:
                out[token].add(line_error)

        return {k: frozenset(v) for k, v in out.items()}

    @classmethod
    def from_strings(
        cls,
        references: Iterable[str],
        predictions: Iterable[str],
        tokenizer: Tokenizer | None = None,
        metadata: Iterable[Mapping[Hashable, Hashable] | None] | None = None,
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

    def __len__(self) -> int:
        return len(self.line_errors)

    def __repr__(self) -> str:
        return f"TranscriptionEvaluator(len={len(self)})"

    __str__ = __repr__
