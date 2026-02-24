import math
from collections import Counter

import pytest
from stringalign.statistics import StringConfusionMatrix


def test_compute_positive_predictive_value(sample_confusion_matrix: StringConfusionMatrix) -> None:
    ppv = sample_confusion_matrix.compute_positive_predictive_value()
    assert ppv == pytest.approx({"a": 0.75, "b": 2 / 3, "c": 1.0, "d": 0.0, "e": float("nan")}, nan_ok=True)


def test_compute_positive_predictive_value_aggregate(sample_confusion_matrix: StringConfusionMatrix) -> None:
    ppv = sample_confusion_matrix.compute_positive_predictive_value(aggregate_over="ab")
    assert ppv == pytest.approx(5 / 7)


def test_no_tp_or_fn_gives_nan(sample_confusion_matrix: StringConfusionMatrix) -> None:
    ppv = sample_confusion_matrix.compute_positive_predictive_value(aggregate_over="h")
    assert isinstance(ppv, float)
    assert math.isnan(ppv)
