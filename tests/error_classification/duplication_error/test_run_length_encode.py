import hypothesis.strategies as st
import pytest
from hypothesis import given
from stringalign.error_classification.duplication_error import run_length_encode


@st.composite
def run_length_encoding(draw):
    num_characters = draw(st.integers(min_value=0, max_value=100))
    encoding = [None] * num_characters

    for idx in range(num_characters):
        exclude_characters = [encoding[idx - 1][0]] if idx else []
        character = draw(st.characters(exclude_characters=exclude_characters))
        count = draw(st.integers(min_value=1, max_value=10))
        encoding[idx] = (character, count)

    string = "".join(character * count for character, count in encoding)
    return string, tuple(encoding)


@given(run_length_encoding=run_length_encoding())
def test_run_length_encode(run_length_encoding: tuple[str, tuple[tuple[str, int]]]) -> None:
    string, encoding = run_length_encoding
    assert run_length_encode(string) == encoding


@pytest.mark.parametrize(
    "string, encoding",
    [
        ("Hello!", (("H", 1), ("e", 1), ("l", 2), ("o", 1), ("!", 1))),
        ("aabcaaadeefc", (("a", 2), ("b", 1), ("c", 1), ("a", 3), ("d", 1), ("e", 2), ("f", 1), ("c", 1))),
        (
            "Hello wooorld!!",
            (
                ("H", 1),
                ("e", 1),
                ("l", 2),
                ("o", 1),
                (" ", 1),
                ("w", 1),
                ("o", 3),
                ("r", 1),
                ("l", 1),
                ("d", 1),
                ("!", 2),
            ),
        ),
        ((("ba"), ("na"), ("na")), (("ba", 1), ("na", 2))),
    ],
)
def test_run_length_ecode_with_examples(string: str, encoding: list[tuple[str, int]]) -> None:
    assert run_length_encode(string) == encoding
