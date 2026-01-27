from collections import Counter

import pytest
from stringalign.statistics import StringConfusionMatrix


def test_compute_f1_score(sample_confusion_matrix: StringConfusionMatrix) -> None:
    f1 = sample_confusion_matrix.compute_f1_score()
    supposed = {
        "a": 0.75,
        "b": 0.8,
        "c": 2 / 3,
        "d": 0.0,
        "e": 0.0,
    }
    assert f1 == pytest.approx(supposed)


def test_compute_f1_score_aggregate(sample_confusion_matrix: StringConfusionMatrix) -> None:
    f1 = sample_confusion_matrix.compute_f1_score(aggregate_over="ab")
    assert f1 == pytest.approx(10 / (10 + 2 + 1))
