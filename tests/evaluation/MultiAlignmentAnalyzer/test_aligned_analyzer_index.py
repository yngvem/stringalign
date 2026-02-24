from stringalign.align import Replaced
from stringalign.evaluate import MultiAlignmentAnalyzer


def test_raw_lookup() -> None:
    evaluator = MultiAlignmentAnalyzer.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
    )
    raw_index = evaluator.alignment_operator_index["raw"]
    assert raw_index[Replaced(reference="a", predicted="b")] == frozenset(
        {evaluator.alignment_analyzers[0], evaluator.alignment_analyzers[2]}
    )
    assert raw_index[Replaced(reference="f", predicted="g")] == frozenset({evaluator.alignment_analyzers[1]})


def test_combined_lookup() -> None:
    evaluator = MultiAlignmentAnalyzer.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
    )
    combined_index = evaluator.alignment_operator_index["combined"]
    assert combined_index[Replaced(reference="a", predicted="b")] == frozenset({evaluator.alignment_analyzers[0]})
    assert combined_index[Replaced(reference="f", predicted="g")] == frozenset({evaluator.alignment_analyzers[1]})
    assert combined_index[Replaced(reference="aa", predicted="bb")] == frozenset({evaluator.alignment_analyzers[2]})
