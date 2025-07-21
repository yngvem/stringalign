from pathlib import Path

import PIL
from stringalign.visualize import base64_encode_image, create_html_image


def test_width_is_used():
    """The provided width is used in the image tag"""
    with PIL.Image.open(Path(__file__).with_name("data") / "stringalign_test.jpg") as img:
        html_img = create_html_image(img, width=123)

    assert 'width="123px"' in html_img


def test_alt_is_used():
    """The provided alt is used in the image tag"""
    with PIL.Image.open(Path(__file__).with_name("data") / "stringalign_test.jpg") as img:
        html_img = create_html_image(img, alt="description")

    assert 'alt="description"' in html_img


def test_no_alt_attribute_if_no_alt():
    """If no alt text is provided, there is no alt attribute in the img tag"""
    with PIL.Image.open(Path(__file__).with_name("data") / "stringalign_test.jpg") as img:
        html_img = create_html_image(img)

    assert "alt=" not in html_img


def test_b64_in_img_tag():
    """The img tag includes base64 encoded image"""
    with PIL.Image.open(Path(__file__).with_name("data") / "stringalign_test.jpg") as img:
        base64_img = base64_encode_image(img).decode("ascii")
        html_img = create_html_image(img)

    assert f'src="data:image/jpeg;base64, {base64_img}"' in html_img
