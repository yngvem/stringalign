import hypothesis.strategies as st
import pytest
from hypothesis import given
from stringalign.align import Deleted, Replaced

from ...strategies import different_text_strings


@given(substring=st.text())
def test_deleted_instantiation(substring: str) -> None:
    """It should be possible to instantiate the Deleted class with a substring"""
    deleted = Deleted(substring)
    assert deleted.substring == substring


@given(substring=st.text())
def test_deleted_equality(substring: str) -> None:
    """Two Deleted objects created with the same substring should be equal"""
    deleted1 = Deleted(substring)
    deleted2 = Deleted(substring)
    assert deleted1 == deleted2


@given(substring=st.text(min_size=1))
def test_deleted_replaces_with_empty_string(substring: str) -> None:
    """A Deleted object turns into a Replaced object with an itself as the replace string"""
    deleted = Deleted(substring=substring)
    replace_deleted = deleted.generalize()
    assert replace_deleted == Replaced("", substring)


@given(substring=st.text())
def test_deleted_simplifies_to_itself(substring: str) -> None:
    """Simplifying a Deleted object returns the Deleted object"""
    deleted = Deleted(substring=substring)
    assert deleted == deleted.simplify()


@given(strings=different_text_strings())
def test_deleted_inequality(strings: tuple[str, str]) -> None:
    """Two Deleted objects created with different substrings should not be equal"""
    substring1, substring2 = strings
    deleted1 = Deleted(substring1)
    deleted2 = Deleted(substring2)
    assert deleted1 != deleted2


@given(substring=st.text())
def test_deleted_hash(substring: str) -> None:
    """Deleted class should be hashable and two objects with the same string should have the same hash"""
    deleted1 = Deleted(substring)
    deleted2 = Deleted(substring)
    assert hash(deleted1) == hash(deleted2)


@given(strings=different_text_strings())
def test_deleted_hash_inequality(strings: tuple[str, str]) -> None:
    """Two Deleted objects created with different substrings should have different hash"""
    substring1, substring2 = strings
    deleted1 = Deleted(substring1)
    deleted2 = Deleted(substring2)
    assert hash(deleted1) != hash(deleted2)


@given(substring=st.text())
def test_deleted_immutable(substring: str) -> None:
    """Deleted class should be immutable"""
    deleted = Deleted(substring)
    with pytest.raises(AttributeError):
        deleted.substring = "new substring"  # type: ignore
