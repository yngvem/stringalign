import pytest
from stringalign.error_classification.diacritic_error import count_diacritic_errors


@pytest.mark.parametrize(
    "reference, predicted, expected",
    [
        ("ø", "o", True),
        ("å", "a", True),
        ("á", "à", True),
        ("å", "á", True),
        ("é", "e", True),
        ("Ð", "D", True),
        ("a", "á", True),
        ("a", "à", True),
        ("i", "i", False),  # Confusable, should give no diacritic error
        ("ø", "o̸", False),  # Confusable, should give no diacritic error
        ("Ð", "Đ", False),  # Confusable, should give no diacritic error
        ("a", "b", False),
    ],
)
def test_diacritic_error(reference: str, predicted: str, expected: bool) -> None:
    """Diacritic errors should be detected correctly"""
    result = count_diacritic_errors(reference, predicted)
    assert result == expected
