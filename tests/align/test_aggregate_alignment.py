from itertools import pairwise
from typing import List

import hypothesis.strategies as st
from hypothesis import given
from stringalign.align import (
    AlignmentOperation,
    Delete,
    Insert,
    Keep,
    Replace,
    aggregate_alignment,
)


def alignment_strategy():
    return st.lists(
        st.one_of(
            st.builds(Insert, st.text(min_size=1)),
            st.builds(Delete, st.text(min_size=1)),
            st.builds(Keep, st.text(min_size=1)),
            st.builds(Replace, st.text(min_size=1), st.text(min_size=1)),
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
        if not isinstance(op1, Keep):
            assert isinstance(op2, Keep), (op1, op2)

        if not isinstance(op2, Keep):
            assert isinstance(op1, Keep), (op1, op2)


def test_aggregate_alignment_with_example():
    alignment = [
        Insert("a"),
        Insert("b"),
        Keep("a"),
        Replace("a", "b"),
        Insert("a"),
        Replace("b", "c"),
        Delete("a"),
        Keep("b"),
        Keep("c"),
        Replace("a", "e"),
    ]
    assert list(aggregate_alignment(alignment)) == [
        Insert("ab"),
        Keep("a"),
        Replace("aba", "bac"),
        Keep("bc"),
        Replace("a", "e"),
    ]
