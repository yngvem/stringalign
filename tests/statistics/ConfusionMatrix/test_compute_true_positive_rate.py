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


def test_compute_true_positive_rate(sample_confusion_matrix: StringConfusionMatrix) -> None:
    tpr = sample_confusion_matrix.compute_true_positive_rate()
    assert tpr == pytest.approx({"a": 0.75, "b": 1.0, "c": 0.5, "e": 0})


def test_compute_true_positive_rate_aggregate(sample_confusion_matrix: StringConfusionMatrix) -> None:
    tpr = sample_confusion_matrix.compute_true_positive_rate(aggregate_over="ab")
    assert tpr == pytest.approx(5 / 6)


def test_compute_true_positive_rate_aliases(sample_confusion_matrix: StringConfusionMatrix) -> None:
    assert sample_confusion_matrix.compute_recall == sample_confusion_matrix.compute_true_positive_rate
    assert sample_confusion_matrix.compute_sensitivity == sample_confusion_matrix.compute_true_positive_rate
