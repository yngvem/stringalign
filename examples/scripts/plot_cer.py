"""
.. _cer_example:

Computing the CER and WER
=========================

This example shows how to compute the character error rate (CER) and word error rate (WER) with Stringalign and how the choice of tokenizer can be important.
"""

import stringalign

# %%
# One way to measure the performance of a predicted text transcription compared to a reference is by calculating the character error rate (CER) and word error rate (WER) which are special cases of the token error rate (TER) (For more details on these metrics see :ref:`token_error_rate`).
# To calculate the CER between two strings we first need a character-level tokenizer which we use to get an alignment that we can use to compare the strings.
from stringalign.evaluate import AlignmentAnalyzer

reference = "Ηello world!"
predicted = "Hello world!!"

tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()
alignment_analyzer = AlignmentAnalyzer.from_strings(reference, predicted, tokenizer=tokenizer)

cer = alignment_analyzer.compute_ter()

print(f"The character error rate is {cer:.2f}")

# %%
# You might notice that this number is twice what we may expect.
# We can visualise the alignment to understand why.

alignment_analyzer.visualize()

# %%
# We see that there was a :ref:`confusable character <confusables>` used for the ``H``, and the benefit of this
# way of computing the CER and WER is that the tokenizer is explicit.
# If we want to resolve confusables, then we can switch out the tokenizer.

reference = "Ηello world!"
predicted = "Hello world!!"

# Resolve confusables before tokenization
normalizer = stringalign.normalize.StringNormalizer(resolve_confusables="intentional")
tokenizer = stringalign.tokenize.GraphemeClusterTokenizer(pre_tokenization_normalizer=normalizer)

alignment_analyzer = AlignmentAnalyzer.from_strings(reference, predicted, tokenizer=tokenizer)
cer = alignment_analyzer.compute_ter()

print(f"The character error rate is {cer:.2f}")

alignment_analyzer.visualize()

# %%
# Computing the word error rate
# -----------------------------
#
# Similarly, if we want to compute the word error rate, we can switch out the tokenizer, and, for example,
# use whitespace characters to signify word boundaries.


reference = "Ηello world!"
predicted = "Hello world!!"

# Resolve confusables before tokenization
normalizer = stringalign.normalize.StringNormalizer(resolve_confusables="intentional")
word_tokenizer = stringalign.tokenize.SplitAtWhitespaceTokenizer(pre_tokenization_normalizer=normalizer)

alignment_analyzer = AlignmentAnalyzer.from_strings(reference, predicted, tokenizer=word_tokenizer)
wer = alignment_analyzer.compute_ter()

print(f"The word error rate is {wer:.2f}")
alignment_analyzer.visualize(space_alignment_ops=True)  # Space alignment ops to add whitespace around each word

# %%
# Using different word tokenizers
# -------------------------------
#
# Sometimes, we may not be too interested in how punctuation affects model performance.
# In those cases, we can, for example, use the :class:`stringalign.tokenize.UnicodeWordTokenizer`, which uses the
# word extraction algorithm described in :cite:p:`unicode-annex-29` to tokenize the strings into words without punctuation.

reference = "Ηello world!"
predicted = "Hello world!!"

# Resolve confusables before tokenization
normalizer = stringalign.normalize.StringNormalizer(resolve_confusables="intentional")
unicode_word_tokenizer = stringalign.tokenize.UnicodeWordTokenizer(pre_tokenization_normalizer=normalizer)

alignment_analyzer = AlignmentAnalyzer.from_strings(reference, predicted, tokenizer=unicode_word_tokenizer)
unicode_word_wer = alignment_analyzer.compute_ter()

print(f"The word error rate with a SplitAtWhitespaceTokenizer is: {wer:.2f}")
print(f"The word error rate with a UnicodeWordTokenizer is:       {unicode_word_wer:.2f}")
alignment_analyzer.visualize(space_alignment_ops=True)  # Space alignment ops to add whitespace around each word

# %%
# Convenience functions
# ---------------------
#
# Generally, it is good practice to explicitly define your tokenizer before calculating the CER or WER.
# Afterall, before looking at the CER you should have an idea of what you mean by "character" for your particular problem.
# However, stringalign also supports three convinence functions for quickly calculating CER, WER and TER:
# :func:`stringalign.evaluate.compute_cer`, :func:`stringalign.evaluate.compute_wer` and :func:`stringalign.evaluate.compute_ter`.
# These functions will use sensible defaults and return the :class:`stringalign.evaluate.AlignmentAnalyzer` used for the calculation.
# To ensure reproducibility, you can inspect the returned analyzer and note the tokenization and normalization.

cer, cer_analyzer = stringalign.evaluate.compute_cer(reference, predicted)
wer, wer_analyzer = stringalign.evaluate.compute_wer(reference, predicted)

print(f"The CER is {cer}")
print(f"We used this analyzer to compute the CER: {cer_analyzer}")
print()
print(f"The WER is {wer}")
print(f"We used this analyzer to compute the WER: {wer_analyzer}")

# %%
# Evaluating multiple strings
# ---------------------------
# We can also evaluate multiple strings at once.
# The most obvious way to do that might be to compute the CER for each sample and take an average.
# However, that approach would put artificially high weight on characters in short strings.
# Instead, we want to compute the total number of insertions, deletions, substitutions and reference tokens across all strings, and then compute the error rates using the equations defined in :ref:`token_error_rate`.
# To do that in Stringalign, we create a :class:`stringalign.evaluate.MultiAlignmentAnalyzer`
from stringalign.evaluate import MultiAlignmentAnalyzer

references = ["Ηello world!", "Goodbye for now :)"]
predictions = ["Hello world!!", "Godbye for now!"]

# Resolve confusables before tokenization
normalizer = stringalign.normalize.StringNormalizer(resolve_confusables="intentional")
tokenizer = stringalign.tokenize.GraphemeClusterTokenizer(pre_tokenization_normalizer=normalizer)

multi_alignment_analyzer = MultiAlignmentAnalyzer.from_strings(references, predictions, tokenizer=tokenizer)
cer = multi_alignment_analyzer.compute_ter()

print(f"The overall CER for this dataset is {cer}")
