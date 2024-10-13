from collections import Counter

import pytest
from stringalign.statistics import StringConfusionMatrix


@pytest.fixture
def sample_confusion_matrix() -> StringConfusionMatrix:
    return StringConfusionMatrix(
        true_positives=Counter({"a": 3, "b": 2, "c": 1}),
        false_positives=Counter({"a": 1, "b": 1, "d": 1}),
        false_negatives=Counter({"a": 1, "c": 1, "e": 1}),
        edit_counts=Counter(),
    )


def test_compute_positive_predictive_value(sample_confusion_matrix: StringConfusionMatrix) -> None:
    ppv = sample_confusion_matrix.compute_positive_predictive_value()
    assert ppv == pytest.approx({"a": 0.75, "b": 2 / 3, "c": 1.0})


def test_compute_positive_predictive_value_aggregate(sample_confusion_matrix: StringConfusionMatrix) -> None:
    ppv = sample_confusion_matrix.compute_positive_predictive_value(aggregate_over="ab")
    assert ppv == pytest.approx(5 / 7)
