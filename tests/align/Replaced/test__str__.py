import pytest
from stringalign.align import Replaced


@pytest.mark.parametrize(
    "kept_op, expected_str",
    [
        (Replaced("A", "B"), "REPLACED 'A' -> 'B'"),
        (Replaced("Hello, World!", ""), "REPLACED 'Hello, World!' -> ''"),
    ],
)
def test_simple_formating_of_known_examples(kept_op: Replaced, expected_str: str) -> None:
    """__str__ works as expected for simple known examples"""
    assert str(kept_op) == expected_str
