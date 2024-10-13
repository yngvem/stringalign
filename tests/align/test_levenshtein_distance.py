import hypothesis.strategies as st
import Levenshtein
import pytest
from hypothesis import given
from stringalign.align import levenshtein_distance

from tests.utils import caseswap_n_randomly, interleave_strings, remove_n_characters


@pytest.mark.parametrize(
    "string1, string2, expected_distance",
    [
        ("", "", 0),
        ("a", "", 1),
        ("", "a", 1),
        ("a", "a", 0),
        ("a", "b", 1),
        ("a", "aa", 1),
        ("aa", "a", 1),
        ("A", "a", 1),
        ("hello", "Hallo", 2),
        ("string", "align", 5),
    ],
)
def test_levenshtein_distance_with_examples(string1: str, string2: str, expected_distance: int) -> None:
    assert levenshtein_distance(string1, string2) == expected_distance


@pytest.mark.parametrize(
    "string1, string2, expected_distance",
    [
        ("", "", 0),
        ("🐍", "", 1),
        ("🏳️‍🌈", "", 1),
        ("🏳️‍🌈", "🏳️‍🌈", 0),
        ("🏳️‍🌈", "🏳️‍🌈🏳️‍🌈", 1),
        ("🏳️‍🌈", "🏳️‍🌈🏳️‍🌈🏳️‍🌈", 2),
        ("🏳️‍🌈", "🏁", 1),
        ("😶‍🌫️", "😶", 1),
    ],
)
def test_levenshtein_distance_with_emojis(string1: str, string2: str, expected_distance: int) -> None:
    assert levenshtein_distance(string1, string2) == expected_distance


@given(
    string1=st.text(
        alphabet=st.characters(min_codepoint=0, max_codepoint=127, blacklist_characters="\r")
    ),  # Only ASCII characters
    string2=st.text(alphabet=st.characters(min_codepoint=0, max_codepoint=127, blacklist_characters="\r")),
)
def test_levenshtein_distance_with_Levenshtein(string1: str, string2: str) -> None:
    assert levenshtein_distance(string1, string2) == Levenshtein.distance(string1, string2)


@st.composite
def string_pair_with_known_levenshtein_distance(draw: st.DrawFn) -> tuple[str, str, int]:
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

    inserted = draw(
        st.text(alphabet=st.characters(categories=["L"], exclude_characters=set(text) | set(text.swapcase())))
    )

    num_flipped = draw(st.integers(min_value=0, max_value=len(text)))

    should_insert = rng.choice([True, False])
    predicted = text

    # To avoid swaps where there are multiple possible alignments with varying number case-swaps,
    # we only insert or delete characters.
    if not should_insert:
        num_removed = draw(st.integers(min_value=0, max_value=len(text) - num_flipped))
        num_inserted = 0
    else:
        num_removed = 0
        num_inserted = len(inserted)

    predicted = remove_n_characters(text, num_removed, rng)
    predicted = caseswap_n_randomly(predicted, num_flipped, rng)
    if should_insert:
        predicted = interleave_strings(predicted, inserted, rng)

    return text, predicted, num_flipped + num_inserted + num_removed


@given(string_pair_with_known_levenshtein_distance())
def test_levenshtein_distance_with_known_distance(string_pair: tuple[str, str, int]) -> None:
    string1, string2, expected_distance = string_pair
    assert levenshtein_distance(string1, string2) == expected_distance
