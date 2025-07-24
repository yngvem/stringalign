from stringalign.visualize import HtmlString


def test_identity():
    """The HtmlString returns itself when calling _repr_html_."""
    html_string = HtmlString("test")
    assert html_string._repr_html_() == html_string
