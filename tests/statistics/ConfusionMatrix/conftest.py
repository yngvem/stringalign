from collections import Counter

import pytest

from stringalign.statistics import StringConfusionMatrix


@pytest.fixture()
def sample_confusion_matrix() -> StringConfusionMatrix:
    return StringConfusionMatrix(
        true_positives=Counter({"a": 2, "b": 1, "c": 1}),
        false_positives=Counter({"d": 1, "e": 1}),
        false_negatives=Counter({"f": 1, "g": 1}),
    )
