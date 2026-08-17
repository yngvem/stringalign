from stringalign.visualize import HtmlString


def test_returns_htmlstring():
    assert isinstance(HtmlString("a") + HtmlString("b"), HtmlString)
