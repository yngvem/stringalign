"""
.. _randomised_alignments_example:

Uncertainty metrics for token-specific statistics
=================================================

This is a simple example that demonstrates how to estimate the uncertainty for token-specific metrics (see :ref:`sequence_alignment` for more information about how these can occur).
We use the same toy dataset here as in :ref:`most_common_errors_example`.
"""

from collections import Counter
from pathlib import Path

import numpy as np
import stringalign

data_path = Path("synthetic_transcription_data")
predictions_path = data_path / "predicted.txt"
reference_path = data_path / "reference.txt"

predictions = predictions_path.read_text().splitlines()
references = reference_path.read_text().splitlines()
image_paths = data_path.glob("line*.jpg")

# %%
# Normally, when we evaluate token-specific statistics, we would create a :class:`MultiAlignmentAnalyzer <stringalign.evaluation.MultiAlignmentAnalyzer>`.
# However, now, we want to get uncertainty metrics on the different edit operations.
# To get those, we need many :class:`MultiAlignmentAnalyzer <stringalign.evaluation.MultiAlignmentAnalyzer>` instances that use randomised alignments with different random seeds.

analyzers = [
    stringalign.evaluation.MultiAlignmentAnalyzer.from_strings(
        references=references,
        predictions=predictions,
        randomize_alignment=True,
        random_state=i,
    )
    for i in range(10)
]

# %%
# After creating the alignment analyzers, we find the set of all edit operations that occur in at least one alignment and use that to get lists of edit operation counts.

all_edit_operations = {edit_op for analyzer in analyzers for edit_op in analyzer.edit_counts["raw"]}
edit_operation_counts = {
    edit_op: [analyzer.edit_counts["raw"][edit_op] for analyzer in analyzers] for edit_op in all_edit_operations
}

# %%
# Now that we have a dictionary that maps the edit operations to their count in each of the random alignments, we can compute their mean and standard deviation.

edit_operation_averages = Counter({edit_op: np.mean(counts) for edit_op, counts in edit_operation_counts.items()})
edit_operation_stddev = {edit_op: np.std(counts) for edit_op, counts in edit_operation_counts.items()}

for edit_op, count in edit_operation_averages.most_common(10):
    stddev = edit_operation_stddev[edit_op]
    print(f"{edit_op:19s}: {count:5.2f} +- {stddev:.2f}")

# %%
# We see that in this case, there was no uncertainty in the most common errors, and even then, the uncertainty was not too large.
# This type of uncertainty analysis can be very useful when, e.g. comparing different transcription models on token-specific metrics.
