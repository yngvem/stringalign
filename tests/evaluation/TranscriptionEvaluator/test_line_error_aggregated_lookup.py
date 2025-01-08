from stringalign.align import Replace
from stringalign.evaluation import TranscriptionEvaluator


def test_raw_lookup():
    evaluator = TranscriptionEvaluator.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
    )
    assert evaluator.line_error_aggregated_lookup[Replace("b", "a")] == frozenset({evaluator.line_errors[0]})
    assert evaluator.line_error_aggregated_lookup[Replace("g", "f")] == frozenset({evaluator.line_errors[1]})
    assert evaluator.line_error_aggregated_lookup[Replace("bb", "aa")] == frozenset({evaluator.line_errors[2]})
