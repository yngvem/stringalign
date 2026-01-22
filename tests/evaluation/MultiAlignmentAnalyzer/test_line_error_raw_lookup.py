from stringalign.align import Replaced
from stringalign.evaluation import MultiAlignmentAnalyzer


def test_raw_lookup():
    evaluator = MultiAlignmentAnalyzer.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
    )
    assert evaluator.alignment_analyzer_raw_lookup[Replaced("a", "b")] == frozenset(
        {evaluator.alignment_analyzers[0], evaluator.alignment_analyzers[2]}
    )
    assert evaluator.alignment_analyzer_raw_lookup[Replaced("f", "g")] == frozenset(
        {
            evaluator.alignment_analyzers[1],
        }
    )
