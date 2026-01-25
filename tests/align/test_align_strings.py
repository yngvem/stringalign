import unicodedata
from typing import Any
from unittest.mock import Mock

import hypothesis.strategies as st
import numpy as np
import pytest
from hypothesis import given
from stringalign.align import (
    AlignmentOperation,
    Deleted,
    Inserted,
    InvalidRngError,
    Kept,
    Replaced,
    align_strings,
    compute_levenshtein_distance_from_alignment,
)
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


@pytest.mark.parametrize(
    "reference, predicted",
    [
        ("aa", "a"),
        ("aa", "b"),
        ("ab", "ba"),
    ],
)
def test_same_alignment_if_not_randomize(reference: str, predicted: str) -> None:
    """If aligment is not randomized the same strings should always get the same alignment"""
    first_alignment = align_strings(reference, predicted)

    assert all(align_strings(reference, predicted) == first_alignment for _ in range(10))


@pytest.mark.parametrize("random_state", [0, 1, 4, 101, 256])
@pytest.mark.parametrize(
    "reference, predicted",
    [
        ("aa", "a"),
        ("aa", "b"),
        ("ab", "ba"),
    ],
)
def test_same_alignment_if_same_random_state(reference: str, predicted: str, random_state: int) -> None:
    """If aligment is randomized with same random state the same strings should always get the same alignment"""
    first_alignment = align_strings(
        reference,
        predicted,
        randomize_alignment=True,
        random_state=random_state,
    )
    assert all(
        align_strings(
            reference,
            predicted,
            randomize_alignment=True,
            random_state=random_state,
        )
        == first_alignment
        for _ in range(10)
    )


@pytest.mark.parametrize(
    "reference, predicted",
    [
        ("aa", "a"),
        ("aa", "b"),
        ("ab", "ba"),
    ],
)
def test_not_same_alignment_if_different_random_state(reference: str, predicted: str) -> None:
    """If aligment is randomized with varying random state, the same strings shouldn't always get the same alignment"""
    first_alignment = align_strings(
        reference,
        predicted,
        randomize_alignment=True,
    )
    assert not all(
        align_strings(reference, predicted, randomize_alignment=True, random_state=i) == first_alignment
        for i in range(10)
    )


@pytest.mark.parametrize(
    "reference, predicted",
    [
        ("aa", "a"),
        ("aa", "b"),
        ("ab", "ba"),
    ],
)
def test_not_same_alignment_if_no_random_state(reference: str, predicted: str) -> None:
    """If aligment is randomized without setting random state, the same strings shouldn't always get equal alignment"""
    first_alignment = align_strings(
        reference,
        predicted,
        randomize_alignment=True,
    )
    assert not all(align_strings(reference, predicted, randomize_alignment=True) == first_alignment for _ in range(10))


@pytest.mark.parametrize(
    "reference, predicted",
    [
        ("aa", "a"),
        ("aa", "b"),
        ("ab", "ba"),
    ],
)
def test_same_levenshtein_if_different_random_state(reference: str, predicted: str) -> None:
    """The same strings should get alignments with the same Levenshtein distance even for randomized alignments"""
    first_alignment = align_strings(
        reference,
        predicted,
        randomize_alignment=True,
    )
    first_alignment_levenshtein = compute_levenshtein_distance_from_alignment(first_alignment[0])
    assert all(
        compute_levenshtein_distance_from_alignment(
            align_strings(reference, predicted, randomize_alignment=True, random_state=i)[0]
        )
        == first_alignment_levenshtein
        for i in range(10)
    )


@pytest.mark.parametrize(
    "reference, predicted",
    [
        ("aa", "a"),
        ("aa", "b"),
        ("ab", "ba"),
    ],
)
def test_random_state_is_used_when_its_an_rng(reference: str, predicted: str):
    """If the random state is provided as an RNG, then it is used"""
    mocked = Mock(spec=np.random.Generator)
    mocked.choice.return_value = Kept("mocked choice return value")

    align_strings(reference, predicted, randomize_alignment=True, random_state=mocked)
    mocked.choice.assert_called()


@pytest.mark.parametrize("invalid_random_state", ["not a valid rng", np.inf, []])
def test_invalid_random_state_raises(invalid_random_state: Any) -> None:
    """When an invalid rng is provided, IvalidRngError should be raised."""
    with pytest.raises(InvalidRngError):
        align_strings(
            "some string",
            "different string",
            randomize_alignment=True,
            random_state=invalid_random_state,
        )
