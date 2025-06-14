from collections import Counter

import pytest
from stringalign.align import Deleted, Inserted, Kept, Replaced
from stringalign.statistics import StringConfusionMatrix


def test__add__simple_example() -> None:
    """The addition of two StringConfusionMatrix objects should sum the counts."""
    cm1 = StringConfusionMatrix(
        true_positives=Counter({"a": 3, "b": 2, "c": 1}),
        false_positives=Counter({"a": 1, "b": 1, "d": 1}),
        false_negatives=Counter({"a": 1, "c": 1, "e": 1}),
        edit_counts=Counter(
            {
                Kept("a"): 3,
                Kept("b"): 2,
                Kept("c"): 1,
                Inserted("a"): 1,
                Inserted("b"): 1,
                Deleted("a"): 1,
                Deleted("c"): 1,
                Replaced("d", "e"): 1,
            }
        ),
    )
    cm2 = StringConfusionMatrix(
        true_positives=Counter({"a": 3, "b": 2, "d": 1}),
        false_positives=Counter({"a": 1, "b": 1, "f": 1}),
        false_negatives=Counter({"a": 1, "c": 1, "g": 1}),
        edit_counts=Counter(
            {
                Kept("a"): 3,
                Kept("b"): 2,
                Kept("d"): 1,
                Inserted("a"): 1,
                Inserted("b"): 1,
                Deleted("a"): 1,
                Deleted("c"): 1,
                Replaced("f", "g"): 1,
            }
        ),
    )

    cm3 = cm1 + cm2
    assert cm3.true_positives == cm1.true_positives + cm2.true_positives
    assert cm3.false_positives == cm1.false_positives + cm2.false_positives
    assert cm3.false_negatives == cm1.false_negatives + cm2.false_negatives
    assert cm3.edit_counts == cm1.edit_counts + cm2.edit_counts


def test__add__with_non_cm() -> None:
    """Adding a StringConfusionMatrix to a non-StringConfusionMatrix should raise TypeError."""
    cm = StringConfusionMatrix.get_empty()
    with pytest.raises(TypeError):
        _ = cm + "this is not a confusion matrix"  # type: ignore[operator]
