from collections import deque
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Self

from stringalign.align import AlignmentOperation, Keep, aggregate_alignment, align_strings
from stringalign.tokenize import Tokenizer


def check_horizontal_segmentation_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
) -> bool:
    is_boundary = (previous_operation is None) or (next_operation is None)
    return is_boundary and not isinstance(current_operation, Keep)


@dataclass(frozen=True, slots=True)
class LineError:
    reference: str
    prediction: str
    alignment: tuple[AlignmentOperation, ...]
    horisontal_segmentation_errors: tuple[AlignmentOperation, ...]

    @classmethod
    def from_strings(cls, reference: str, prediction: str, tokenizer: Tokenizer | None) -> Self:
        alignment = tuple(aggregate_alignment(align_strings(reference, prediction, tokenizer=tokenizer)))
        window: deque[AlignmentOperation | None] = deque(maxlen=3)

        if not alignment:
            return cls(
                reference=reference, prediction=prediction, alignment=tuple(), horisontal_segmentation_errors=tuple()
            )

        alignment_iterator = iter(alignment)
        window.append(None)
        window.append(next(alignment_iterator))

        horisontal_segmentation_errors = []
        op: AlignmentOperation | None
        for op in chain(alignment_iterator, (None, None)):
            window.append(op)
            if window[1] is None:
                break

            if check_horizontal_segmentation_error(window[0], window[1], window[2]):
                horisontal_segmentation_errors.append(window[1])

        return cls(
            reference=reference,
            prediction=prediction,
            alignment=alignment,
            horisontal_segmentation_errors=tuple(horisontal_segmentation_errors),
        )


@dataclass(frozen=True, slots=True)
class TranscriptionEvaluator:
    references: tuple[str, ...]
    predictions: tuple[str, ...]
    line_errors: tuple[LineError, ...]

    horisontal_segmentation_errors: tuple[LineError, ...]

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
            horisontal_segmentation_errors=tuple(err for err in line_errors if err.horisontal_segmentation_errors),
        )
