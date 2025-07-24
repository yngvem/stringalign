from typing import Literal

from stringalign.align import Kept, align_strings
from stringalign.normalize import StringNormalizer
from stringalign.tokenize import Tokenizer


def count_confusable_errors(
    reference: str,
    predicted: str,
    tokenizer: Tokenizer,
    consider_confusables: Literal["confusables", "intentional"] | dict[str, str],
) -> int:
    normalizer = StringNormalizer(normalization=None, resolve_confusables=consider_confusables)
    alignment, _ = align_strings(reference, predicted, tokenizer=tokenizer)

    num_confusable_errors = 0
    for alignment_op in alignment:
        if isinstance(alignment_op, Kept):
            continue

        alignment_op = alignment_op.generalize()
        resolved_ref = normalizer(alignment_op.reference)
        resolved_pred = normalizer(alignment_op.predicted)
        num_confusable_errors += resolved_ref == resolved_pred

    return num_confusable_errors
