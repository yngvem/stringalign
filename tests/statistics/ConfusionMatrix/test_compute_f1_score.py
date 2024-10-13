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
