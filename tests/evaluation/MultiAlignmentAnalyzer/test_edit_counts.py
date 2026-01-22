from collections import Counter

from stringalign.align import Deleted, Replaced
from stringalign.evaluation import MultiAlignmentAnalyzer


def test_simple_example_known_values() -> None:
    """The edit operation are summed correctly for multiple strings"""
    evaluator = MultiAlignmentAnalyzer.from_strings(
        references=["ab", "abc"],
        predictions=["Ab", "a"],
    )
    alignment_operation_counts = evaluator.edit_counts
    expeced_alignment_operation_counts = {
        "raw": Counter(
            {Replaced(reference="a", predicted="A"): 1, Deleted(substring="b"): 1, Deleted(substring="c"): 1}
        ),
        "combined": Counter({Replaced(reference="a", predicted="A"): 1, Deleted(substring="bc"): 1}),
    }

    assert alignment_operation_counts == expeced_alignment_operation_counts
