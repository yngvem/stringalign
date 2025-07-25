import hypothesis.strategies as st
import pytest
import stringalign
from hypothesis import given
from stringalign.align import Deleted, Inserted, Kept, Replaced

from ...strategies import different_text_strings


@given(substring=st.text())
def test_keep_instantiation(substring: str) -> None:
    """It should be possible to instantiate the Keep class with a substring"""
    keep = Kept(substring)
    assert keep.substring == substring


@given(substring=st.text())
def test_keep_equality(substring: str) -> None:
    """Two Keep objects created with the same substring should be equal"""
    keep1 = Kept(substring)
    keep2 = Kept(substring)
    assert keep1 == keep2


@given(substring=st.text())
def keep(substring: str) -> None:
    """Simplifying a Keep object returns the Keep object"""
    keep = Kept(substring=substring)
    assert keep == keep.simplify()


@given(strings=different_text_strings())
def test_keep_inequality(strings: tuple[str, str]) -> None:
    """Two Keep objects created with different substrings should not be equal"""
    substring1, substring2 = strings
    keep1 = Kept(substring1)
    keep2 = Kept(substring2)
    assert keep1 != keep2


@given(substring=st.text())
def test_keep_hash(substring) -> None:
    """Keep class should be hashable and two objects with the same string should have the same hash"""
    keep1 = Kept(substring)
    keep2 = Kept(substring)
    assert hash(keep1) == hash(keep2)


@given(strings=different_text_strings())
def test_keep_hash_inequality(strings) -> None:
    """Two Keep objects created with different substrings should have different hash"""
    substring1, substring2 = strings
    keep1 = Kept(substring1)
    keep2 = Kept(substring2)
    assert hash(keep1) != hash(keep2)


@given(substring=st.text())
def test_keep_immutable(substring) -> None:
    """Keep class should be immutable"""
    keep = Kept(substring)
    with pytest.raises(AttributeError):
        keep.substring = "new substring"  # type: ignore


@given(substring1=st.text(), substring2=st.text())
def test_keep_merge(substring1, substring2) -> None:
    """Merging to Keep instances gives a Keep instance with the substrings concatenated"""
    keep1 = Kept(substring1)
    keep2 = Kept(substring2)

    merged_keep = keep1.merge(keep2, tokenizer=stringalign.tokenize.GraphemeClusterTokenizer())
    assert merged_keep == Kept(substring1 + substring2)


@given(substring=st.text())
@pytest.mark.parametrize("OtherType", [Deleted, Replaced, Inserted, str])
def test_keep_cannot_merge_with_different_type(substring: str, OtherType: type) -> None:
    """Merging Keep instance with not Keep instance raises TypeError"""
    keep = Kept(substring)
    with pytest.raises(TypeError):
        keep.merge(OtherType("NOT A KEPT INSTANCE"), tokenizer=stringalign.tokenize.GraphemeClusterTokenizer())
