import pytest
from stringalign.align import AlignmentOperation, Deleted, Inserted, Kept, Replaced
from stringalign.statistics import _is_combined_alignment
from stringalign.tokenize import GraphemeClusterTokenizer


def test_simple_not_combined_example() -> None:
    example_alignment: list[AlignmentOperation] = [Kept("h"), Kept("e"), Deleted("i")]
    assert not _is_combined_alignment(example_alignment, tokenizer=GraphemeClusterTokenizer())


@pytest.mark.parametrize(
    "alignment_op",
    [
        Kept("He"),
        Deleted("He"),
        Inserted("He"),
        Replaced("He", "h"),
        Replaced("H", "He"),
    ],
)
def test_simple_combined_example(alignment_op: AlignmentOperation) -> None:
    example_alignment = [Kept("a"), alignment_op, Kept("a")]
    assert _is_combined_alignment(example_alignment, tokenizer=GraphemeClusterTokenizer())
