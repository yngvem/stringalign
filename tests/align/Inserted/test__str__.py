import pytest
from stringalign.align import Inserted


@pytest.mark.parametrize(
    "kept_op, expected_str",
    [
        (Inserted("A"), "INSERTED 'A'"),
        (Inserted("Hello, World!"), "INSERTED 'Hello, World!'"),
    ],
)
def test_simple_formating_of_known_examples(kept_op: Inserted, expected_str: str) -> None:
    """__str__ works as expected for simple known examples"""
    assert str(kept_op) == expected_str
