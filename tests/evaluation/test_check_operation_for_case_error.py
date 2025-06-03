import pytest
from stringalign.align import AlignmentOperation, Deleted, Inserted, Kept, Replaced
from stringalign.evaluation import check_operation_for_case_error


@pytest.mark.parametrize("previous_operation", [None, Kept("a"), Inserted("a"), Deleted("a"), Replaced("a", "b")])
@pytest.mark.parametrize("next_operation", [None, Kept("a"), Inserted("a"), Deleted("a"), Replaced("a", "b")])
@pytest.mark.parametrize(
    "current_operation, num_case_errors",
    [
        (Replaced("String", "String"), 0),
        (Replaced("String", "sTRING"), 6),
        (Replaced("String", "Align"), 0),
        (Replaced("hELL", "Hello"), 4),
        (Replaced("h", "Hello"), 1),
        (Replaced("h", "Hello"), 1),
    ],
)
def test_case_error(
    previous_operation: AlignmentOperation,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation,
    num_case_errors: int,
) -> None:
    assert check_operation_for_case_error(previous_operation, current_operation, next_operation) == num_case_errors
