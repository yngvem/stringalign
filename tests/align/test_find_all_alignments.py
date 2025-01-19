from datetime import timedelta

import hypothesis.strategies as st
import pytest
from hypothesis import given, settings
from stringalign.align import (
    AlignmentOperation,
    Delete,
    Insert,
    Keep,
    Replace,
    align_strings,
    compute_levenshtein_distance_from_alignment,
    find_all_alignments,
)


@pytest.mark.parametrize(
    "reference, predicted, alignments",
    [
        (
            "ab",
            "ba",
            (
                (Replace("b", "a"), Replace("a", "b")),
                (Insert("a"), Keep("b"), Delete("a")),
                (Delete("b"), Keep("a"), Insert("b")),
            ),
        )
    ],
)
def test_find_all_alignments_with_examples(
    reference: str, predicted: str, alignments: tuple[tuple[AlignmentOperation, ...], ...]
) -> None:
    """All expected aligmments should be found with no duplicates."""
    all_aligments = tuple(find_all_alignments(reference, predicted))

    assert len(all_aligments) == len(alignments)
    assert set(all_aligments) == set(alignments)


# These hypothesis tests have a very small max_size since the number of possible alignments
# grows exponentially, so some pathological examples that Hypothesis finds will take too long
# to run.
@settings(deadline=timedelta(milliseconds=500))
@given(reference=st.text(max_size=10), predicted=st.text(max_size=10))
def test_no_duplicates(reference: str, predicted: str) -> None:
    all_alignments = tuple(find_all_alignments(reference, predicted))
    assert len(set(all_alignments)) == len(all_alignments)


@settings(deadline=timedelta(milliseconds=500))
@given(reference=st.text(max_size=10), predicted=st.text(max_size=10))
def test_all_equally_good(reference: str, predicted: str) -> None:
    all_alignments = find_all_alignments(reference, predicted)
    costs = {compute_levenshtein_distance_from_alignment(alignment) for alignment in all_alignments}
    assert len(costs) == 1


@settings(deadline=timedelta(milliseconds=500))
@given(reference=st.text(max_size=10), predicted=st.text(max_size=10))
def test_best_is_among_all(reference: str, predicted: str) -> None:
    all_alignments = find_all_alignments(reference, predicted)
    best_alignment = align_strings(reference, predicted)[0]
    assert best_alignment in set(all_alignments)
