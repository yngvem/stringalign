from collections import Counter

import pytest
from stringalign.align import (
    Deleted,
    Inserted,
    Replaced,
    align_strings,
    combine_alignment_ops,
)
from stringalign.statistics import CombinedAlignmentWarning, StringConfusionMatrix
from stringalign.tokenize import UnicodeWordTokenizer


def test_warning_raised_on_combined_alignment_default_tokenizer() -> None:
    reference = "abc"
    predicted = "xyz"
    alignment, _unique = align_strings(reference=reference, predicted=predicted, tokenizer=None)
    combined_alignment = list(combine_alignment_ops(alignment))

    with pytest.warns(CombinedAlignmentWarning):
        StringConfusionMatrix.from_strings_and_alignment(reference, predicted, combined_alignment)


def test_warning_raised_on_combined_alignment_unicode_word_tokenizer() -> None:
    reference = "abc def"
    predicted = "uvw xyz"
    alignment, _unique = align_strings(reference=reference, predicted=predicted, tokenizer=UnicodeWordTokenizer())
    combined_alignment = list(combine_alignment_ops(alignment))

    with pytest.warns(CombinedAlignmentWarning):
        StringConfusionMatrix.from_strings_and_alignment(reference, predicted, combined_alignment)


def test_from_strings_and_alignment() -> None:
    reference = "abcbaa"
    predicted = "acdeaai"
    alignment = align_strings(reference=reference, predicted=predicted)[0]

    result = StringConfusionMatrix.from_strings_and_alignment(reference, predicted, alignment)

    assert result.true_positives == Counter({"a": 3})
    assert result.false_positives == Counter({"c": 1, "d": 1, "e": 1, "i": 1})
    assert result.false_negatives == Counter({"c": 1, "b": 2})
    assert result.edit_counts == Counter(
        {
            Replaced("b", "c"): 1,
            Replaced("c", "d"): 1,
            Replaced("b", "e"): 1,
            Inserted("i"): 1,
        }
    )


def test_from_strings_and_alignment_empty() -> None:
    result = StringConfusionMatrix.from_strings_and_alignment("", "", [])

    assert result.true_positives == Counter()
    assert result.false_positives == Counter()
    assert result.false_negatives == Counter()
    assert result.edit_counts == Counter()
