import unicodedata

import hypothesis.strategies as st
import pytest
from hypothesis import given
from stringalign.align import AlignmentOperation, Deleted, Inserted, Kept, Replaced, align_strings
from stringalign.normalize import StringNormalizer
from stringalign.tokenize import GraphemeClusterTokenizer


@given(reference=st.text(), predicted=st.text())
def test_align_strings_length(reference: str, predicted: str) -> None:
    alignment = align_strings(reference, predicted)[0]
    tokenizer = GraphemeClusterTokenizer()
    ref_clusters, pred_clusters = tokenizer(reference), tokenizer(predicted)
    assert len(alignment) >= max(len(ref_clusters), len(pred_clusters))


@given(reference=st.text(), predicted=st.text())
def test_align_strings_types(reference: str, predicted: str) -> None:
    alignment = align_strings(reference, predicted)[0]
    for op in alignment:
        assert isinstance(op, AlignmentOperation)


@given(reference=st.text(), predicted=st.text())
def test_align_strings_reconstruct(reference: str, predicted: str) -> None:
    tokenizer = GraphemeClusterTokenizer(
        pre_clustering_normalizer=StringNormalizer(normalization=None),
        post_clustering_normalizer=StringNormalizer(normalization=None),
    )
    alignment = align_strings(reference, predicted, tokenizer=tokenizer)[0]

    rec_predicted = ""
    rec_reference = ""
    pred_iter = iter(tokenizer(predicted))
    ref_iter = iter(tokenizer(reference))
    for op in alignment:
        if isinstance(op, Kept):
            rec_predicted += next(ref_iter)
            rec_reference += next(pred_iter)

        elif isinstance(op, Replaced):
            ref_char = next(ref_iter)
            pred_char = next(pred_iter)

            assert ref_char == op.reference
            assert pred_char == op.predicted

            rec_predicted += op.predicted
            rec_reference += op.reference

        elif isinstance(op, Deleted):
            char = next(ref_iter)
            assert char == op.substring
            rec_reference += char

        elif isinstance(op, Inserted):
            char = next(pred_iter)
            assert char == op.substring
            rec_predicted += char

    assert rec_reference == reference
    assert rec_predicted == predicted


@given(text=st.text())
def test_align_strings_identical(text: str) -> None:
    alignment = align_strings(text, text)[0]
    assert all(isinstance(op, Kept) for op in alignment)
    assert len(alignment) == len(GraphemeClusterTokenizer()(text))


def test_normalise_unicode() -> None:
    a_with_ring = "Å"
    letter_å = "Å"

    assert a_with_ring != letter_å
    assert align_strings(a_with_ring, letter_å) == ((Kept(letter_å),), True)


def test_align_combining_grapheme() -> None:
    """Test that graphemes that consist of multiple code-points are handled as a single character.

    See e.g. https://tonsky.me/blog/unicode/ and https://grapheme.readthedocs.io/en/latest/grapheme.html
    """
    assert align_strings("ą́", "a") == ((Replaced(reference=unicodedata.normalize("NFC", "ą́"), predicted="a"),), True)


def test_align_emojis() -> None:
    """Test that emojis that consist of multiple code-points are handled as a single character.

    See e.g. https://tonsky.me/blog/unicode/ and https://grapheme.readthedocs.io/en/latest/grapheme.html
    """
    rainbow_flag = "🏳️‍🌈"
    assert rainbow_flag == "".join(["🏳", "️", "‍", "🌈"])

    rainbow = "🌈"

    alignment = align_strings(rainbow_flag, rainbow)
    assert alignment == ((Replaced(reference="🏳️‍🌈", predicted="🌈"),), True)


@pytest.mark.parametrize(
    "reference, predicted, unique_alignment",
    [
        ("a", "a", True),
        ("a", "b", True),
        ("aa", "ab", True),
        ("aa", "a", False),
        ("aa", "b", False),
        ("ab", "ba", False),
    ],
)
def test_detect_multiple_alignments(reference, predicted, unique_alignment) -> None:
    assert align_strings(reference, predicted)[1] == unique_alignment
