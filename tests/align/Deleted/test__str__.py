import pytest
from stringalign.align import Deleted


@pytest.mark.parametrize(
    "kept_op, expected_str",
    [
        (Deleted("A"), "DELETED  'A'"),
        (Deleted("Hello, World!"), "DELETED  'Hello, World!'"),
    ],
)
def test_simple_formating_of_known_examples(kept_op: Deleted, expected_str: str) -> None:
    """__str__ works as expected for simple known examples"""
    assert str(kept_op) == expected_str
