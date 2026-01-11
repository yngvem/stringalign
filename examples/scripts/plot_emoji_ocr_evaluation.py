"""
Toy emoji OCR example
=====================

This example demonstrates how stringalign correctly computes evaluation metrics even for complex inputs like emojis,
where other tools may return misleading results by default. First let's load in our synthetic dataset with some toy
OCR transcriptions.
"""

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

print("Gold standard:\n", dataset["samples"][0]["gold_standard"], end="\n\n")
print("Transcription:\n", dataset["samples"][0]["transcription"], end="\n\n")
load_image(dataset["samples"][0]["image"])

# %%
# Evaluate transcriptions
# -----------------------

references = [sample["gold_standard"] for sample in dataset["samples"]]
predictions = [sample["transcription"] for sample in dataset["samples"]]

tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()  # This is the default, but it's nice to be explicit
evaluator = stringalign.evaluation.MultiAlignmentAnalyzer.from_strings(
    references=references, predictions=predictions, tokenizer=tokenizer
)

cer = evaluator.confusion_matrix.compute_token_error_rate()
print(f"The overall CER is {cer}")

# %%
# Look at the performance for the different lines
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

for alignment_error in evaluator.alignment_errors:
    sample_cer = alignment_error.confusion_matrix.compute_token_error_rate()

    print(f"Reference:\n{alignment_error.reference}\n")
    print(f"Predicted:\n{alignment_error.predicted}\n")
    print(f"CER: {sample_cer}")

# %%
# We see that the CER and WER is computed correctly, even for emojis. Each emoji counts as just a single character,
# even if it consists of several code points (like how ❤️‍🩹 consists of ❤️[ZWJ]🩹).
#
#
# Jiwer does not compute the CER correctly
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# The default behavioiur of Jiwer is not to cluster based on grapheme clusters, so if we compute the CER for strings
# with ZWJ-emoji sequences, we can get surprising results

import jiwer

jiwer_cer = jiwer.cer("🐈‍⬛", "🐦‍⬛")
stringalign_cer, _analyzer = stringalign.evaluation.compute_cer("🐈‍⬛", "🐦‍⬛")
print("Jiwer:", jiwer_cer)
print("Stringalign:", stringalign_cer)

# %%
# We see that Jiwer gets only 1/3 CER, even though 100% of the characters are wrong. However, since Stringalign knows
# that 🐈‍[ZWJ]⬛ and 🐦‍[ZWJ]⬛ both are single grapheme clusters, it returns the correct CER.
#
# Recreating Jiwer's calculations in stringalign
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
jiwer_tokenizer = stringalign.tokenize.add_join(sep="")(list)
stringalign_jiwer_cer, _analyzer = stringalign.evaluation.compute_ter("🐈‍⬛", "🐦‍⬛", tokenizer=jiwer_tokenizer)
print("Stringalign mimicking jiwer:", stringalign_jiwer_cer)

# %%
# Visualizing Stringalign's alignment
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
alignment_error = stringalign.evaluation.AlignmentAnalyzer.from_strings(
    "🐈‍⬛",
    "🐦‍⬛",
    tokenizer=tokenizer,
)
alignment_error.visualize()

# %%
# Visualizing Jiwer's alignment
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
alignment_error = stringalign.evaluation.AlignmentAnalyzer.from_strings(
    "🐈‍⬛",
    "🐦‍⬛",
    tokenizer=jiwer_tokenizer,
)
alignment_error.visualize()


# TODO: Si noe om hvordan dette kan påvirke vekting i CER
