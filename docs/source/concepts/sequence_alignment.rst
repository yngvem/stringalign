.. _sequence_alignment:

Sequence alignment: Stringaling's backbone
==========================================

All metrics that Stringalign computes are built around *sequence alignment*, also known as *optimal matching*.
In sequence alignment, we want to find the *optimal alignment* of two sequences, which is defined by a minimal set of *edit operations* that turns one string (what we call the predicted string) into another string (what we call the reference string).
These edit operations can, in our case, be insertions, deletions or replacements.
For example, if we have the predicted string ``Helo wrolb!`` and the reference string ``Hello world!``, then the optimal alignment consists of four edit operations:

* Insert an ``l`` in the word ``Helo``
* Insert an ``o`` between the ``w`` and the ``r`` in the word ``wrolb!``
* Delete the ``o`` after the ``r`` in the word ``wrolb!``
* Replace the ``b`` in the word ``wrolb!`` with a ``d``

With these edit operations, we get the following alignment:

.. raw:: html
    :file: sequence_alignment/character_alignment.html

From this alignment, we can compute a variety of useful metrics, like the :ref:`levenshtein_distance`, :ref:`character error rate (CER) <token_error_rate>` and :ref:`token specific accuracies <token_specific_performance_example>`.

Tokenization
------------

There was one very important topic we glossed over above: What are we aligning?
In the example above, we aligned characters, or :ref:`grapheme_clusters`, but, if we wanted to find the word error rate instead of the character error rate, we could align words instead.
For example, if we use a tokenizer that splits at whitespace, we could get the following two edits:

1. Replace ``Helo`` with ``Hello``
2. Replace ``wrolb!`` with ``world!``

In general, we need a way to split a string into a sequence of *tokens* which we align, and Stringalign has a variety of built-in *tokenizers*. For characters, you can use the :class:`GraphemeClusterTokenizer <stringalign.tokenize.GraphemeClusterTokenizer>`, and for words, you can either use the :class:`SplitAtWhitespaceTokenizer <stringalign.tokenize.SplitAtWhitespaceTokenizer>`, the :class:`UnicodeWordTokenizer <stringalign.tokenize.UnicodeWordTokenizer>` or the :class:`SplitAtWordBoundaryTokenizer <stringalign.tokenize.SplitAtWordBoundaryTokenizer>`.
For more information about tokenization and what they do, see the :ref:`tokenizers_example` example or the api documentation for the :mod:`stringalign.tokenize` module.


The uniqueness properties of string alignment
---------------------------------------------

While the number of edit operations in the optimal alignment is unique, there may be more than one optimal alignment.
For example, in the string above, we have the following degrees of freedom

1. Do you insert the ``l`` between the ``e`` and ``l`` or between the ``l`` and ``o``?
2. How do you handle the transposition of the ``o`` and the ``r`` in ``wrolb!``?
    - Insert ``o`` before ``r`` and delete ``o`` after ``r``?
    - Delete ``r`` beffore ``o`` and insert ``r`` after ``o``?
    - Replace ``r`` with ``o`` and ``o`` with ``r``?

In total, this means that there are six different possible optimal character-alignments between the strings ``Hello world!`` and ``Helo wrolb!``:

.. raw:: html
    :file: sequence_alignment/combined_alignment.html

These "degeneracies" mean that we need to take care when we compare character-specific operations.
For example, the true positive rate for a given character can change depending on which of the optimal alignments Stringalign chooses.
Still, our experience is that while non-uniqueness poses a theoretical issue, inspecting these character-specific metrics can provide valuable insight into model performance, as demonstrated in :ref:`norhand_example`.

Dealing with multiple optimal alignments
----------------------------------------

Stringalign has implemented two features to alleviate the effect of nonunique alignments: storing uniqueness information for all aligned strings and combining subsequent alignment operations.
By storing whether each aligned string pair is unique, we make it possible to manualy inspect a subset of all non-unique string pairs to assess effect of different alignments.
Stringalign also has an option to return all possible optimal alignments for two strings but the number of possible optimal alignments grows exponentially with the sequence length, so this can be very slow.
To deal with the exponential increase in possible optimal sequence alignments, we also have the option of computing a random optimal alignment, which makes it possible to get uncertainty estimates for the edit operation counts, which you can see in the :ref:`randomised_alignments_example`-example.
Finally, by combining subsequent alignment operations, we avoid some of the degeneracies (e.g. transposition of tokens), which makes some heuristics for classifying edit operation types (e.g. n-gram duplication errors) and the edit counts for each token-substring more stable.

For example, if we combine edit operations in our example, we get the following two possible alignments:

1. Insert an ``l`` between the ``l`` and ``o``
2. Replace ``ro`` with ``or`` in wrolb!

and

1. Insert an ``l`` between the ``e`` and ``l``
2. Replace ``ro`` with ``or`` in wrolb!

However, combining alignment operations also means that metrics requiring the count of each token in the reference are ill-defined (e.g. token specific sensitivities), so these can only be computed with the "raw" non-combined alignment operations.
See :ref:`most_common_errors_example` for an example demonstrating the utility of combining sequence alignments.
