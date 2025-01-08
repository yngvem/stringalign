from stringalign.align import Replace
from stringalign.evaluation import TranscriptionEvaluator


def test_raw_lookup():
    evaluator = TranscriptionEvaluator.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
    )
    assert evaluator.line_error_raw_lookup[Replace("b", "a")] == frozenset(
        {evaluator.line_errors[0], evaluator.line_errors[2]}
    )
    assert evaluator.line_error_raw_lookup[Replace("g", "f")] == frozenset(
        {
            evaluator.line_errors[1],
        }
    )
