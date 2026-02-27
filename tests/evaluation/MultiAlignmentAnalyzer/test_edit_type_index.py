from stringalign.evaluate import EditType, MultiAlignmentAnalyzer


def test_index_points_to_correct_analyzer() -> None:
    references = ["Hello!", "Hello!", "Hello!", "Hełlo!", "Hello!", "Hello!"]
    predictions = ["Hello", "Helllo!", "Helo!", "Hello!", "Hel1o!", "HEllo!"]

    multi_alignment_analyzer = MultiAlignmentAnalyzer.from_strings(
        references=references,
        predictions=predictions,
    )

    analyzers = multi_alignment_analyzer.alignment_analyzers
    index = multi_alignment_analyzer.edit_type_index

    # Only the first line has a horisontal segmentation error
    assert list(index[EditType.HORISONTAL_SEGMENTATION_ERROR]) == [analyzers[0]]

    # Only the second line has a token duplication error
    assert list(index[EditType.TOKEN_DUPLICATION_ERROR]) == [analyzers[1]]

    # Only the third line has a removed duplicate token error
    assert list(index[EditType.REMOVED_DUPLICATE_TOKEN_ERROR]) == [analyzers[2]]

    # Only the forth line has a diacritic error
    assert list(index[EditType.DIACRITIC_ERROR]) == [analyzers[3]]

    # Only the fifth line has a confusable error
    assert list(index[EditType.CONFUSABLE_ERROR]) == [analyzers[4]]

    # Only the sixth line has a case error
    assert list(index[EditType.CASE_ERROR]) == [analyzers[5]]
