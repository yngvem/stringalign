from collections import deque

import pytest
from stringalign.align import AlignmentOperation, Delete, Insert, Keep, Replace
from stringalign.evaluation import check_operation_for_horizontal_segmentation_error

# Some things to keep in mind:
#    Input to AlignmentOperation classification functions:
#         If center element is Keep, then first and last element will be Delete, Insert, Replace or None
#         If center element is Delete, Insert, Replace, then first and last element will be Keep or None


@pytest.mark.parametrize(
    "window, is_segmentation_error",
    [
        (deque([None, Delete("Hello"), Keep(" world!")]), True),
        (deque([None, Keep("Hello"), Delete(" world!")]), False),
        (deque([None, Replace("hELLO", "Hello"), Keep(" world!")]), True),
        (deque([None, Insert("Hello"), Keep(" world!")]), True),
        (deque([None, Keep("Hello"), Insert(" world!")]), False),
    ],
)
def test_horizontal_segmentation_beginning_of_line_with_examples(
    window: deque[AlignmentOperation], is_segmentation_error: bool
) -> None:
    assert check_operation_for_horizontal_segmentation_error(*window) == is_segmentation_error


@pytest.mark.parametrize(
    "window, is_segmentation_error",
    [
        (deque([Keep("Hello"), Delete(" world!"), None]), True),
        (deque([Delete("Hello"), Keep(" world!"), None]), False),
        (deque([Replace("hELLO", "Hello"), Keep(" world!"), None]), False),
        (deque([Keep(" world!"), Replace("hELLO", "Hello"), None]), True),
        (deque([Insert("Hello"), Keep(" world!"), None]), False),
        (deque([Keep("Hello"), Insert(" world!"), None]), True),
        (deque([None, Insert("Hello world!"), None]), True),
        (deque([None, Keep("Hello world!"), None]), False),
    ],
)
def test_horizontal_segmentation_end_of_line_with_examples(
    window: deque[AlignmentOperation], is_segmentation_error: bool
) -> None:
    assert check_operation_for_horizontal_segmentation_error(*window) == is_segmentation_error
