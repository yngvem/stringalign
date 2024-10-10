from collections.abc import Generator

import pytest
from stringalign.error_classification.duplication_error import get_all_n_run_length_encodings


@pytest.mark.parametrize(
    "string, n, all_n_run_length_encodings",
    [
        ("Hello", 1, ((("H", 1), ("e", 1), ("l", 2), ("o", 1)),)),
        ("bananas", 2, ((("ba", 1), ("na", 2), ("s", 1)), (("b", 1), ("an", 2), ("as", 1)))),
        (
            "Hello",
            2,
            (
                (
                    ("He", 1),
                    ("ll", 1),
                    ("o", 1),
                ),
                (("H", 1), ("el", 1), ("lo", 1)),
            ),
        ),
        (
            "bananas",
            3,
            (
                (
                    ("ban", 1),
                    ("ana", 1),
                    ("s", 1),
                ),
                (
                    ("b", 1),
                    ("ana", 1),
                    ("nas", 1),
                ),
                (
                    ("ba", 1),
                    ("nan", 1),
                    ("as", 1),
                ),
            ),
        ),
    ],
)
def test_get_all_n_run_length_encodings(
    string: str, n: int, all_n_run_length_encodings: Generator[tuple[tuple[str, int], ...], None, None]
) -> None:
    assert tuple(get_all_n_run_length_encodings(string, n)) == all_n_run_length_encodings
