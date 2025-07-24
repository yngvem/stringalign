import hypothesis.strategies as st
import pytest
import stringalign
from hypothesis import given
from stringalign.align import Deleted, Inserted, Kept, Replaced

from ...strategies import different_text_strings


@given(predicted=st.text(), reference=st.text())
def test_replace_instantiation(reference: str, predicted: str) -> None:
    """It should be possible to instantiate the Replaced class with a predicted and a reference text"""
    replaced = Replaced(reference=reference, predicted=predicted)
    assert replaced.predicted == predicted
    assert replaced.reference == reference


@given(predicted=st.text(), reference=st.text())
def test_replace_equality(reference: str, predicted: str) -> None:
    """Two Replaced objects created with the same predictions and references should be equal"""
    replace1 = Replaced(reference=reference, predicted=predicted)
    replace2 = Replaced(reference=reference, predicted=predicted)
    assert replace1 == replace2


@given(predicted=st.text(), reference=st.text())
def test_replace_replaces_with_itself(reference: str, predicted: str) -> None:
    """Generalizing a Replaced object returns itself"""
    replaced = Replaced(reference=reference, predicted=predicted)
    assert replaced == replaced.generalize()


@given(predicted=st.text(min_size=1))
def test_replace_with_emtpy_string_simplifies_to_delete(predicted: str) -> None:
    """Simplifying a Replaced object with an empty string as reference returns an Inserted object"""
    replaced = Replaced(reference="", predicted=predicted)
    simplified_replaced = replaced.simplify()
    assert simplified_replaced == Inserted(predicted)


@given(reference=st.text(min_size=1))
def test_replacing_empty_string_simplifies_to_insert(reference: str) -> None:
    """Simplifying a Replaced object with an empty string as predicted returns a deleted object"""
    replaced = Replaced(reference=reference, predicted="")
    simplified_replaced = replaced.simplify()
    assert simplified_replaced == Deleted(reference)


@given(predicteds=different_text_strings(), reference=st.text())
def test_replace_inequality_predicted(predicteds: tuple[str, str], reference: str) -> None:
    """Two Replaced objects created with different predictions should not be equal"""
    predicted1, predicted2 = predicteds
    replace1 = Replaced(reference=reference, predicted=predicted1)
    replace2 = Replaced(reference=reference, predicted=predicted2)
    assert replace1 != replace2


@given(predicted=st.text(), references=different_text_strings())
def test_replace_inequality_reference(predicted: str, references: tuple[str, str]) -> None:
    """Two Replaced objects created with  different references should not be equal"""
    reference1, reference2 = references
    replace1 = Replaced(reference=reference1, predicted=predicted)
    replace2 = Replaced(reference=reference2, predicted=predicted)
    assert replace1 != replace2


@given(predicted=st.text(), reference=st.text())
def test_replace_hash(predicted: str, reference: str):
    """Replaced class should be hashable and two objects with the same string should have the same hash"""
    replace1 = Replaced(reference=reference, predicted=predicted)
    replace2 = Replaced(reference=reference, predicted=predicted)
    assert hash(replace1) == hash(replace2)


@given(predicteds=different_text_strings(), reference=st.text())
def test_replace_hash_inequality_predicted(predicteds: tuple[str, str], reference: str) -> None:
    """Two Replaced objects created with different predictions should have different hashes"""
    predicted1, predicted2 = predicteds
    replace1 = Replaced(reference=reference, predicted=predicted1)
    replace2 = Replaced(reference=reference, predicted=predicted2)
    assert hash(replace1) != hash(replace2)


@given(predicted=st.text(), references=different_text_strings())
def test_replace_hash_inequality_reference(predicted: str, references: tuple[str, str]) -> None:
    """Two Replaced objects created with different references should have different hashes"""
    reference1, reference2 = references
    replace1 = Replaced(reference=reference1, predicted=predicted)
    replace2 = Replaced(reference=reference2, predicted=predicted)
    assert hash(replace1) != hash(replace2)


@given(predicted=st.text(), reference=st.text())
def test_replace_immutable(predicted: str, reference: str):
    """Replaced class should be immutable"""
    replaced = Replaced(reference=reference, predicted=predicted)
    with pytest.raises(AttributeError):
        replaced.predicted = "new predicted"  # type: ignore
    with pytest.raises(AttributeError):
        replaced.reference = "new reference"  # type: ignore


@given(predicted=st.text(), reference=st.text())
@pytest.mark.parametrize("OtherType", [Inserted, Kept, Deleted, str])
def test_replace_cannot_merge_with_different_type(predicted: str, reference: str, OtherType: type) -> None:
    """Merging Replaced instance with not Replaced instance raises TypeError"""
    replaced = Replaced(reference=reference, predicted=predicted)
    with pytest.raises(TypeError):
        replaced.merge(OtherType("NOT A REPLACE INSTANCE"), tokenizer=stringalign.tokenize.GraphemeClusterTokenizer())
