import pytest
from stringalign.align import AlignmentOperation, Delete, Insert, Keep, Replace
from stringalign.evaluation import check_operation_for_case_error


@pytest.mark.parametrize("previous_operation", [None, Keep("a"), Delete("a"), Insert("a"), Replace("a", "b")])
@pytest.mark.parametrize("next_operation", [None, Keep("a"), Delete("a"), Insert("a"), Replace("a", "b")])
@pytest.mark.parametrize(
    "current_operation, num_case_errors",
    [
        (Replace("String", "String"), 0),
        (Replace("String", "sTRING"), 6),
        (Replace("String", "Align"), 0),
        (Replace("hELL", "Hello"), 4),
        (Replace("h", "Hello"), 1),
        (Replace("h", "Hello"), 1),
    ],
)
def test_case_error(
    previous_operation: AlignmentOperation,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation,
    num_case_errors: int,
) -> None:
    assert check_operation_for_case_error(previous_operation, current_operation, next_operation) == num_case_errors
