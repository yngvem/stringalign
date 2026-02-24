"""
Toy emoji OCR example
=====================

This example demonstrates how Stringalign accurately computes evaluation metrics even for complex inputs like emojis,
where other tools may return misleading results by default.

The default behaviour of, for example, Jiwer is not to cluster based on grapheme clusters, so if we compute the CER for strings
with ZWJ-emoji sequences, we can get surprising results
"""

import io
import json
from pathlib import Path

import jiwer
import PIL.Image
import stringalign

jiwer_cer = jiwer.cer("🐈‍⬛", "🐦‍⬛")
stringalign_cer, _analyzer = stringalign.evaluate.compute_cer("🐈‍⬛", "🐦‍⬛")
print("Jiwer:", jiwer_cer)
print("Stringalign:", stringalign_cer)

# %%
# We see that Jiwer gets only 1/3 CER, even though 100% of the characters are wrong.
# This artificially low error is caused by Jiwer tokenizing (and therefore aligning) based on code points, so 🐈‍⬛ and 🐦‍⬛will be treated as 🐈‍[ZWJ]⬛ and 🐦‍[ZWJ]⬛.
# Stringalign on the other hand, tokenizes based on grapheme clusters so 🐈‍⬛ and 🐦‍⬛ are correctly treated as two emojis and not six code points.  (See :ref:`grapheme_clusters` for an introduction to grapheme clusters).

# %%
# Lets see how we can use Stringalign to accurately calculate the CER for a synthetic dataset with some toy
# OCR transcriptions containing emojis.
import io
import json
from pathlib import Path

import PIL.Image
import stringalign


def load_image(path: Path | str) -> PIL.Image.Image:
    path = data_path / path
    return PIL.Image.open(io.BytesIO(path.read_bytes()))


data_path = Path("emoji_ocr_evaluation_data")
dataset = json.loads((data_path / "lines.json").read_text())

# %%
# Look at one sample
# ------------------

print(f"Gold standard:\n{dataset['samples'][0]['gold_standard']}\n")
print(f"Transcription:\n{dataset['samples'][0]['transcription']}\n")
load_image(dataset["samples"][0]["image"])

# %%
# Evaluate transcriptions
# -----------------------

references = [sample["gold_standard"] for sample in dataset["samples"]]
predictions = [sample["transcription"] for sample in dataset["samples"]]

tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()  # This is the default, but it's still nice to be explicit
evaluator = stringalign.evaluate.MultiAlignmentAnalyzer.from_strings(
    references=references, predictions=predictions, tokenizer=tokenizer
)

cer = evaluator.confusion_matrix.compute_token_error_rate()
print(f"The overall CER is {cer}")

# %%
# Look at the performance for the different lines
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

for alignment_error in evaluator.alignment_analyzers:
    sample_cer = alignment_error.confusion_matrix.compute_token_error_rate()
    jiwer_cer = jiwer.cer(alignment_error.reference, alignment_error.predicted)

    print(f"Reference:\n{alignment_error.reference}\n")
    print(f"Predicted:\n{alignment_error.predicted}\n")
    print(f"CER: {sample_cer:3.2%}, Jiwer CER: {jiwer_cer:3.2%}\n\n")

# %%
# We see that stringalign computes CER correctly, even for emojis.
