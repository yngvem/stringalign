from pathlib import Path

import PIL
import pytest
from stringalign.visualize import base64_encode_image, create_html_image


def test_width_is_used() -> None:
    """The provided width is used in the image tag"""
    with PIL.Image.open(Path(__file__).with_name("data") / "stringalign_test.jpg") as img:
        html_img = create_html_image(img, width=123)

    assert 'width="123px"' in html_img


def test_alt_is_used() -> None:
    """The provided alt is used in the image tag"""
    with PIL.Image.open(Path(__file__).with_name("data") / "stringalign_test.jpg") as img:
        html_img = create_html_image(img, alt="description")

    assert 'alt="description"' in html_img


def test_no_alt_attribute_if_no_alt():
    """If no alt text is provided, there is no alt attribute in the img tag"""
    with PIL.Image.open(Path(__file__).with_name("data") / "stringalign_test.jpg") as img:
        html_img = create_html_image(img)

    assert "alt=" not in html_img


def test_b64_in_img_tag() -> None:
    """The img tag includes base64 encoded image"""
    with PIL.Image.open(Path(__file__).with_name("data") / "stringalign_test.jpg") as img:
        base64_img = base64_encode_image(img).decode("ascii")
        html_img = create_html_image(img)

    assert f'src="data:image/jpeg;base64, {base64_img}"' in html_img


def test_file_path() -> None:
    """Input can be a file path"""
    file_path = Path(__file__).with_name("data") / "stringalign_test.jpg"
    html_img = create_html_image(file_path)

    assert 'src="data:image/jpeg;base64,' in html_img


def test_file_path_string() -> None:
    """Input can be a file path as a string"""
    file_path = str(Path(__file__).with_name("data") / "stringalign_test.jpg")
    html_img = create_html_image(file_path)

    assert 'src="data:image/jpeg;base64,' in html_img


@pytest.mark.parametrize("not_a_file", [42, 3.14, None, [], {}, set()])
def test_non_file_object_raises_type_error(not_a_file) -> None:
    """Non-file objects raise a TypeError"""
    with pytest.raises(TypeError):
        create_html_image(not_a_file)


def test_jpg_is_handled_as_jpeg_mime_type() -> None:
    """jpg file ending is handled as jpeg mime type"""
    file_path = Path(__file__).with_name("data") / "stringalign_test.jpg"
    html_img = create_html_image(file_path)

    assert 'src="data:image/jpeg;base64,' in html_img


def test_png_file_has_png_mime_type() -> None:
    """png file ending is handled as png mime type"""
    file_path = Path(__file__).with_name("data") / "stringalign_test.png"
    html_img = create_html_image(file_path)

    assert 'src="data:image/png;base64,' in html_img
