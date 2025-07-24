from stringalign.visualize import HtmlString


def test__repr__():
    """The HtmlString returns itself when calling _repr_html_."""
    html_string = HtmlString("test")
    assert repr(html_string) == "HtmlString('test')"
