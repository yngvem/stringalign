import pytest
from stringalign.evaluation import TranscriptionEvaluator


def test_simple_example() -> None:
    evaluator = TranscriptionEvaluator.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
    )

    assert evaluator.false_negative_lookup["a"] == frozenset({evaluator.line_errors[0], evaluator.line_errors[2]})
    assert evaluator.false_negative_lookup["f"] == frozenset({evaluator.line_errors[1]})


def test_key_error_for_non_existent_false_negative() -> None:
    evaluator = TranscriptionEvaluator.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
    )

    with pytest.raises(KeyError):
        _ = evaluator.false_negative_lookup["c"]
