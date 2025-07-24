import pytest
from stringalign.error_classification.confusable_error import count_confusable_errors
from stringalign.tokenize import GraphemeClusterTokenizer


@pytest.mark.parametrize(
    "reference, predicted, expected, confusables",
    [
        ("a", "a", 0, "confusables"),
        ("a", "b", 0, "confusables"),
        ("a", "b", 1, {"a": "b"}),
        ("a", "b", 1, {"b": "a"}),
        ("l", "1", 1, "confusables"),
    ],
)
def test_with_simple_example(reference, predicted, expected, confusables):
    assert count_confusable_errors(reference, predicted, GraphemeClusterTokenizer(), confusables) == expected


def test_with_pathological_example():
    """Confusable errors should be detected even when resolving confusables worsens the CER

    This is a particularly pathological example. There is a confusable error: l -> 1, but
    resolving confusables will also turn the "ﬃ" into "ffi", which will make the CER worsen.

    Here, we test that the confusable error is still detected, even though the CER will worsen
    """
    reference = "l b"
    predicted = "1 ﬃ"

    assert count_confusable_errors(reference, predicted, GraphemeClusterTokenizer(), "confusables") == 1
