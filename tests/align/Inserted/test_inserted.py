import hypothesis.strategies as st
import pytest
from hypothesis import given
from stringalign.align import Inserted, Replaced

from ...strategies import different_text_strings


@given(substring=st.text())
def test_inserted_instantiation(substring: str) -> None:
    """It should be possible to instantiate the Inserted class with a substring"""
    inserted = Inserted(substring)
    assert inserted.substring == substring


@given(substring=st.text())
def test_inserted_equality(substring: str) -> None:
    """Two Inserted objects created with the same substring should be equal"""
    inserted1 = Inserted(substring)
    inserted2 = Inserted(substring)
    assert inserted1 == inserted2


@given(substring=st.text())
def test_inserted_replaces_with_empty_string(substring: str) -> None:
    """An Inserted object turns into a Replaced object with an empty string"""
    inserted = Inserted(substring=substring)
    replaced_inserted = inserted.generalize()
    assert replaced_inserted == Replaced(substring, "")


@given(substring=st.text())
def test_inserted_simplifies_to_itself(substring: str) -> None:
    """Simplifying an Inserted object returns the Inserted object"""
    inserted = Inserted(substring=substring)
    assert inserted == inserted.simplify()


@given(strings=different_text_strings())
def test_inserted_inequality(strings: tuple[str, str]) -> None:
    """Two Inserted objects created with different substrings should not be equal"""
    substring1, substring2 = strings
    inserted1 = Inserted(substring1)
    inserted2 = Inserted(substring2)
    assert inserted1 != inserted2


@given(substring=st.text())
def test_inserted_hash(substring: str) -> None:
    """Inserted class should be hashable and two objects with the same string should have the same hash"""
    inserted1 = Inserted(substring)
    inserted2 = Inserted(substring)
    assert hash(inserted1) == hash(inserted2)


@given(strings=different_text_strings())
def test_inserted_hash_inequality(strings: tuple[str, str]) -> None:
    """Two Inserted objects created with different substrings should have different hash"""
    substring1, substring2 = strings
    inserted1 = Inserted(substring1)
    inserted2 = Inserted(substring2)
    assert hash(inserted1) != hash(inserted2)


@given(substring=st.text())
def test_inserted_immutable(substring: str) -> None:
    """Inserted class should be immutable"""
    inserted = Inserted(substring)
    with pytest.raises(AttributeError):
        inserted.substring = "new substring"  # type: ignore
