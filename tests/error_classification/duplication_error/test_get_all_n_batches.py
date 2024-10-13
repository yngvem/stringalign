from collections.abc import Generator

import pytest
from stringalign.error_classification.duplication_error import get_all_n_batches


@pytest.mark.parametrize(
    "string, n, all_n_batches",
    [
        ("Hello", 1, (("H", "e", "l", "l", "o"),)),
        ("bananas", 2, (("ba", "na", "na", "s"), ("b", "an", "an", "as"))),
        (
            "Hello",
            2,
            (
                (
                    "He",
                    "ll",
                    "o",
                ),
                ("H", "el", "lo"),
            ),
        ),
        (
            "bananas",
            3,
            (
                (
                    "ban",
                    "ana",
                    "s",
                ),
                ("b", "ana", "nas"),
                (
                    "ba",
                    "nan",
                    "as",
                ),
            ),
        ),
    ],
)
def test_get_all_n_batches_with_examples(
    string: str, n: int, all_n_batches: Generator[tuple[str, ...], None, None]
) -> None:
    assert tuple(get_all_n_batches(string, n)) == all_n_batches
