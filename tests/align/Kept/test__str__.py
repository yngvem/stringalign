import pytest
from stringalign.align import Kept


@pytest.mark.parametrize(
    "kept_op, expected_str",
    [
        (Kept("A"), "KEPT     'A'"),
        (Kept("Hello, World!"), "KEPT     'Hello, World!'"),
    ],
)
def test_simple_formating_of_known_examples(kept_op: Kept, expected_str: str) -> None:
    """__str__ works as expected for simple known examples"""
    assert str(kept_op) == expected_str
