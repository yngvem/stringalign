"""
Computing the CER and WER
=========================

This example demonstrates how to compute the CER and WER with Stringalign and how choosing the correct tokenizer can be important.
"""

import stringalign

# %%
# The best way of comparing two strings with StringAlign is with the :class:`stringalign.evaluation.AlignmentAnalyzer`.
# This class provides a collection of utilities that makes it easy to compare two strings and investigate what their
# differences are.
#
# One way to measure the performance of a predicted text transcription compared to a reference is by calculating the character error rate (CER) and word error rate (WER) which are special cases of the token error rate (TER) (For more details on these metrics see :ref:`_token_error_rate`).
# To calculate the CER between two strings we first need a chracter-level tokenizer which we use to get an aligmment that we can use to compare the strings.
#
# .. sidebar::
#
#    Stringalign also has a couple of convenience functions for computing the CER and WER with a single function call:
#    :func:`stringalign.align.compute_cer` and :func:`stringalign.align.compute_wer`.
#    These are intended for prototyping and data exploration, and we reccomend that the methods we describe here are used
#    for more in-depth data analysis.
from stringalign.evaluation import AlignmentAnalyzer

reference = "Ηello world!"
predicted = "Hello world!!"

tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()
alignment_analyzer = AlignmentAnalyzer.from_strings(reference, predicted, tokenizer=tokenizer)

cer = alignment_analyzer.compute_ter()

print(f"The character error rate is {cer:.2f}")

# %%
# If you're VÅKEN, then you might notice that this number is twice what we may expect.
# We can visualise the alignment to understand why.

alignment_analyzer.visualize()

# %%
# We see that there was a :ref:`confusable character <_confusables>` used for the ``H``, and the benefit of this
# way of computing the CER and WER is that the tokenizer is explicit.
# If we want to resolve confusables, then we just need to switch out the tokenizer.

# TODO: GAMMEL
# The benefit of this approach is that the tokenizer is explicit.
# If we, for example, want the tokenizer to resolve confusables :ref:`confusable characters <_confusables>` we can specify this like so:

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
# Similarly, if we want to compute the word error rate, we just need to switch out the tokenizer, and, for example,
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
# Covenience functions
# --------------------
#
# Generally, it is good practice to explicitly define your tokenizer before calculating the CER or WER.
# Afterall, before looking at the CER you should have an idea of what you mean by "character" for your particular problem.
# However, stringalign also supports three convinence functions for quickly calculating CER, WER and TER:
# :func:`stringalign.evaluate.compute_cer`, :func:`stringalign.evaluate.compute_wer` and :func:`stringalign.evaluate.compute_ter`.
# These functions will use sensible defaults and return the AlignmentAnalyser used for the calculation.
# By inspecting the returned analyser, you can see the tokenization and normalization used to ensure reproducibility.

cer, cer_analyzer = stringalign.evaluation.compute_cer(reference, predicted)
wer, wer_analyzer = stringalign.evaluation.compute_wer(reference, predicted)

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
# Instead, we want to compute the total number of insertions, deletions, substitutions and reference tokens across all strings, and then compute the error rates using the equations defined in :ref:`_token_error_rate`.
# To do that in Stringalign, we create a :class:`stringalign.evaluation.MultiAlignmentAnalyzer`
from stringalign.evaluation import MultiAlignmentAnalyzer

references = ["Ηello world!", "Goodbye for now :)"]
predictions = ["Hello world!!", "Godbye for now!"]

# Resolve confusables before tokenization
normalizer = stringalign.normalize.StringNormalizer(resolve_confusables="intentional")
tokenizer = stringalign.tokenize.GraphemeClusterTokenizer(pre_tokenization_normalizer=normalizer)

multi_alignment_analyzer = MultiAlignmentAnalyzer.from_strings(references, predictions, tokenizer=tokenizer)
cer = multi_alignment_analyzer.compute_ter()

print(f"The overall CER for this dataset is {cer}")
