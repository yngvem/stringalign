from stringalign.align import Replaced
from stringalign.evaluation import TranscriptionEvaluator


def test_raw_lookup():
    evaluator = TranscriptionEvaluator.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
    )
    le_agg_lookup = evaluator.line_error_combined_lookup
    assert le_agg_lookup[Replaced(reference="a", predicted="b")] == frozenset({evaluator.line_errors[0]})
    assert le_agg_lookup[Replaced(reference="f", predicted="g")] == frozenset({evaluator.line_errors[1]})
    assert le_agg_lookup[Replaced(reference="aa", predicted="bb")] == frozenset({evaluator.line_errors[2]})
