"""
.. _most_common_errors_example:

Exploring common errors in a transcription
==========================================

It is often interesting to not only look at the rate of errors but also at what types of errors a model makes. Such exploration can reveal patterns in errors which can, for example, give insights into how to improve the performance of the model.
This example will show how to use Stringalign to quickly get an overview of the top 10 most common errors in a transcription.
We start by loading some toy data based on an excerpt from a digitized copy of `Lærebog i de forskjellige Grene af Huusholdningen <https://www.nb.no/items/URN:NBN:no-nb_digibok_2009111210001>`_ by Hanna Winsnes (1846).
"""

from pathlib import Path

import stringalign
from stringalign.visualize import HtmlString, create_html_image

data_path = Path("synthetic_transcription_data")
predictions_path = data_path / "predicted.txt"
reference_path = data_path / "reference.txt"

predictions = predictions_path.read_text().splitlines()
references = reference_path.read_text().splitlines()
image_paths = data_path.glob("line*.jpg")
metadata = [{"image_path": data_path / f"line{line_num:02d}.jpg"} for line_num in range(14)]


# %%
# After loading the data, we can create a :class:`stringalign.evaluate.MultiAlignmentAnalyzer` which aligns all reference/prediction-pairs and makes it easy for us to explore common transcription errors.
analyzer = stringalign.evaluate.MultiAlignmentAnalyzer.from_strings(
    predictions=predictions,
    references=references,
    metadata=metadata,
)

# %%
# We start by looking at the ``raw`` edit counts, which corresponds to single-token alignment operations.

counts = analyzer.edit_counts["raw"]
for operation, count in counts.most_common(10):
    print(f"{operation:21}: {count}")

# %%
# We see that the most common transcription error is converting ``s`` to ``f``.
# We also see three ``æ -> a`` replacements and and insertions of ``e``.
# It can also be useful to consider combined edit operation counts, as that allows us to find common multi-token replacements, insertions and deletions.

counts = analyzer.edit_counts["combined"]
for operation, count in counts.most_common(10):
    print(f"{operation:21}: {count}")

# %%
# When we inspect the combined edit operation counts, we see that there are some common two-token replacements, such as ``æ -> ae``, ``rn -> m`` and ``m -> nn``.
#
# Visualising the alignments
# --------------------------
#
# It can also be useful to visualise the data to get a better understanding of why the model makes the mistakes it does.
# In particular, we can use the :meth:`MultiAlignmentAnalyzer.alignment_operator_index <stringalign.evaluate.MultiAlignmentAnalyzer.alignment_operator_index>` method to iterate over the :class:`AlignmentAnalyzer <stringalign.evaluate.AlignmentAnalyzer>` instances that contain transcriptions with a specified edit.

most_common_error = counts.most_common(1)[0][0]

# We create a long HTML string to display the visualisation in Sphinx.
# If you're using Jupyter, then you can use ``IPython.display.display`` in each iteration instead.
table_html = ""
for line_analyzer in analyzer.alignment_operator_index["combined"][most_common_error]:
    image_html = create_html_image(line_analyzer.metadata["image_path"])
    alignment_html = line_analyzer.visualize(which="combined")
    table_html += image_html + alignment_html

HtmlString(table_html)

# %%
# We see that the OCR-model struggles particularly with the long s of the Fraktur typeface, so a natural step to improve performance could be to train a model with more Fraktur text.
