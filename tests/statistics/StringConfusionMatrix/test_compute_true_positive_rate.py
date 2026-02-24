import math
from collections import Counter

import pytest
from stringalign.statistics import StringConfusionMatrix


def test_compute_true_positive_rate(sample_confusion_matrix: StringConfusionMatrix) -> None:
    tpr = sample_confusion_matrix.compute_true_positive_rate()
    assert tpr == pytest.approx({"a": 0.75, "b": 1.0, "c": 0.5, "d": float("nan"), "e": 0}, nan_ok=True)


def test_compute_true_positive_rate_aggregate(sample_confusion_matrix: StringConfusionMatrix) -> None:
    tpr = sample_confusion_matrix.compute_true_positive_rate(aggregate_over="ab")
    assert tpr == pytest.approx(5 / 6)


def test_compute_true_positive_rate_aliases(sample_confusion_matrix: StringConfusionMatrix) -> None:
    assert sample_confusion_matrix.compute_recall == sample_confusion_matrix.compute_true_positive_rate
    assert sample_confusion_matrix.compute_sensitivity == sample_confusion_matrix.compute_true_positive_rate


def test_no_tp_or_fn_gives_nan(sample_confusion_matrix: StringConfusionMatrix) -> None:
    tpr = sample_confusion_matrix.compute_true_positive_rate(aggregate_over="h")
    assert isinstance(tpr, float)
    assert math.isnan(tpr)
