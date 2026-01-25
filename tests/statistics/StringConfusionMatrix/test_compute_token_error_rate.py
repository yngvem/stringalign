import typing
import unicodedata

import hypothesis
import hypothesis.strategies as st
import jiwer
import pytest
from stringalign.statistics import StringConfusionMatrix


def test_simple_example() -> None:
    """The token error rate is the same as Jiwer's for a simple example."""
    truth, predicted = "aaaabbcce", "aaabbbcda"
    cm = StringConfusionMatrix.from_strings(truth, predicted)
    ter = cm.compute_token_error_rate()
    assert ter == pytest.approx(jiwer.cer(truth, predicted))


def test_different_than_jiwer_on_decomposed_diacritic() -> None:
    """The token error rate is different compared to Jiwer for decomposed diacritic characters."""
    truth = unicodedata.normalize("NFD", "å")
    predicted = "a"
    cm = StringConfusionMatrix.from_strings(truth, predicted)
    ter = cm.compute_token_error_rate()
    assert ter > typing.cast(float, jiwer.cer(truth, predicted)) - 1e-8


def test_empty_reference_string_and_empty_predicted_string() -> None:
    """The token error rate is zero for empty strings."""
    cm = StringConfusionMatrix.from_strings("", "")
    ter = cm.compute_token_error_rate()
    assert ter == 0.0


def test_empty_reference_string_and_non_empty_predicted_string() -> None:
    """The token error rate is one for an empty reference string and a non-empty predicted string."""
    cm = StringConfusionMatrix.from_strings("", "not empty")
    ter = cm.compute_token_error_rate()
    assert ter == float("inf")


@hypothesis.given(
    predicted=st.text(alphabet=st.characters(max_codepoint=127)),  # ASCII characters only
    reference=st.text(alphabet=st.characters(max_codepoint=127), min_size=1),  # ASCII characters only
)
def test_character_tokenizer_gives_same_cer_as_jiwer_for_ascii(
    reference: str,
    predicted: str,
) -> None:
    """Calculating error rate with character tokenizer gives same result as jiwer cer for ASCII strings.

    Note, we cannot use Jiwer's tokenizer here, since it strips the input, which makes it so the tokens themselves
    change if tokenized again. That is ``tokenize(tokenize(string)[i]) != tokenize(string)[i]``. This breaks an
    assumption of the string confusion matrix.
    """
    # Jiwer strips strings before tokenizing, stringalign does not, so let's strip them first.
    reference = reference.strip().replace("\r", "")  # Jiwer doesn't handle newlines well
    predicted = predicted.strip().replace("\r", "")  # Jiwer doesn't handle newlines well
    hypothesis.assume(reference)
    cm = StringConfusionMatrix.from_strings(reference, predicted)
    cer = cm.compute_token_error_rate()
    assert jiwer.cer(reference, predicted) == pytest.approx(cer)


@hypothesis.given(
    predicted=st.text(alphabet=st.characters(max_codepoint=127)),  # ASCII characters only
    reference=st.text(alphabet=st.characters(max_codepoint=127), min_size=1),  # ASCII characters only
)
def test_word_tokenizer_gives_same_wer_as_jiwer_for_simple_words(
    reference: str,
    predicted: str,
) -> None:
    """Calculating error rate with the jiwer word tokenizer gives the same result as jiwer wer for simple words."""
    predicted = predicted.strip().replace("\r", "")  # Jiwer doesn't handle newlines well
    reference = reference.strip().replace("\r", "")  # Jiwer doesn't handle newlines well
    hypothesis.assume(reference)

    def tokenizer(s: str) -> list[str]:
        return jiwer.transformations.wer_default([s])[0]

    assert len(tokenizer("ab cd")) == 2

    cm = StringConfusionMatrix.from_strings(reference, predicted, tokenizer=tokenizer)  # type: ignore
    wer = cm.compute_token_error_rate()
    assert jiwer.wer(reference, predicted) == pytest.approx(wer)
