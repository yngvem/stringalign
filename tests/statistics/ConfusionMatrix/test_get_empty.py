from collections import Counter

from stringalign.align import Delete, Insert, Keep, Replace, align_strings
from stringalign.statistics import StringConfusionMatrix


def test_from_strings_and_alignment_empty() -> None:
    result = StringConfusionMatrix.get_empty()

    assert result.true_positives == Counter()
    assert result.false_positives == Counter()
    assert result.false_negatives == Counter()
    assert result.edit_counts == Counter()
