import hypothesis.strategies as st
import pytest
from hypothesis import given
from stringalign.align import Insert, Replace

from ...strategies import different_text_strings


@given(substring=st.text())
def test_insert_instantiation(substring: str) -> None:
    """It should be possible to instantiate the Insert class with a substring"""
    insert = Insert(substring)
    assert insert.substring == substring


@given(substring=st.text())
def test_insert_equality(substring: str) -> None:
    """Two Insert objects created with the same substring should be equal"""
    insert1 = Insert(substring)
    insert2 = Insert(substring)
    assert insert1 == insert2


@given(substring=st.text(min_size=1))
def test_insert_replaces_with_empty_string(substring: str) -> None:
    """A Insert object turns into a Replace object with an itself as the replace string"""
    insert = Insert(substring=substring)
    replaced_insert = insert.generalize()
    assert replaced_insert == Replace("", substring)


@given(substring=st.text())
def test_insert_simplifies_to_itself(substring: str) -> None:
    """Simplifying a Insert object returns the Insert object"""
    insert = Insert(substring=substring)
    assert insert == insert.simplify()


@given(strings=different_text_strings())
def test_insert_inequality(strings: tuple[str, str]) -> None:
    """Two Insert objects created with different substrings should not be equal"""
    substring1, substring2 = strings
    insert1 = Insert(substring1)
    insert2 = Insert(substring2)
    assert insert1 != insert2


@given(substring=st.text())
def test_insert_hash(substring: str) -> None:
    """Insert class should be hashable and two objects with the same string should have the same hash"""
    insert1 = Insert(substring)
    insert2 = Insert(substring)
    assert hash(insert1) == hash(insert2)


@given(strings=different_text_strings())
def test_insert_hash_inequality(strings: tuple[str, str]) -> None:
    """Two Insert objects created with different substrings should have different hash"""
    substring1, substring2 = strings
    insert1 = Insert(substring1)
    insert2 = Insert(substring2)
    assert hash(insert1) != hash(insert2)


@given(substring=st.text())
def test_insert_immutable(substring: str) -> None:
    """Insert class should be immutable"""
    insert = Insert(substring)
    with pytest.raises(AttributeError):
        insert.substring = "new substring"  # type: ignore
