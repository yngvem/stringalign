from unittest.mock import create_autospec

import pytest
import stringalign
from stringalign.evaluation import LineError


def test_visualize_calls_create_html(monkeypatch: pytest.MonkeyPatch) -> None:
    """The visualize method should call create_html with the correct arguments."""
    line_error = LineError.from_strings("Hello, world!", "Hallo, word?", tokenizer=None)

    mock_function = create_autospec(
        stringalign.visualize.create_alignment_html, return_value='<div class="alignment">Mocked HTML</div>'
    )
    monkeypatch.setattr(stringalign.evaluation, "create_alignment_html", mock_function)

    out_html = line_error.visualize(which="raw", space_tokens=True)
    mock_function.assert_called_once_with(
        alignment=line_error.raw_alignment,
        space_tokens=True,
    )
    assert out_html == '<div class="alignment">Mocked HTML</div>'
