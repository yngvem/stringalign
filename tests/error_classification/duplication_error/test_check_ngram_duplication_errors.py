# Check that banana -> bananana is 2-gram insertion but not 1-gram insertion and not 1/2-gram deletion
# Example with banana -> bana is 2-gram deletion but not 1-gram deletion and not 1/2-gram insertion
# Example with kitten -> kiten is 1-gram deletion but not 2-gram deletion and not 1/2-gram insertion
# Example with turtle -> turttle is 1-gram insertion but not 2-gram insertion and not 1/2-gram deletion


from typing import Literal

import pytest
from stringalign.error_classification.duplication_error import check_ngram_duplication_errors


@pytest.mark.parametrize(
    "reference, predicted, n, type, expected",
    [
        ("banana", "bananana", 2, "insert", True),
        ("banana", "bananana", 1, "insert", False),
        ("banana", "bananana", 1, "delete", False),
        ("banana", "bananana", 2, "delete", False),
        ("banana", "bana", 2, "delete", True),
        ("banana", "bana", 1, "delete", False),
        ("banana", "bana", 1, "insert", False),
        ("banana", "bana", 2, "insert", False),
        ("kitten", "kiten", 1, "delete", True),
        ("kitten", "kiten", 2, "delete", False),
        ("kitten", "kiten", 1, "insert", False),
        ("kitten", "kiten", 2, "insert", False),
        ("turtle", "turttle", 1, "insert", True),
        ("turtle", "turttle", 2, "insert", False),
        ("turtle", "turttle", 1, "delete", False),
        ("turtle", "turttle", 2, "delete", False),
    ],
)
def test_check_ngram_duplication_errors_with_examples(
    reference: str, predicted: str, n: int, type: Literal["insert", "delete"], expected: bool
) -> None:
    assert check_ngram_duplication_errors(reference, predicted, n=n, type=type) == expected


def test_check_ngram_duplication_errors_with_invalid_type() -> None:
    with pytest.raises(ValueError):
        check_ngram_duplication_errors("banana", "bananana", n=2, type="invalid")  # type: ignore
