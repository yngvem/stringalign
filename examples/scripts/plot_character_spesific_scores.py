"""
.. _token_specific_performance_example:

Evaluating token-specific performance
=====================================

Sometimes, you might be interested in seeing how the model performs on a specific subset of characters.
Stringalign provides a couple of useful utilities for this.
"""

import stringalign

references = [
    "Snekkermester Thor Bjørklund fra Øvre Smestad i Fåberg patenterte Ostehøvelen i 1925.",
    "Snøen smeltet i vårsola.",
    "Ved å blande blått og gult kan du få grønt.",
    "Det var et ærlig forsøk",
]
predictions = [
    "Snekkermester Thor Bjorklund fra Ovre Smestad i Faberg patenterte Ostehovelen i 1925.",
    "Snoen smeltet i varsola",
    "Ved a blande blatt og gult kan du fa grønt.",
    "Det var et aerlig forsok",
]

tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()
analyzer = stringalign.evaluation.MultiAlignmentAnalyzer.from_strings(references, predictions, tokenizer)
cm = analyzer.confusion_matrix

cer = cm.compute_token_error_rate()
print(f"The CER is {cer}")

# %%
# Next, we can compute token-specific statistics to see how the model performs on specific characters:

sensitivity = cm.compute_sensitivity()
precision = cm.compute_precision()
f1_scores = cm.compute_f1_score()

for character in "æøå":
    print(f"Statistics for {character}:")
    print(f"Sensitivity: {sensitivity[character]}")
    print(f"Precision:   {precision[character]}")
    print(f"F1 score:    {f1_scores[character]}")
    print()

# %%
# We see that the precision can be ``nan``, this happens for all tokens *not* in the predicted string, as the precision is defined by the number of times a given token was correctly identified (``true_positives``) divided by the number of times the token was predicted (``true_positives + false_positives``).
# If a token never occurs in the predicted string, then this quantity is ill-defined, and becomes ``nan``.
#
# Aggregating the summary statistics
# ----------------------------------
# We can also aggregate the number of true positives, false positives and false negatives for multiple tokens to get an overall measure for Norwegian special characters

overall_sensitivity = cm.compute_sensitivity(aggregate_over="æøå")
overall_precision = cm.compute_precision(aggregate_over="æøå")
overall_f1 = cm.compute_f1_score(aggregate_over="æøå")

print(f"The overall sensitivity for æ, ø and å is: {overall_sensitivity}")
print(f"The overall precision for æ, ø and å is:   {overall_precision}")
print(f"The overall F1 score for æ, ø and å is:    {overall_f1}")
