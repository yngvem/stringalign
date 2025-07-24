# Input: Reference and predicted text
# Output: bool if the only error(s) are accent errors
# (i.e. still error after normalisation and confusable resolving, but not after removing all nonspacing marks)
import unicodedata

from stringalign.normalize import StringNormalizer


def check_diacritic_errors(reference: str, predicted: str) -> bool:
    """Check if the only difference between the reference and predicted text is due to diacritic errors.

    The function resolves confusables and normalizes the string to normalized decomposed form.
    Then it removes all nonspacing marks and checks if the resulting strings are equal.

    As diacritics are (almost always) nonspacing marks, this will return True if the only difference is
    due to diacritics.

    The reason we resolve confusables is that some letters have diacritics that cannot be detected by
    counting nonspacing marks in decomposed strings. For example, the letter "ø" is confusable with "o" and
    a Combining Long Solidus Overlay (U+0338), which is a nonspacing mark. If we don't resolve confusables,
    then the function will return False when "ø" is transcribed as "o", while if we first resolve confusables,
    then it will return True.

    Note:
    -----
    Unicode is a vast and complex standard, so there might be some edge cases where this function
    does not detect all diacritic-errors. If you find such cases, please report them as issues.

    Parameters:
    -----------
    reference
        The reference text.
    predicted
        The predicted text.

    Returns:
    --------
    bool
        True if the only difference is due to diacritic errors, False otherwise.
    """
    normalizer = StringNormalizer(normalization="NFD", resolve_confusables="confusables")

    reference_normalized = normalizer(reference)
    predicted_normalized = normalizer(predicted)

    reference_no_marks = "".join(char for char in reference_normalized if unicodedata.category(char) != "Mn")
    predicted_no_marks = "".join(char for char in predicted_normalized if unicodedata.category(char) != "Mn")

    return reference_no_marks == predicted_no_marks and reference_normalized != predicted_normalized
