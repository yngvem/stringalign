import stringalign
from stringalign.align import levenshtein_distance


# TODO: Make this function accept a tokenizer
def count_case_errors(reference: str, predicted: str) -> int:
    """Count the number of errors that are solely due to mistaken casing.

    This function counts the number of edits we can avoid if we make casefold the strings before aligning them.

    Parameters:
    -----------
    reference
        The reference text.
    predicted
        The predicted text.

    Returns:
    --------
    int
        The number of case errors.
    """
    distance = levenshtein_distance(reference, predicted)
    casefolded_distance = levenshtein_distance(
        reference,
        predicted,
        tokenizer=stringalign.tokenize.GraphemeClusterTokenizer(
            post_clustering_normalizer=stringalign.normalize.StringNormalizer(case_insensitive=True)
        ),
    )

    return distance - casefolded_distance
