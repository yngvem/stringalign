import pytest
from hypothesis import given
from hypothesis import strategies as st
from stringalign.align import Kept
from stringalign.evaluation import join_windows


@given(center_string=st.text())
def test_join_windows_no_operations(center_string: str) -> None:
    assert join_windows(center_string, None, None) == center_string


@given(center_string=st.text(), previous_operation_string=st.text())
def test_join_windows_with_previous_operation(center_string: str, previous_operation_string: str) -> None:
    prev_op = Kept(previous_operation_string)
    assert join_windows(center_string, prev_op, None) == previous_operation_string + center_string


@given(center_string=st.text(), next_operation_string=st.text())
def test_join_windows_with_next_operation(center_string: str, next_operation_string: str) -> None:
    next_op = Kept(next_operation_string)
    assert join_windows(center_string, None, next_op) == center_string + next_operation_string


@given(center_string=st.text(), previous_operation_string=st.text(), next_operation_string=st.text())
def test_join_windows_with_both_operations(
    center_string: str, previous_operation_string: str, next_operation_string: str
) -> None:
    prev_op = Kept(previous_operation_string)
    next_op = Kept(next_operation_string)
    expected = previous_operation_string + center_string + next_operation_string
    assert join_windows(center_string, prev_op, next_op) == expected


@given(center=st.text(), prev=st.text(), next=st.text())
def test_join_windows_hypothesis(center: str, prev: str, next: str) -> None:
    if prev:
        prev_op = Kept(prev)
    else:
        prev_op = None

    if next:
        next_op = Kept(next)
    else:
        next_op = None

    expected = prev + center + next
    assert join_windows(center, prev_op, next_op) == expected
