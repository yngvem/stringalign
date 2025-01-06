from stringalign.align import Replace, align_strings
from stringalign.statistics import StringConfusionMatrix
from stringalign.tokenize import SplitAtWordBoundaryTokenizer, UnicodeWordTokenizer


def test_from_strings() -> None:
    reference = "hello world"
    predicted = "hello Python"

    result = StringConfusionMatrix.from_strings(reference, predicted, tokenizer=UnicodeWordTokenizer())
    assert result.false_positives["Python"] == 1
    assert result.false_negatives["world"] == 1
    assert result.true_positives["hello"] == 1
    assert result.edit_counts[Replace("Python", "world")] == 1


def test_from_strings_and_alignment() -> None:
    reference = "hello world"
    predicted = "hello Python"
    tokenizer = SplitAtWordBoundaryTokenizer()
    alignment, _unique = align_strings(reference, predicted, tokenizer)

    result = StringConfusionMatrix.from_strings_and_alignment(reference, predicted, alignment, tokenizer)
    assert result.false_positives["Python"] == 1
    assert result.false_negatives["world"] == 1
    assert result.true_positives["hello"] == 1
    assert result.edit_counts[Replace("Python", "world")] == 1
