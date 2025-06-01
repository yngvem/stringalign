from itertools import pairwise

import hypothesis.strategies as st
from hypothesis import given
from stringalign.align import (
    AlignmentOperation,
    Deleted,
    Inserted,
    Kept,
    Replaced,
    aggregate_alignment,
)


def alignment_strategy():
    return st.lists(
        st.one_of(
            st.builds(Deleted, st.text(min_size=1)),
            st.builds(Inserted, st.text(min_size=1)),
            st.builds(Kept, st.text(min_size=1)),
            st.builds(Replaced, st.text(min_size=1), st.text(min_size=1)),
        )
    )


@given(alignment=alignment_strategy())
def test_aggregate_alignment_length(alignment):
    aggregated = list(aggregate_alignment(alignment))
    assert len(aggregated) <= len(alignment)


@given(alignment=alignment_strategy())
def test_aggregate_alignment_types(alignment):
    for op in aggregate_alignment(alignment):
        assert isinstance(op, AlignmentOperation)


@given(alignment=alignment_strategy())
def test_aggregate_alignment_consecutive_not_nones(alignment):
    for op1, op2 in pairwise(aggregate_alignment(alignment)):
        if not isinstance(op1, Kept):
            assert isinstance(op2, Kept), (op1, op2)

        if not isinstance(op2, Kept):
            assert isinstance(op1, Kept), (op1, op2)


def test_aggregate_alignment_with_example():
    alignment = [
        Deleted("a"),
        Deleted("b"),
        Kept("a"),
        Replaced("a", "b"),
        Deleted("a"),
        Replaced("b", "c"),
        Inserted("a"),
        Kept("b"),
        Kept("c"),
        Replaced("a", "e"),
    ]
    assert list(aggregate_alignment(alignment)) == [
        Deleted("ab"),
        Kept("a"),
        Replaced("aba", "bac"),
        Kept("bc"),
        Replaced("a", "e"),
    ]
