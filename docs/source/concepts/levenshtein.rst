.. _levenshtein_distance:

Levenshtein distance
====================

The Levenshtein distance :cite:p:`navarro_guided_2001`, also sometimes called edit distance, is a metric for measuring the difference between two strings.
The Levenshtein distance between two strings is given by the minimum number of edits (insertions, deletions or replacements/substitutions) that you need to transform one string into the other.
The higher the number, the more different the two strings are.

Example
-------

The Levenshtein distance between ``sun`` and ``sand`` is two because to turn ``sun`` into ``sand`` you need to replace one (``u -> a``) and add one (``d`` at the end).

.. code:: python

    import stringalign
    print(stringalign.align.levenshtein("sun", "sand"))

.. code::

    2

See the API documentation for :py:func:`stringalign.align.levenshtein_distance` for more information about this function.

.. note::
    What constitutes "one edit" depends on how the string is tokenized.
    In general the Levenshtein distance is defined as the smallest number of "single-character" edits, so to get an as accurate as possible Levenstein distance you might need to :ref:`normalize <unicode_normalization>` your strings and/or :ref:`segment on grapheme clusters <grapheme_clusters>` (Stringalign does both by default).
