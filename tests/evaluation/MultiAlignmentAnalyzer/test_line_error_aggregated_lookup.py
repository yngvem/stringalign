from stringalign.align import Replaced
from stringalign.evaluation import MultiAlignmentAnalyzer


def test_raw_lookup():
    evaluator = MultiAlignmentAnalyzer.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
    )
    le_agg_lookup = evaluator.alignment_error_combined_lookup
    assert le_agg_lookup[Replaced(reference="a", predicted="b")] == frozenset({evaluator.alignment_analyzers[0]})
    assert le_agg_lookup[Replaced(reference="f", predicted="g")] == frozenset({evaluator.alignment_analyzers[1]})
    assert le_agg_lookup[Replaced(reference="aa", predicted="bb")] == frozenset({evaluator.alignment_analyzers[2]})
