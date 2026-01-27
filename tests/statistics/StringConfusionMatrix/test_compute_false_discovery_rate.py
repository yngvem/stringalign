import math
from collections import Counter

import pytest
from stringalign.statistics import StringConfusionMatrix


def test_compute_false_discovery_rate_simple_example(sample_confusion_matrix: StringConfusionMatrix) -> None:
    fdr = sample_confusion_matrix.compute_false_discovery_rate()
    assert fdr == pytest.approx({"a": 0.25, "b": 1 / 3, "c": 0, "d": 1, "e": float("nan")}, nan_ok=True)


def test_compute_false_discovery_rate_value_aggregate(sample_confusion_matrix: StringConfusionMatrix) -> None:
    fdr = sample_confusion_matrix.compute_false_discovery_rate(aggregate_over="ab")
    assert fdr == pytest.approx(2 / 7)


def test_no_tp_or_fn_gives_nan(sample_confusion_matrix: StringConfusionMatrix) -> None:
    fdr = sample_confusion_matrix.compute_false_discovery_rate(aggregate_over="h")
    assert isinstance(fdr, float)
    assert math.isnan(fdr)
