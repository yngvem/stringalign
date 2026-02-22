from typing import Literal
from unittest.mock import MagicMock, create_autospec

import pytest
import stringalign
from stringalign.align import Kept
from stringalign.evaluate import AlignmentAnalyzer
from stringalign.tokenize import GraphemeClusterTokenizer


def test_visualize_calls_create_html(monkeypatch: pytest.MonkeyPatch) -> None:
    """The visualize method should call create_html with the correct arguments."""
    line_error = AlignmentAnalyzer.from_strings("Hello, world!", "Hallo, word?", tokenizer=None)

    mock_function = create_autospec(
        stringalign.visualize.create_alignment_html, return_value='<div class="alignment">Mocked HTML</div>'
    )
    monkeypatch.setattr(stringalign.visualize, "create_alignment_html", mock_function)

    out_html = line_error.visualize(which="raw", space_alignment_ops=True)
    mock_function.assert_called_once_with(
        alignment=line_error.raw_alignment,
        space_alignment_ops=True,
    )
    assert out_html == '<div class="alignment">Mocked HTML</div>'


@pytest.mark.parametrize("which", ["raw", "combined"])
def test_raw_alignment_is_used(monkeypatch: pytest.MonkeyPatch, which: Literal["raw", "combined"]) -> None:
    mocked = MagicMock()
    monkeypatch.setattr(stringalign.visualize, "create_alignment_html", mocked)
    ae = AlignmentAnalyzer(
        reference="H",
        predicted="H",
        combined_alignment=(Kept("H"),),
        raw_alignment=(Kept("H"),),
        unique_alignment=True,
        horisontal_segmentation_errors=(),
        token_duplication_errors=(),
        removed_duplicate_token_errors=(),
        diacritic_errors=(),
        confusable_errors=(),
        case_errors=(),
        metadata=None,
        tokenizer=GraphemeClusterTokenizer(),
    )
    alignments_map = {"raw": ae.raw_alignment, "combined": ae.combined_alignment}
    ae.visualize(which=which)
    mocked.assert_called_once_with(alignment=alignments_map[which], space_alignment_ops=False)
