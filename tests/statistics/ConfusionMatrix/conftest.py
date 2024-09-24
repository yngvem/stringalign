# conftest.py
from collections import Counter

import pytest

from stringalign.align import AlignmentOperation, Replace, Insert, Delete
from stringalign.statistics import StringConfusionMatrix


@pytest.fixture
def sample_confusion_matrix():
    return StringConfusionMatrix(
        true_positives=Counter({'a': 2, 'b': 1, 'c': 1}),
        false_positives=Counter({'d': 1, 'e': 1}),
        false_negatives=Counter({'f': 1, 'g': 1})
    )


@pytest.fixture
def sample_alignment() -> tuple[str, str, list[AlignmentOperation | None]]:
    return [
        "abcbag",
        "acdegi",
        None,
        Insert("b"),
        None,
        Replace("d", "b"),
        Replace("e", "a"),
        None,
        Delete("i")
    ]