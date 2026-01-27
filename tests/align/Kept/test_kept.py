import hypothesis.strategies as st
import pytest
import stringalign
from hypothesis import given
from stringalign.align import Deleted, Inserted, Kept, Replaced

from ...strategies import different_text_strings


@given(substring=st.text())
def test_kept_instantiation(substring: str) -> None:
    """It should be possible to instantiate the Kept class with a substring"""
    kept = Kept(substring)
    assert kept.substring == substring


@given(substring=st.text())
def test_kept_equality(substring: str) -> None:
    """Two Kept objects created with the same substring should be equal"""
    kept1 = Kept(substring)
    kept2 = Kept(substring)
    assert kept1 == kept2


@given(substring=st.text())
def test_simplifying_returns_kept(substring: str) -> None:
    """Simplifying a Kept object returns the Kept object"""
    kept = Kept(substring=substring)
    assert kept == kept.simplify()


@given(strings=different_text_strings())
def test_kept_inequality(strings: tuple[str, str]) -> None:
    """Two Kept objects created with different substrings should not be equal"""
    substring1, substring2 = strings
    kept1 = Kept(substring1)
    kept2 = Kept(substring2)
    assert kept1 != kept2


@given(substring=st.text())
def test_kept_hash(substring) -> None:
    """Kept class should be hashable and two objects with the same string should have the same hash"""
    kept1 = Kept(substring)
    kept2 = Kept(substring)
    assert hash(kept1) == hash(kept2)


@given(strings=different_text_strings())
def test_kept_hash_inequality(strings) -> None:
    """Two Kept objects created with different substrings should have different hash"""
    substring1, substring2 = strings
    kept1 = Kept(substring1)
    kept2 = Kept(substring2)
    assert hash(kept1) != hash(kept2)


@given(substring=st.text())
def test_kept_immutable(substring) -> None:
    """Kept class should be immutable"""
    kept = Kept(substring)
    with pytest.raises(AttributeError):
        kept.substring = "new substring"  # type: ignore


@given(substring1=st.text(), substring2=st.text())
def test_kept_merge(substring1, substring2) -> None:
    """Merging to Kept instances gives a Kept instance with the substrings concatenated"""
    kept1 = Kept(substring1)
    kept2 = Kept(substring2)

    merged_kept = kept1.merge(kept2, tokenizer=stringalign.tokenize.GraphemeClusterTokenizer())
    assert merged_kept == Kept(substring1 + substring2)


@given(substring=st.text())
@pytest.mark.parametrize("OtherType", [Deleted, Replaced, Inserted, str])
def test_kept_cannot_merge_with_different_type(substring: str, OtherType: type) -> None:
    """Merging Kept instance with not Kept instance raises TypeError"""
    kept = Kept(substring)
    with pytest.raises(TypeError):
        kept.merge(OtherType("NOT A KEPT INSTANCE"), tokenizer=stringalign.tokenize.GraphemeClusterTokenizer())
