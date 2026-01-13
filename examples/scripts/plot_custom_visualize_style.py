"""
.. _custom_visualisation_stylesheet:

Customise the alignment visualisation with CSS
==============================================

If you want, then you can change the appearance of the alignment visualisation by applying custom CSS.
This will override the default style sheet completely, so if you want to just update parts of the styling, you should copy the default style sheet, add your updates and then supply the entire updated style sheet.
You can see the the default style sheet by calling :func:`stringalign.visualize.create_alignment_stylesheet`, or by reading the source code on GitHub, `here <https://github.com/yngvem/stringalign/blob/main/python/stringalign/assets/stylesheet.css>`_.
Below is an example where we modify the style sheet to change the colors used, the font size and to use ``*`` instead of ``-`` to signify inserted and deleted tokens.
"""

import stringalign
from stringalign.evaluation import AlignmentAnalyzer

reference = "Hello world!"
predicted = "Helo w0rld!!"

tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()
analyzer = AlignmentAnalyzer.from_strings(reference=reference, predicted=predicted, tokenizer=tokenizer)

css = """

.alignment {
    font-family: monospace;
    text-align: left;
    --kept: #49B6FF;  /* Updated colour */
    --replaced: #CAD49D;  /* Updated colour */
    --inserted: #E6C0E9;  /* Updated colour */
    --neutral: #fff;
    font-size: 24px;  /* Updated font size */
}

.alignment-chunk, .alignment-labels {
    display: inline-block;
    min-width: 1em;
}
.alignment-chunk.spaced {
    margin-left: 0.5em;
}

span.reference, span.predicted {
    white-space: pre;
    display: block;
    text-align: center;
}
.kept.reference, .kept.predicted {
    background-color: var(--kept);
}
.deleted.reference {
    background-color: var(--inserted);
}
.deleted.predicted::after, .inserted.reference::after {
    content: "*";  /* Updated character size */
}
.inserted.predicted {
    background-color: var(--inserted);
}
.replaced.reference, .replaced.predicted{
    background-color: var(--replaced);
}
"""
stringalign.visualize.create_alignment_html(
    alignment=analyzer.raw_alignment,
    reference_label="Gold standard:",
    predicted_label="Model estimate:",
    space_alignment_ops=False,
    stylesheet=css,
)

# %%
# If you want to use the visualization in an existing application with a separate CSS, you can even remove the styling from the html completely and add your own styling separately.
