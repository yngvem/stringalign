from collections import Counter

from stringalign.align import Deleted, Kept, Replaced
from stringalign.evaluate import MultiAlignmentAnalyzer


def test_simple_example_known_values() -> None:
    """The alignment operation are summed correctly for multiple strings"""
    evaluator = MultiAlignmentAnalyzer.from_strings(
        references=["ab", "abc"],
        predictions=["Ab", "ab"],
    )
    alignment_operation_counts = evaluator.alignment_operation_counts
    expeced_alignment_operation_counts = {
        "raw": Counter(
            {
                Replaced(reference="a", predicted="A"): 1,
                Kept(substring="b"): 2,
                Kept(substring="a"): 1,
                Deleted(substring="c"): 1,
            }
        ),
        "combined": Counter(
            {
                Replaced(reference="a", predicted="A"): 1,
                Kept(substring="b"): 1,
                Kept(substring="ab"): 1,
                Deleted(substring="c"): 1,
            }
        ),
    }

    assert alignment_operation_counts == expeced_alignment_operation_counts
