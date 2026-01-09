from typing import Literal

import pytest
import stringalign.tokenize
from stringalign.error_classification.duplication_error import check_ngram_duplication_errors


@pytest.mark.parametrize(
    "reference, predicted, n, type, expected",
    [
        ("banana", "bananana", 2, "inserted", True),
        ("banana", "bananana", 1, "inserted", False),
        ("banana", "bananana", 1, "deleted", False),
        ("banana", "bananana", 2, "deleted", False),
        ("banana", "bana", 2, "deleted", True),
        ("banana", "bana", 1, "deleted", False),
        ("banana", "bana", 1, "inserted", False),
        ("banana", "bana", 2, "inserted", False),
        ("kitten", "kiten", 1, "deleted", True),
        ("kitten", "kiten", 2, "deleted", False),
        ("kitten", "kiten", 1, "inserted", False),
        ("kitten", "kiten", 2, "inserted", False),
        ("turtle", "turttle", 1, "inserted", True),
        ("turtle", "turttle", 2, "inserted", False),
        ("turtle", "turttle", 1, "deleted", False),
        ("turtle", "turttle", 2, "deleted", False),
    ],
)
def test_check_ngram_duplication_errors_with_examples(
    reference: str, predicted: str, n: int, type: Literal["inserted", "deleted"], expected: bool
) -> None:
    tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()
    assert check_ngram_duplication_errors(reference, predicted, n=n, error_type=type, tokenizer=tokenizer) == expected


def test_check_ngram_duplication_errors_with_invalid_type() -> None:
    tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()
    with pytest.raises(ValueError):
        check_ngram_duplication_errors("banana", "bananana", n=2, error_type="invalid", tokenizer=tokenizer)  # type: ignore
