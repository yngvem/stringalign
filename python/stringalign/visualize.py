from __future__ import annotations

import base64
import html
import io
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import PIL.Image

    from stringalign.align import AlignmentTuple


def compress_css(css):
    """Simple compression of css that turns all whitespace into a single space.

    This will remove newlines, tabs, and multiple spaces, (somewhat similar to minification, but not as thorough)
    """
    compressed_css = " ".join(css.split())
    return compressed_css


def create_alignment_stylesheet(space_tokens: bool) -> str:
    stylesheet = compress_css((Path(__file__).with_name("assets") / "stylesheet.css").read_text())
    if space_tokens:
        stylesheet += "\n.alignment-chunk { margin-left: 0.5em; }\n"

    return stylesheet


def _create_alignment_html(
    alignment: AlignmentTuple, reference_label: str = "Reference:", predicted_label: str = "Predicted:"
) -> str:
    alignment_html = ['<div class="alignment">']

    alignment_html.append('<div class="alignment-labels">')
    alignment_html.append(f'<span class="reference label">{html.escape(reference_label)}</span>')
    alignment_html.append(f'<span class="predicted label">{html.escape(predicted_label)}</span>')
    alignment_html.append("</div>")
    for operation in alignment:
        reference, predicted = operation.to_html()

        alignment_chunk_html = "<div class='alignment-chunk'>"
        alignment_chunk_html += f"{reference} {predicted}"
        alignment_chunk_html += "</div>"

        alignment_html.append(alignment_chunk_html)

    alignment_html.append("</div>")
    return "".join(alignment_html)


def create_alignment_html(
    alignment: AlignmentTuple,
    reference_label: str = "Reference:",
    predicted_label: str = "Predicted:",
    stylesheet: str | None = None,
    space_tokens: bool = False,
) -> str:
    """Create an HTML representation of the alignment with embedded CSS styles.

    Arguments:
    ----------
    alignment:
        The alignment data to visualize.
    reference_label:
        The label for the reference text.
    predicted_label:
        The label for the predicted text.
    stylesheet:
        Optional CSS stylesheet to apply. If None, a default stylesheet is used. For no styling, pass an empty string.

    Returns:
    --------
    str:
        An HTML string representing the alignment with embedded styles.
    """
    if stylesheet is None:
        stylesheet = create_alignment_stylesheet(space_tokens=space_tokens)

    if stylesheet:
        style = f"<style>{stylesheet}</style>"
    else:
        style = ""

    alignment_html = _create_alignment_html(
        alignment=alignment,
        reference_label=reference_label,
        predicted_label=predicted_label,
    )
    return style + alignment_html


def base64_encode_image(image: PIL.Image.Image) -> bytes:
    """Convert a PIL image into a base64-encoded JPEG image."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue())


def create_html_image(image: PIL.Image.Image | Path | str, width=500, alt=None) -> str:
    """Convert a PIL image into a HTML image tag with a base64-encoded JPEG image to e.g. embed in Jupyter notebooks."""
    if alt is None:
        alt = ""
    else:
        alt = f'alt="{alt}"'

    if isinstance(image, Path | str):
        file_type = Path(image).suffix.removeprefix(".")
        with open(image, "rb") as file:
            bytes_img = file.read()
            b64_img = base64.b64encode(bytes_img)
    else:
        try:
            b64_img = base64_encode_image(image)
        except Exception as e:
            raise TypeError(f"Image must be PIL.Image.Image, Path or string, not {type(image)}") from e
        else:
            file_type = "jpeg"

    # JPG is not a valid MIME type, so if the file type is .jpg, we need to convert it to .jpeg
    if file_type == "jpg":
        file_type = "jpeg"

    return f'<img src="data:image/{file_type};base64, {b64_img.decode("ascii")}" width="{width}px" {alt}/>'
