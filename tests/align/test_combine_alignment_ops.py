from itertools import pairwise

import hypothesis.strategies as st
from hypothesis import given
from stringalign.align import (
    AlignmentOperation,
    Deleted,
    Inserted,
    Kept,
    Replaced,
    combine_alignment_ops,
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
def test_length(alignment):
    combined = list(combine_alignment_ops(alignment))
    assert len(combined) <= len(alignment)


@given(alignment=alignment_strategy())
def test_types(alignment):
    for op in combine_alignment_ops(alignment):
        assert isinstance(op, AlignmentOperation)


@given(alignment=alignment_strategy())
def test_consecutive_not_nones(alignment):
    for op1, op2 in pairwise(combine_alignment_ops(alignment)):
        if not isinstance(op1, Kept):
            assert isinstance(op2, Kept), (op1, op2)

        if not isinstance(op2, Kept):
            assert isinstance(op1, Kept), (op1, op2)


def test_with_example():
    alignment = [
        Deleted("a"),
        Deleted("b"),
        Kept("a"),
        Replaced(reference="b", predicted="a"),
        Deleted("a"),
        Replaced(reference="c", predicted="b"),
        Inserted("a"),
        Kept("b"),
        Kept("c"),
        Replaced(reference="e", predicted="a"),
    ]
    assert list(combine_alignment_ops(alignment)) == [
        Deleted("ab"),
        Kept("a"),
        Replaced(reference="bac", predicted="aba"),
        Kept("bc"),
        Replaced(reference="e", predicted="a"),
    ]
