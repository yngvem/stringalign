import unicodedata
from typing import Literal

import hypothesis.strategies as st
import pytest
from hypothesis import given
from stringalign.tokenize import StringNormalizer


@given(string=st.text(alphabet=st.characters()))  # Specify st.characters to get invalid utf-8 code-points
@pytest.mark.parametrize("normalization", ["NFD", "NFKD", "NFC", "NFKC"])
def test_unicode_normalization(string: str, normalization: Literal["NFC", "NFD", "NFKC", "NFKD"]) -> None:
    """Letters are normalized according to the unicode standard."""
    normalizer = StringNormalizer(normalization=normalization)

    assert normalizer(string) == unicodedata.normalize(normalization, string)


@pytest.mark.parametrize("string", ["â", "ñ", "å", "ﬁ"])
@pytest.mark.parametrize("normalization", ["NFD", "NFKD", "NFC", "NFKC"])
def test_unicode_normalization_with_example(string: str, normalization: Literal["NFC", "NFD", "NFKC", "NFKD"]) -> None:
    """Letters are normalized according to the unicode standard."""
    normalizer = StringNormalizer(normalization=normalization)

    assert normalizer(string) == unicodedata.normalize(normalization, string)


@pytest.mark.parametrize(
    "string, normalization, different_normalization",
    [
        ["â", "NFD", "NFC"],
        ["â", "NFC", "NFD"],
        ["ñ", "NFD", "NFC"],
        ["ñ", "NFC", "NFD"],
        ["å", "NFD", "NFC"],
        ["å", "NFC", "NFD"],
        ["ﬁ", "NFD", "NFKD"],
        ["ﬁ", "NFC", "NFKC"],
    ],
)
def test_unicode_normalization_different_forms_with_example(
    string: str,
    normalization: Literal["NFC", "NFD", "NFKC", "NFKD"],
    different_normalization: Literal["NFC", "NFD", "NFKC", "NFKD"],
):
    """Using different normalization can give different strings."""
    normalizer = StringNormalizer(normalization=normalization)
    different_normalizer = StringNormalizer(normalization=different_normalization)

    assert normalizer(string) != different_normalizer(string)


@pytest.mark.parametrize(
    "string, casefolded",
    [
        ["ß", "ss"],  # German eszett
        ["Σ", "σ"],  # Greek capital sigma
        ["ﬀ", "ff"],  # Latin small ligature ff
        ["ﬄ", "ffl"],  # Latin small ligature ffl
        ["ﬃ", "ffi"],  # Latin small ligature ffi
        ["ſ", "s"],  # Latin ligature long s
        ["ﬅ", "st"],  # Latin small ligature long s t
        ["ﬆ", "st"],  # Latin small ligature st
        ["մ", "մ"],  # Armenian small letter men (U+0574)
        ["ᵹ", "ᵹ"],  # Latin small letter insular g (U+1D79)
        ["ῌ", "ηι"],  # Greek capital letter heta (U+1F2C)
    ],
)
def test_case_insensitive_with_example(string: str, casefolded: str) -> None:
    """The normalizer casefolds letters correctly."""
    normalizer = StringNormalizer(normalization=None, case_insensitive=True)

    assert normalizer(string) == casefolded


@given(string=st.text(alphabet=st.characters()))  # Specify st.characters to get invalid utf-8 code-points
def test_case_insensitive(string: str) -> None:
    """The normalizer casefolds the letters correctly"""
    normalizer = StringNormalizer(normalization=None, case_insensitive=True)

    assert normalizer(string) == string.casefold()


@pytest.mark.parametrize(
    "string, normalized_string",
    [
        ["Hello world", "Hello world"],
        ["Hello  world", "Hello world"],
        ["Hello                           world", "Hello world"],
        ["Hello  \t world", "Hello world"],
        ["Hello  \n world", "Hello world"],
        ["Hello  \u00a0 world", "Hello world"],  # no-break space
    ],
)
def test_normalize_whitespace_with_examples(string: str, normalized_string: str) -> None:
    """One or more whitespace characters are always replaced by a single regular space"""
    normalizer = StringNormalizer(normalization=None, normalize_whitespace=True)

    assert normalizer(string) == normalized_string


