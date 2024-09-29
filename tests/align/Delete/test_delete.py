import hypothesis.strategies as st
import pytest
from hypothesis import given
from stringalign.align import Delete, Replace

from ...strategies import different_text_strings


@given(substring=st.text())
def test_delete_instantiation(substring: str) -> None:
    """It should be possible to instantiate the Delete class with a substring"""
    delete = Delete(substring)
    assert delete.substring == substring


@given(substring=st.text())
def test_delete_equality(substring: str) -> None:
    """Two Delete objects created with the same substring should be equal"""
    delete1 = Delete(substring)
    delete2 = Delete(substring)
    assert delete1 == delete2


@given(substring=st.text())
def test_delete_replaces_with_empty_string(substring: str) -> None:
    """A Delete object turns into a Replace object with an empty string"""
    delete = Delete(substring=substring)
    replaced_delete = delete.generalize()
    assert replaced_delete == Replace(substring, "")


@given(substring=st.text())
def test_delete_simplifies_to_itself(substring: str) -> None:
    """Simplifying a Delete object returns the Delete object"""
    delete = Delete(substring=substring)
    assert delete == delete.simplify()


@given(strings=different_text_strings())
def test_delete_inequality(strings: tuple[str, str]) -> None:
    """Two Delete objects created with different substrings should not be equal"""
    substring1, substring2 = strings
    delete1 = Delete(substring1)
    delete2 = Delete(substring2)
    assert delete1 != delete2


@given(substring=st.text())
def test_delete_hash(substring: str) -> None:
    """Delete class should be hashable and two objects with the same string should have the same hash"""
    delete1 = Delete(substring)
    delete2 = Delete(substring)
    assert hash(delete1) == hash(delete2)


@given(strings=different_text_strings())
def test_delete_hash_inequality(strings: tuple[str, str]) -> None:
    """Two Delete objects created with different substrings should have different hash"""
    substring1, substring2 = strings
    delete1 = Delete(substring1)
    delete2 = Delete(substring2)
    assert hash(delete1) != hash(delete2)


@given(substring=st.text())
def test_delete_immutable(substring: str) -> None:
    """Delete class should be immutable"""
    delete = Delete(substring)
    with pytest.raises(AttributeError):
        delete.substring = "new substring"  # type: ignore
