import pytest
from stringalign.align import Deleted, Kept, align_strings
from stringalign.evaluate import AlignmentAnalyzer, FrozenDict
from stringalign.tokenize import GraphemeClusterTokenizer, SplitAtWhitespaceTokenizer


@pytest.mark.parametrize(
    "alignment_analyzer, ter_value",
    [
        (
            AlignmentAnalyzer(
                reference="Hi, world!",
                predicted="Hi, world",
                combined_alignment=(Kept("Hi, world"), Deleted("!")),
                raw_alignment=tuple(align_strings("Hi, world!", "Hi, world")[0]),
                unique_alignment=True,
                heuristic_edit_classifications=FrozenDict(),
                metadata=None,
                tokenizer=GraphemeClusterTokenizer(),
            ),
            0.1,
        ),
        (
            AlignmentAnalyzer(
                reference="H",
                predicted="H",
                combined_alignment=(Kept("H"),),
                raw_alignment=(Kept("H"),),
                unique_alignment=True,
                heuristic_edit_classifications=FrozenDict(),
                metadata=None,
                tokenizer=GraphemeClusterTokenizer(),
            ),
            0,
        ),
        (
            AlignmentAnalyzer(
                reference="Hello",
                predicted="",
                combined_alignment=(Deleted("Hello"),),
                raw_alignment=(Deleted("Hello"),),
                unique_alignment=True,
                heuristic_edit_classifications=FrozenDict(),
                metadata=None,
                tokenizer=SplitAtWhitespaceTokenizer(),
            ),
            1,
        ),
    ],
)
def test_simple_example_known_values(alignment_analyzer: AlignmentAnalyzer, ter_value: float) -> None:
    assert alignment_analyzer.compute_ter() == ter_value