@given(string=st.text(alphabet=st.characters()))  # Specify st.characters to get invalid utf-8 code-points
def test_no_consecutive_space_after_normalize_whitespace(string: str) -> None:
    """After normalizing whitespace there should be no consecutive spaces"""
    normalizer = StringNormalizer(normalization=None, normalize_whitespace=True)

    assert "  " not in normalizer(string)


@given(string=st.text(alphabet=st.characters()))  # Specify st.characters to get invalid utf-8 code-points
def test_number_of_non_whitespace_unchanged_after_normalize_whitespace(string: str) -> None:
    """Normalizing the whitespace does not change the number of non-whitespace characters"""
    normalizer = StringNormalizer(normalization=None, normalize_whitespace=True)

    assert sum(not c.isspace() for c in string) == sum(not c.isspace() for c in normalizer(string))


@given(string=st.text(alphabet=st.characters()))  # Specify st.characters to get invalid utf-8 code-points
def test_non_whitespace_character_order_unchanged_after_normalize_whitespace(string: str) -> None:
    """Normalizing the whitespace does not change the order of non-whitespace characters"""
    normalizer = StringNormalizer(normalization=None, normalize_whitespace=True)

    assert "".join(c for c in string if not c.isspace()) == "".join(c for c in normalizer(string) if not c.isspace())


@pytest.mark.parametrize(
    "string, normalized_string",
    [
        ["Hello world", "Helloworld"],
        ["Hello  world", "Helloworld"],
        ["Hello                           world", "Helloworld"],
        ["Hello  \t world", "Helloworld"],
        ["Hello  \n world", "Helloworld"],
        ["Hello  \u00a0 world", "Helloworld"],  # no-break space
        ["H ello w o r   ld", "Helloworld"],
    ],
)
def test_remove_whitespace_with_examples(string: str, normalized_string: str) -> None:
    """After normalizing whitespace there should be no whitespace characters"""
    normalizer = StringNormalizer(normalization=None, remove_whitespace=True)

    assert normalizer(string) == normalized_string


@given(string=st.text(alphabet=st.characters()), whitespace=st.characters(categories=("Zs", "Zp", "Zl")))
def test_no_space_after_normalize_whitespace(string: str, whitespace: str) -> None:
    """After normalizing whitespace there should be no whitespace characters"""
    normalizer = StringNormalizer(normalization=None, remove_whitespace=True)

    assert whitespace not in normalizer(string)


@pytest.mark.parametrize(
    "string, normalized_string",
    [
        ["Hello world", "Hello world"],
        ["(Hello world!@%#~^¨)", "Hello world"],
        ["ÁáČčŠšŽžÅåÄäÖö", "ÁáČčŠšŽžÅåÄäÖö"],
        ["Is 4 examples enough?", "Is 4 examples enough"],
        ["no_we_need_underscores!", "noweneedunderscores"],
        ["and some \t more \n whitespace \u00a0!", "and some \t more \n whitespace \u00a0"],
    ],
)
def test_remove_non_word_characters_with_examples(string: str, normalized_string: str) -> None:
    """Test that non word characters are removed correctly"""
    normalizer = StringNormalizer(normalization=None, remove_non_word_characters=True)

    assert normalizer(string) == normalized_string


@given(string=st.text())
def test_remove_non_word_characters(string: str) -> None:
    """No non-word characters is in normalized text"""
    normalizer = StringNormalizer(remove_non_word_characters=True)
    normalized_string = normalizer(string)

    assert all(c.isalnum() or c.isspace() for c in normalized_string)


@given(string=st.text(alphabet=st.characters(categories=("Lu", "Ll", "Nd", "Zs"))))
def test_remove_non_word_characters_unchanged(string: str) -> None:
    """Text containing only word characters and spaces remain unchanged"""
    normalizer = StringNormalizer(normalization=None, remove_non_word_characters=True)
    normalized_string = normalizer(string)

    assert normalized_string == string


@given(string=st.text())
def test_remove_non_word_characters_length(string: str) -> None:
    """Normalized text should not be longer than the original text"""

    normalizer = StringNormalizer(normalization=None, remove_non_word_characters=True)
    normalized_string = normalizer(string)

    assert len(normalized_string) <= len(string)
