"""
Overview of tokenizations
=====================

This example shows the different tokenization methods available in Stringalign 
and how you can easily add your own custom tokenization if you have any specific needs.

For these examples we will not add any string normalization (see :ref:`this example for more on that <example_normalization>`).
See :ref:`here <cer_example>` for an example that adds a string normalization to a tokenizer.
And the :mod:`stringalign.normalize` API documentation for an overview of the normalization options available in Stringalign.
"""
import stringalign

example_sentence = "Hello World! This is fun (example) sentence no. 10 000.😶‍🌫️"

# %%
# :class:`stringalign.tokenize.GraphemeClusterTokenizer`
# ------------------------------------------------------
tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()
print(tokenizer(example_sentence))

# %%
# :class:`stringalign.tokenize.SplitAtWhitespaceTokenizer`
# --------------------------------------------------------
tokenizer = stringalign.tokenize.SplitAtWhitespaceTokenizer()
print(tokenizer(example_sentence))

# %%
# :class:`stringalign.tokenize.SplitAtWordBoundaryTokenizer`
# ----------------------------------------------------------
tokenizer = stringalign.tokenize.SplitAtWordBoundaryTokenizer()
print(tokenizer(example_sentence))

# %%
# :class:`stringalign.tokenize.UnicodeWordTokenizer`
# --------------------------------------------------
tokenizer = stringalign.tokenize.UnicodeWordTokenizer()
print(tokenizer(example_sentence))

# %% 
# Custom tokenizer using `nb_tokenizer`
# -------------------------------------
import nb_tokenizer

tokenizer = stringalign.tokenize.add_join()(nb_tokenizer.tokenize)

print(tokenizer(example_sentence))