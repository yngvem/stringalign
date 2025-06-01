from collections import deque

import pytest
from stringalign.align import AlignmentOperation, Deleted, Inserted, Kept, Replaced
from stringalign.evaluation import check_operation_for_horizontal_segmentation_error

# Some things to keep in mind:
#    Input to AlignmentOperation classification functions:
#         If center element is Kept, then first and last element will be Deleted, Inserted, Replaced or None
#         If center element is Deleted, Insertd, Replaced, then first and last element will be Keep or None


@pytest.mark.parametrize(
    "window, is_segmentation_error",
    [
        (deque([None, Inserted("Hello"), Kept(" world!")]), True),
        (deque([None, Kept("Hello"), Inserted(" world!")]), False),
        (deque([None, Replaced("hELLO", "Hello"), Kept(" world!")]), True),
        (deque([None, Deleted("Hello"), Kept(" world!")]), True),
        (deque([None, Kept("Hello"), Deleted(" world!")]), False),
    ],
)
def test_horizontal_segmentation_beginning_of_line_with_examples(
    window: deque[AlignmentOperation], is_segmentation_error: bool
) -> None:
    assert check_operation_for_horizontal_segmentation_error(*window) == is_segmentation_error


@pytest.mark.parametrize(
    "window, is_segmentation_error",
    [
        (deque([Kept("Hello"), Inserted(" world!"), None]), True),
        (deque([Inserted("Hello"), Kept(" world!"), None]), False),
        (deque([Replaced("hELLO", "Hello"), Kept(" world!"), None]), False),
        (deque([Kept(" world!"), Replaced("hELLO", "Hello"), None]), True),
        (deque([Deleted("Hello"), Kept(" world!"), None]), False),
        (deque([Kept("Hello"), Deleted(" world!"), None]), True),
        (deque([None, Deleted("Hello world!"), None]), True),
        (deque([None, Kept("Hello world!"), None]), False),
    ],
)
def test_horizontal_segmentation_end_of_line_with_examples(
    window: deque[AlignmentOperation], is_segmentation_error: bool
) -> None:
    assert check_operation_for_horizontal_segmentation_error(*window) == is_segmentation_error
