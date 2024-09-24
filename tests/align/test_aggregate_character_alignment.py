from itertools import pairwise
from typing import List

import hypothesis.strategies as st
from hypothesis import given

from stringalign.align import (
    Delete,
    Insert,
    Replace,
    aggregate_character_alignment,
)


def alignment_strategy():
    return st.lists(
        st.one_of(
            st.none(),
            st.builds(Insert, st.text(min_size=1)),
            st.builds(Delete, st.text(min_size=1)),
            st.builds(Replace, st.text(min_size=1), st.text(min_size=1))
        )
    )


@given(alignment_strategy())
def test_aggregate_alignment_length(alignment):
    aggregated = list(aggregate_character_alignment(alignment))
    assert len(aggregated) <= len(alignment)


@given(alignment_strategy())
def test_aggregate_alignment_types(alignment):
    for op in aggregate_character_alignment(alignment):
        assert op is None or isinstance(op, (Insert, Delete, Replace))


@given(alignment_strategy())
def test_aggregate_alignment_consecutive_not_nones(alignment):
    for op1, op2 in pairwise(aggregate_character_alignment(alignment)):
        if op1 is not None:
            assert op2 is None, (op1, op2)
        
        if op2 is not None:
            assert op1 is None, (op1, op2)


def test_aggregate_alignment_with_example():
    alignment = [Insert('a'), Insert('b'), None, Replace('a', 'b'), Insert('a'), Replace('b', 'c'), Delete('a'), None, Replace('a', 'e')]
    assert list(aggregate_character_alignment(alignment)) == [Insert('ab'), None, Replace('aba', 'bac'), None, Replace('a', 'e')] 
