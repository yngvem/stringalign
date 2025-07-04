from pathlib import Path

from stringalign.align import AlignmentTuple


def compress_css(css):
    """Simple compression of css that turns all whitespace into a single space.

    This will remove newlines, tabs, and multiple spaces, (somewhat similar to minification, but not as thorough)
    """
    compressed_css = " ".join(css.split())
    return compressed_css


def create_alignment_stylesheet() -> str:
    return compress_css((Path(__file__).with_name("assets") / "stylesheet.css").read_text())


def _create_alignment_html(
    alignment: AlignmentTuple, reference_label: str = "Reference:", predicted_label: str = "Predicted:"
) -> str:
    alignment_html = '<div class="alignment">'

    reference_html = f"<div>{reference_label} "
    predicted_html = f"<div>{predicted_label} "

    for operation in alignment:
        reference, predicted = operation.to_html()
        reference_html += reference
        predicted_html += predicted

    reference_html += "</div>"
    predicted_html += "</div>"

    alignment_html += reference_html
    alignment_html += predicted_html
    return alignment_html


def create_alignment_html(
    alignment: AlignmentTuple,
    reference_label: str = "Reference:",
    predicted_label: str = "Predicted:",
    stylesheet: str | None = None,
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
        stylesheet = create_alignment_stylesheet()

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
