import stringalign
from stringalign.align import levenshtein_distance


def count_case_errors(reference: str, predicted: str) -> int:
    distance = levenshtein_distance(reference, predicted)
    casefolded_distance = levenshtein_distance(
        reference,
        predicted,
        tokenizer=stringalign.tokenize.GraphemeClusterTokenizer(
            post_clustering_normalizer=stringalign.tokenize.StringNormalizer(case_insensitive=True)
        ),
    )

    return distance - casefolded_distance
