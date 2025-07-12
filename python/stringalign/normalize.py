import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Literal


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in the text to a single space."""
    return re.sub(r"\s+", " ", text).strip()


def remove_whitespace(text: str) -> str:
    """Remove all whitespace from the text."""
    return re.sub(r"\s+", "", text)


def remove_non_word_characters(text: str) -> str:
    """Remove all non-word characters from the text, except spaces."""
    return re.sub(r"[^\w\s]|_", "", text)


def resolve_confusables(text: str, confusable_map: dict[str, str]) -> str:
    """Resolve confusable characters in the text using the provided mapping."""
    return "".join(confusable_map.get(char, char) for char in text)


@lru_cache
def load_confusable_map(confusable_type: Literal["confusables", "intentional"]) -> dict[str, str]:
    """Load a confusable character mapping from a JSON file.

    Can either load 'confusable characters' or 'intentional confusables'.

    Confusable characters are based on on the official Unicode list of confusable characters, i.e. characters that often
    look visually similar (e.g. ρ (lowercase rho) and p). It is available at
    https://www.unicode.org/Public/security/latest/confusables.txt

    Intentional confusables are based on the official list of characters that are probably designed to be identical
    when using a harmonized typeface design (e.g. а (cyrillic) and a (latin)). The list is available at
    https://www.unicode.org/Public/security/latest/intentional.txt

    For more information, see the Unicode Technical Standard #39 (UTS #39) about security consideration for unicode at
    https://www.unicode.org/reports/tr39/.

    Arguments
    ---------
    confusable_type:
        The type of confusable characters to load. Can be either "confusables" or "intentional".

    Returns
    -------
    dict[str, str]:
        A mapping of confusable characters to their corresponding counterparts.
    """
    if not confusable_type in {"confusables", "intentional"}:
        raise ValueError(f"Invalid confusable type: {confusable_type}. Must be 'confusables' or 'intentional'.")

    confusable_data = Path(__file__).with_name("unicode_data") / f"{confusable_type}.json"
    assert confusable_data.exists(), (
        f"Confusable data file not found: {confusable_data}. This is a bug and should be reported."
    )

    with confusable_data.open(encoding="utf-8") as f:
        return json.load(f)


class StringNormalizer:
    """Simple string normalizer, used to remove "irrelevant" differences when comparing strings.

    Arguments
    ---------
    normalization:
        Which unicode normalization to use
    case_insensitive:
        If true, run `str.casefold` to make all letters lowercase
    normalize_whitespace:
        Turn any occurance of one or more whitespaces into exactly one regular space
    remove_whitespace:
        Turn any occurance of one or more whitespaces into exactly one regular space
    remove_non_word_characters:
        Remove any character non-alphabetic and non-numeric unicode characters except spaces.
    resolve_confusables:
        How to resolve confusable characters. If it's a string, then it should signify whether it's the Unicode
        confusable or intentional confusable list that should be used. If it's a dictionary, then any occurence
        of a key in the text will be replaced with its corresponding value (so ``{"a": "b"}`` will replace all
        occurences of "a" with "b" in the text). If it's None, then no confusable characters will be resolved.
    """

    def __init__(
        self,
        normalization: Literal["NFC", "NFD", "NFKC", "NFKD", None] = "NFC",
        case_insensitive: bool = False,
        normalize_whitespace: bool = False,
        remove_whitespace: bool = False,
        remove_non_word_characters: bool = False,
        resolve_confusables: Literal["confusables", "intentional", None] | dict[str, str] = None,
    ) -> None:
        self.normalization = normalization
        self.case_insensitive = case_insensitive
        self.normalize_whitespace = normalize_whitespace
        self.remove_whitespace = remove_whitespace
        self.remove_non_word_characters = remove_non_word_characters
        self.resolve_confusables = resolve_confusables

    def __call__(self, text: str) -> str:
        # According to Unicode, we should normalize strings before casefolding them.
        if self.normalization is not None:
            text = unicodedata.normalize(self.normalization, text)

        if self.case_insensitive:
            text = text.casefold()
        if self.normalize_whitespace:
            text = normalize_whitespace(text)
        if self.remove_whitespace:
            text = remove_whitespace(text)
        if self.remove_non_word_characters:
            text = remove_non_word_characters(text)
        if self.resolve_confusables is not None:
            if isinstance(self.resolve_confusables, dict):
                confusable_map = self.resolve_confusables
            else:
                confusable_map = load_confusable_map(self.resolve_confusables)
            text = resolve_confusables(text, confusable_map)

        # Some of these operations, like casefolding, can make normalized text unnormalized.
        # So we normalize again to ensure the text is in the correct form.
        if self.normalization is not None:
            text = unicodedata.normalize(self.normalization, text)

        return text
