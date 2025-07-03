from collections import Counter

from stringalign.align import align_strings
from stringalign.statistics import StringConfusionMatrix


def test_from_strings() -> None:
    reference = "abcbaa"
    predicted = "acdeai"
    alignment = align_strings(reference=reference, predicted=predicted)[0]

    result1 = StringConfusionMatrix.from_strings_and_alignment(reference, predicted, alignment)
    result2 = StringConfusionMatrix.from_strings(reference, predicted)

    assert result1 == result2


def test_from_strings_empty() -> None:
    """The confusion matrix should be empty when both strings are empty."""
    result = StringConfusionMatrix.from_strings("", "")

    assert result.true_positives == Counter()
    assert result.false_positives == Counter()
    assert result.false_negatives == Counter()
    assert result.edit_counts == Counter()
