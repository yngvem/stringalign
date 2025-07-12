from collections import Counter

from stringalign.align import align_strings
from stringalign.statistics import StringConfusionMatrix


def test_confusion_matrix_is_sum_of_confusion_matrices() -> None:
    references = ["abcbaa", "xyz"]
    predictions = ["acdeai", "xyy"]
    alignment1 = align_strings(references[0], predictions[0])[0]
    alignment2 = align_strings(references[1], predictions[1])[0]

    result1 = StringConfusionMatrix.from_string_collections(references, predictions)

    result2 = StringConfusionMatrix.from_strings_and_alignment(
        references[0], predictions[0], alignment1
    ) + StringConfusionMatrix.from_strings_and_alignment(references[1], predictions[1], alignment2)

    assert result1 == result2
