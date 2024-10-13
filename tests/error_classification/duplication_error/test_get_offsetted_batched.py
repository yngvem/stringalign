import hypothesis.strategies as st
import pytest
from hypothesis import given
from stringalign.compat import batched
from stringalign.error_classification.duplication_error import get_offsetted_batched


@pytest.mark.parametrize(
    "string, batch_size, offset, offsetted_batched",
    [
        ("Hello", 2, 1, (("H",), ("e", "l"), ("l", "o"))),
        ("Hello", 2, 0, (("H", "e"), ("l", "l"), ("o",))),
        ("Hello", 1, 0, (("H",), ("e",), ("l",), ("l",), ("o",))),
        ("Hello", 3, 0, (("H", "e", "l"), ("l", "o"))),
        ("Hello", 3, 1, (("H",), ("e", "l", "l"), ("o",))),
        ("Hello", 3, 2, (("H", "e"), ("l", "l", "o"))),
    ],
)
def test_get_offsetted_batched_with_examples(
    string: str, batch_size: int, offset: int, offsetted_batched: tuple[tuple[str, ...], ...]
) -> None:
    assert tuple(get_offsetted_batched(string, batch_size, offset=offset)) == offsetted_batched


@given(
    string=st.text(),
    batch_size=st.integers(min_value=1, max_value=100),
)
def test_get_offsetted_batched_same_as_batched_when_offset_is_zero(string: str, batch_size: int) -> None:
    assert tuple(get_offsetted_batched(string, batch_size, offset=0)) == tuple(batched(string, batch_size))
