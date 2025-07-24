import base64
import io
from pathlib import Path

import PIL.Image
from stringalign.visualize import base64_encode_image


def test_encoded_img_can_be_decoded():
    """Decoding an encoded image should be readable by Pillow"""
    with PIL.Image.open(Path(__file__).with_name("data") / "stringalign_test.jpg") as img:
        base64_img = base64_encode_image(img)

    decoded_img = base64.b64decode(base64_img)
    buffer = io.BytesIO(decoded_img)
    PIL.Image.open(buffer)
