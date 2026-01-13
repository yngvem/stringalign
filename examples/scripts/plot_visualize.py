"""
.. _visualize_example:

Visualizing alignments
======================

Visualizing the alignment of the predicted and reference string is good way to gain some insight beyond summarized metrics.
To aid this type of analysis, Stringalign has functionality to quickly display a lightweight visualization of an alignment.
"""

import stringalign
from stringalign.evaluation import AlignmentAnalyzer

reference = "Hello world!"
predicted = "Hello w0rld!!"

tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()
analyzer = AlignmentAnalyzer.from_strings(reference=reference, predicted=predicted, tokenizer=tokenizer)
analyzer.visualize()

# %%
# .. sidebar::
#
#     :meth:`stringalign.evaluation.AlignmentAnalyzer.visualize` returns a :class:`stringalign.visualize.HtmlString`.
#     This class inherits from the builtin :class:`str`-class, but its contents are interpreted as HTML by tools like Jupyter Notebook.
#
# The visualization is based on html and CSS and can easily be displayed in a notebook, in dashboard-frameworks that support html or in a web application.
#
# Sometimes it can be beneficial to add extra spacing between the alignment operation (for example if your tokenizer removes spaces or your text contains non-spacing tokens).
# To add spacing between each token, you can use the ``space_alignment_ops`` flag.

tokenizer = stringalign.tokenize.SplitAtWhitespaceTokenizer()
analyzer = AlignmentAnalyzer.from_strings(reference=reference, predicted=predicted, tokenizer=tokenizer)
analyzer.visualize()

# %%
analyzer.visualize(space_alignment_ops=True)

# %%
# Customize the visualization
# ---------------------------
# The :meth:`stringalign.evaluation.AlignmentAnalyzer.visualize` method is a convenience wrapper around :func:`stringalign.visualize.create_alignment_html`.
# If you want more customization you can use :func:`stringalign.visualize.create_alignment_html` directly. Then you can, for example, change the text labels

stringalign.visualize.create_alignment_html(
    alignment=analyzer.raw_alignment,
    reference_label="Gold standard:",
    predicted_label="Model estimate:",
    space_alignment_ops=True,
)

# %%
# Customize the styling (advanced)
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# You can also supply your own style sheet, which we demonstrate in :ref:`this short example <custom_visualisation_stylesheet>`.
