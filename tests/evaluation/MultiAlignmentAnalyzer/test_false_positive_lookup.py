import pytest
from stringalign.evaluation import MultiAlignmentAnalyzer


def test_simple_example() -> None:
    evaluator = MultiAlignmentAnalyzer.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
    )

    assert evaluator.false_positive_lookup["b"] == frozenset(
        {evaluator.alignment_analyzers[0], evaluator.alignment_analyzers[2]}
    )
    assert evaluator.false_positive_lookup["g"] == frozenset({evaluator.alignment_analyzers[1]})


def test_key_error_for_non_existent_false_positive() -> None:
    evaluator = MultiAlignmentAnalyzer.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
    )

    with pytest.raises(KeyError):
        _ = evaluator.false_positive_lookup["a"]
