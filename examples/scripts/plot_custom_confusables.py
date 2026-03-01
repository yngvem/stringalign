"""
.. _custom_confusables:

Resolving confusables and ligatures with custom lists
-----------------------------------------------------

Some historical documents contain ligatures and symbols that are not a part of Unicode.
To account for that, several projects use Unicode's private use area (e.g. `MUFI <https://www.mufi.info/q.php?p=mufi/home>`_).
Different datasets may also have differing annotation guidelines, e.g. regarding how to annotate archaic ligatures.
Many of these transcription differences can be resolved by resolving a task-specific list of :ref:`confusables <confusables>`.
"""

import stringalign
from stringalign.evaluate import AlignmentAnalyzer

# %%
# Input data
# ----------
#
# We examine a sentence from the IMPACT Dataset :cite:p:`10.1145/2501115.2501130`.
# Specifically, we select a line from the sample with PRIMA ID 00046895.
# We also use a predicted line from a Tesseract model trained on the GT4Hist dataset :cite:p:`Springmann_Reul_Dipper_Baiter_2018` [1]_
# This particular example is originally used in :cite:p:`neudecker2021survey`.

reference = "eingerien /  viel guter Leu⸗"
predicted = "eingeriſſan/ ſich viel guter Leü⸗"
print(f"Reference: {reference}")
print(f"Predicted: {predicted}")

# %%
# Compute the CER without resolving confusables
# ---------------------------------------------
tokenizer_default = stringalign.tokenize.GraphemeClusterTokenizer()

alignment_analyzer_default = AlignmentAnalyzer.from_strings(reference, predicted, tokenizer=tokenizer_default)

cer_default = alignment_analyzer_default.compute_ter()
print(f"The character error rate (without resolving comfusables) is {cer_default:.2f}")

# %%
# Setup confusable mapping
# ------------------------
#
# The OCR evaluation tool Dinglehopper has a list of confusables that it resolves by default.
# We have copied that list (with comments) from Dinglehopper's `source code <https://github.com/qurator-spk/dinglehopper/blob/cd68a973cb43ce33790d6f52612a684d933a31e4/src/dinglehopper/extracted_text.py>`_ [2]_.
confusable_map = {
    "": "ſſ",
    "\ueba7": "ſſi",  # MUFI: LATIN SMALL LIGATURE LONG S LONG S I
    "": "ch",
    "": "ck",
    "": "ll",
    "": "ſi",
    "": "ſt",
    "ﬁ": "fi",
    "ﬀ": "ff",
    "ﬂ": "fl",
    "ﬃ": "ffi",
    "": "ct",
    "": "tz",  # MUFI: LATIN SMALL LIGATURE TZ
    "\uf532": "as",  # eMOP: Latin small ligature as
    "\uf533": "is",  # eMOP: Latin small ligature is
    "\uf534": "us",  # eMOP: Latin small ligature us
    "\uf535": "Qu",  # eMOP: Latin ligature capital Q small u
    "ĳ": "ij",  # U+0133 LATIN SMALL LIGATURE IJ
    "\ue8bf": "q&",
    # MUFI: LATIN SMALL LETTER Q LIGATED WITH FINAL ET
    # XXX How to replace this correctly?
    "\ueba5": "ſp",  # MUFI: LATIN SMALL LIGATURE LONG S P
    "ﬆ": "st",  # U+FB06 LATIN SMALL LIGATURE ST
} | {
    "": "ü",
    "": "ä",
    "==": "–",  # → en-dash
    "—": "–",  # em-dash → en-dash
    "": "ö",
    "’": "'",
    "⸗": "-",
    "aͤ": "ä",  # LATIN SMALL LETTER A, COMBINING LATIN SMALL LETTER E
    "oͤ": "ö",  # LATIN SMALL LETTER O, COMBINING LATIN SMALL LETTER E
    "uͤ": "ü",  # LATIN SMALL LETTER U, COMBINING LATIN SMALL LETTER E
    "\uf50e": "q́",  # U+F50E LATIN SMALL LETTER Q WITH ACUTE ACCENT
}

# %%
# Compute the CER while resolving confusables
# -------------------------------------------
tokenizer_confusables = stringalign.tokenize.GraphemeClusterTokenizer(
    pre_tokenization_normalizer=stringalign.normalize.StringNormalizer(resolve_confusables=confusable_map)
)

alignment_analyzer_confusables = AlignmentAnalyzer.from_strings(reference, predicted, tokenizer=tokenizer_confusables)

cer_confusables = alignment_analyzer_confusables.compute_ter()
print(f"The character error rate (after resolving confusables) is {cer_confusables:.2f}")

# %%
# Look at strings after resolving confusables
# -------------------------------------------
print("Reference:")
print(f"without resolving confusables and tokenizing: {tokenizer_default(reference)}")
print(f"  after resolving confusables and tokenizing: {tokenizer_confusables(reference)}")

print("Predicted:")
print(f"without resolving confusables and tokenizing: {tokenizer_default(predicted)}")
print(f"  after resolving confusables and tokenizing: {tokenizer_confusables(predicted)}")


# %%
# .. rubric:: Footnotes
#
# .. [1] The full reference and predicted text is available in the GitHub repo of :cite:p:`neudecker2021survey`: https://github.com/cneud/hip21_ocrevaluation/tree/main/data
# .. [2] Note that Dinglehopper uses an Apache 2.0 license, which is why we can copy it here. Dinglehopper's License text is available in Stringalign's GitHub repository.
