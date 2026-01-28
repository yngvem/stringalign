from stringalign.evaluation import MultiAlignmentAnalyzer


def test_with_example():
    evaluator = MultiAlignmentAnalyzer.from_strings(
        references=["abc", "def", "aa"], predictions=["abbc", "dgf", "abb"], metadata=[{"id": 0}, {"id": 1}, None]
    )
    expected = [
        {
            "reference": "abc",
            "predicted": "abbc",
            "horisontal_segmentation_error": False,
            "token_duplication_error": True,
            "removed_duplicate_token_error": False,
            "diacritic_error": False,
            "confusable_error": False,
            "case_error": False,
            "id": 0,
        },
        {
            "reference": "def",
            "predicted": "dgf",
            "horisontal_segmentation_error": False,
            "token_duplication_error": False,
            "removed_duplicate_token_error": False,
            "diacritic_error": False,
            "confusable_error": False,
            "case_error": False,
            "id": 1,
        },
        {
            "reference": "aa",
            "predicted": "abb",
            "horisontal_segmentation_error": True,
            "token_duplication_error": False,
            "removed_duplicate_token_error": False,
            "diacritic_error": False,
            "confusable_error": False,
            "case_error": False,
        },
    ]
    assert evaluator.dump() == expected
