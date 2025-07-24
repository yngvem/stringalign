from stringalign.visualize import create_alignment_stylesheet


def test_space_tokens_spaces_tokens():
    """When creating stylesheet with spaced tokens, the alignment chunks have a left-margin."""
    stylesheet = create_alignment_stylesheet(space_tokens=True)
    assert ".alignment-chunk { margin-left: 0.5em; }" in stylesheet


def test_no_space_tokens_doesnt_space_tokens():
    """When creating stylesheet without spaced tokens, the alignment chunks have no left-margin."""
    stylesheet = create_alignment_stylesheet(space_tokens=False)
    assert ".alignment-chunk { margin-left: 0.5em; }" not in stylesheet
    assert "margin-left" not in stylesheet
