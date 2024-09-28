import hypothesis.strategies as st
import pytest
from hypothesis import given
from stringalign.align import Delete, Insert, Replace

from ...strategies import different_text_strings


@given(st.text(), st.text())
def test_replace_instantiation(substring: str, replacement: str):
    """It should be possible to instantiate the Replace class with a substring and a replacement"""
    replace = Replace(substring, replacement)
    assert replace.substring == substring
    assert replace.replacement == replacement


@given(st.text(), st.text())
def test_replace_equality(substring: str, replacement: str):
    """Two Replace objects created with the same substrings and replacements should be equal"""
    replace1 = Replace(substring=substring, replacement=replacement)
    replace2 = Replace(substring=substring, replacement=replacement)
    assert replace1 == replace2


@given(st.text(), st.text())
def test_replace_replaces_with_itself(substring: str, replacement: str):
    """as_replace returns itself for a Replace object"""
    replace = Replace(substring=substring, replacement=replacement)
    assert replace == replace.as_replace()


@given(st.text(min_size=1))
def test_replace_with_emtpy_string_simplifies_to_delete(substring: str):
    """simplifying a Replace object with an empty string as replacement returns a Delete object"""
    replace = Replace(substring=substring, replacement="")
    simplified_replace = replace.simplify()
    assert simplified_replace == Delete(substring)


@given(st.text(min_size=1))
def test_replacing_empty_string_simplifies_to_insert(replacement: str):
    """simplifying a Replace object with an empty string as substring returns an Insert object"""
    replace = Replace(substring="", replacement=replacement)
    simplified_replace = replace.simplify()
    assert simplified_replace == Insert(replacement)


@given(different_text_strings(), st.text())
def test_replace_inequality_substring(substrings, replacement):
    """Two Replace objects created with different substrings should not be equal"""
    substring1, substring2 = substrings
    replace1 = Replace(substring=substring1, replacement=replacement)
    replace2 = Replace(substring=substring2, replacement=replacement)
    assert replace1 != replace2


@given(st.text(), different_text_strings())
def test_replace_inequality_replacement(substring, replacements):
    """Two Replace objects created with  different substrings should not be equal"""
    replacement1, replacement2 = replacements
    replace1 = Replace(substring=substring, replacement=replacement1)
    replace2 = Replace(substring=substring, replacement=replacement2)
    assert replace1 != replace2


@given(st.text(), st.text())
def test_replace_hash(substring: str, replacement: str):
    """Replace class should be hashable and two objects with the same string should have the same hash"""
    replace1 = Replace(substring=substring, replacement=replacement)
    replace2 = Replace(substring=substring, replacement=replacement)
    assert hash(replace1) == hash(replace2)


@given(different_text_strings(), st.text())
def test_replace_hash_inequality_substring(substrings, replacement):
    """Two Replace objects created with  different substrings should not be equal"""
    substring1, substring2 = substrings
    replace1 = Replace(substring=substring1, replacement=replacement)
    replace2 = Replace(substring=substring2, replacement=replacement)
    assert hash(replace1) != hash(replace2)


@given(st.text(), different_text_strings())
def test_replace_hash_inequality_replacement(substring, replacements):
    """Two Replace objects created with  different substrings should not be equal"""
    replacement1, replacement2 = replacements
    replace1 = Replace(substring=substring, replacement=replacement1)
    replace2 = Replace(substring=substring, replacement=replacement2)
    assert hash(replace1) != hash(replace2)


@given(st.text(), st.text())
def test_replace_immutable(substring: str, replacement: str):
    """Replace class should be immutable"""
    replace = Replace(substring, replacement)
    with pytest.raises(AttributeError):
        replace.substring = "new substring"  # type: ignore
    with pytest.raises(AttributeError):
        replace.replacement = "new replacement"  # type: ignore
