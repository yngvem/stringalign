from collections import Counter

from stringalign.align import Delete, Insert, Replace
from stringalign.statistics import StringConfusionMatrix


def test_from_strings_and_alignment():
    reference = "abcbaa"
    predicted = "acdeai"
    alignment = [
        None,
        Insert("b"),
        None,
        Replace("d", "b"),
        Replace("e", "a"),
        None,
        Delete("i"),
    ]

    result = StringConfusionMatrix.from_strings_and_alignment(reference, predicted, alignment)

    assert result.true_positives == Counter({"a": 2, "c": 1})
    assert result.false_positives == Counter({"d": 1, "e": 1, "i": 1})
    assert result.false_negatives == Counter({"b": 2, "a": 1})


def test_from_strings_and_alignment_empty():
    result = StringConfusionMatrix.from_strings_and_alignment("", "", [])

    assert result.true_positives == Counter()
    assert result.false_positives == Counter()
    assert result.false_negatives == Counter()
