from collections import Counter

from stringalign.align import Delete, Insert, Keep, Replace
from stringalign.statistics import StringConfusionMatrix


def test__add__() -> None:
    cm1 = StringConfusionMatrix(
        true_positives=Counter({"a": 3, "b": 2, "c": 1}),
        false_positives=Counter({"a": 1, "b": 1, "d": 1}),
        false_negatives=Counter({"a": 1, "c": 1, "e": 1}),
        edit_counts=Counter(
            {
                Keep("a"): 3,
                Keep("b"): 2,
                Keep("c"): 1,
                Delete("a"): 1,
                Delete("b"): 1,
                Insert("a"): 1,
                Insert("c"): 1,
                Replace("d", "e"): 1,
            }
        ),
    )
    cm2 = StringConfusionMatrix(
        true_positives=Counter({"a": 3, "b": 2, "d": 1}),
        false_positives=Counter({"a": 1, "b": 1, "f": 1}),
        false_negatives=Counter({"a": 1, "c": 1, "g": 1}),
        edit_counts=Counter(
            {
                Keep("a"): 3,
                Keep("b"): 2,
                Keep("d"): 1,
                Delete("a"): 1,
                Delete("b"): 1,
                Insert("a"): 1,
                Insert("c"): 1,
                Replace("f", "g"): 1,
            }
        ),
    )

    cm3 = cm1 + cm2
    assert cm3.true_positives == cm1.true_positives + cm2.true_positives
    assert cm3.false_positives == cm1.false_positives + cm2.false_positives
    assert cm3.false_negatives == cm1.false_negatives + cm2.false_negatives
    assert cm3.edit_counts == cm1.edit_counts + cm2.edit_counts
