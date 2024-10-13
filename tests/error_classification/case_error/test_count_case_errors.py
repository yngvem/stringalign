import random

import hypothesis.strategies as st
from hypothesis import given
from stringalign.error_classification.case_error import count_case_errors

from tests.utils import caseswap_n_randomly, interleave_strings, remove_n_characters


@given(text=st.text())
def test_same_string_has_no_case_errors(text: str) -> None:
    assert count_case_errors(text, text) == 0


@given(
    text=st.text(
        alphabet=(
            st.characters(categories=["Lu"])
            .filter(lambda c: c.swapcase() != c)
            .filter(lambda c: len(c.swapcase()) == len(c))
            .filter(lambda c: c.swapcase().swapcase() == c)
        )
    ),
    fraction_swapped_case=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
)
def test_correct_count_when_swapped_uppercase(text: str, fraction_swapped_case: float) -> None:
    n_swapped = int(len(text) * fraction_swapped_case)
    flipped = text[:n_swapped].swapcase() + text[n_swapped:]
    assert count_case_errors(text, flipped) == n_swapped


@given(
    text=st.text(
        alphabet=(
            st.characters(categories=["Ll"])
            .filter(lambda c: c.swapcase() != c)
            .filter(lambda c: len(c.swapcase()) == len(c))
            .filter(lambda c: c.swapcase().swapcase() == c)
        )
    ),
    fraction_swapped_case=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
)
def test_correct_count_when_swapped_lowercase(text: str, fraction_swapped_case: float) -> None:
    n_swapped = int(len(text) * fraction_swapped_case)
    flipped = text[:n_swapped].swapcase() + text[n_swapped:]
    assert count_case_errors(text, flipped) == n_swapped


@st.composite
def string_pair_with_known_case_errors(draw: st.DrawFn) -> tuple[str, str, int]:
    rng = draw(st.randoms())
    text = draw(
        st.text(
            alphabet=(
                st.characters(categories=[rng.choice(["Ll", "Lu"])])
                .filter(lambda c: c.swapcase() != c)
                .filter(lambda c: len(c.swapcase()) == len(c))
                .filter(lambda c: c.swapcase().swapcase() == c)
            )
        )
    )
    inserted = draw(st.text(alphabet=st.characters(categories=["L"], exclude_characters=set(text))))

    num_flipped = draw(st.integers(min_value=0, max_value=len(text)))
    num_removed = draw(st.integers(min_value=0, max_value=len(text) - num_flipped))

    should_insert = rng.choice([True, False])
    predicted = text

    # To avoid swaps where there are multiple possible alignments with varying number case-swaps,
    # we only insert or delete characters.
    if not should_insert:
        predicted = remove_n_characters(text, num_removed, rng)
    predicted = caseswap_n_randomly(predicted, num_flipped, rng)
    if should_insert:
        predicted = interleave_strings(predicted, inserted, rng)

    return text, predicted, num_flipped


@given(string_pair_with_known_case_errors())
def test_known_case_errors(case_errors: tuple[str, str, int]) -> None:
    text, predicted, num_flipped = case_errors
    assert count_case_errors(text, predicted) == num_flipped
