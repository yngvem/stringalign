from stringalign.align import Deleted, Inserted, Kept, Replaced, align_strings
from stringalign.visualize import create_alignment_html, create_alignment_stylesheet


def test_empty_stylesheet_no_style_tag():
    """If the stylesheet given is an empty string, no style tag should be present in the HTML."""
    alignment, _unique = align_strings("Hei på deg", "Hade på badet")
    html = create_alignment_html(alignment, stylesheet="")
    assert "<style>" not in html


def test_none_stylesheet_default_style_is_used():
    """If the stylesheet is None, the default style should be used."""
    alignment, _unique = align_strings("Hei på deg", "Hade på badet")
    html = create_alignment_html(alignment, stylesheet=None)
    stylesheet = create_alignment_stylesheet()
    assert "<style>" in html
    assert stylesheet in html


def test_provided_stylesheet_is_used():
    """If a stylesheet is provided, it should be used in the HTML."""
    alignment, _unique = align_strings("Hei på deg", "Hade på badet")
    stylesheet = ".alignment {font-size: 42px; font-weight: bold; color: red; font-family: serif;}"
    html = create_alignment_html(alignment, stylesheet=stylesheet)
    assert "<style>" in html
    assert stylesheet in html


def test_correct_number_of_span_tags():
    """The correct number of span tags should be present in the HTML."""
    alignment, _unique = align_strings("Hei på deg", "Hade på badet")
    html = create_alignment_html(alignment)
    assert html.count("<span") == 2 * len(alignment)


def test_correct_number_of_kept_tags():
    """The correct number of tags with class 'kept' should be present in the HTML."""
    alignment, _unique = align_strings("Hei på deg", "Hade på badet")
    html = create_alignment_html(alignment)
    assert html.count('class="kept') == 2 * len([op for op in alignment if isinstance(op, Kept)])


def test_correct_number_of_deleted_tags():
    """The correct number of tags with class 'deleted' should be present in the HTML."""
    alignment, _unique = align_strings("Hei på deg", "Hade på badet")
    html = create_alignment_html(alignment)
    assert html.count('class="deleted') == 2 * len([op for op in alignment if isinstance(op, Deleted)])


def test_correct_number_of_inserted_tags():
    """The correct number of tags with class 'inserted' should be present in the HTML."""
    alignment, _unique = align_strings("Hei på deg", "Hade på badet")
    html = create_alignment_html(alignment)
    assert html.count('class="inserted') == 2 * len([op for op in alignment if isinstance(op, Inserted)])


def test_correct_number_of_replaced_tags():
    """The correct number of tags with class 'replaced' should be present in the HTML."""
    alignment, _unique = align_strings("Hei på deg", "Hade på badet")
    html = create_alignment_html(alignment)
    assert html.count('class="replaced') == 2 * len([op for op in alignment if isinstance(op, Replaced)])
