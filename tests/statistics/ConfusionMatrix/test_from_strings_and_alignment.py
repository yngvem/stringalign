from collections import Counter

from stringalign.align import Delete, Insert, Replace, align_strings
from stringalign.statistics import StringConfusionMatrix


def test_from_strings_and_alignment() -> None:
    reference = "abcbaa"
    predicted = "acdeai"
    alignment = align_strings(reference=reference, predicted=predicted)[0]

    result = StringConfusionMatrix.from_strings_and_alignment(reference, predicted, alignment)

    assert result.true_positives == Counter({"a": 2, "c": 1})
    assert result.false_positives == Counter({"d": 1, "e": 1, "i": 1})
    assert result.false_negatives == Counter({"b": 2, "a": 1})
    assert result.edit_counts == Counter(
        {
            Insert("b"): 1,
            Replace("d", "b"): 1,
            Replace("e", "a"): 1,
            Delete("i"): 1,
        }
    )


def test_from_strings_and_alignment_empty() -> None:
    result = StringConfusionMatrix.from_strings_and_alignment("", "", [])

    assert result.true_positives == Counter()
    assert result.false_positives == Counter()
    assert result.false_negatives == Counter()
    assert result.edit_counts == Counter()
