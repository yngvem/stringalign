.. _token_error_rate:

The character, word and token error rate
========================================

Character error rate
--------------------

Character error rate (CER) measures the rate of errors in the predicted characters compared to the ground truth.
To calculate CER you divide the total number of incorrect characters in the prediction by the total number of characters in the reference.
In particular, we compute the character error rate as

.. math::

    \text{CER} = \frac{N^{(\text{c})}_i + N^{(\text{c})}_d + N^{(\text{c})}_s}{N^{(\text{c})}_\text{ref}},

where :math:`N^{(\text{c})}_i` is the number of inserted characters in the predicted string, :math:`N^{(\text{c})}_d` is the number of deleted characters in the reference, :math:`N^{(\text{c})}_s` is the number of substituted characters in the reference and :math:`N^{(\text{c})}_\text{ref}` is the total number of character in the reference.

As an example, consider the reference string ``"This is a sentence"`` and the predicted string ``"Tis iss a sentemce"``.
There is one character deletion (``h`` in ``This``), one character insertion (the extra ``s`` in ``is``) and one character substitution (``n -> m`` in ``sentence``), while the total number of characters in the reference is 18. So we have

.. math::

    \text{CER} = \frac{1 + 1 + 1}{18} = \frac{1}{6} = 0.151515...

Word error rate
---------------

Word error rate (WER) measures errors at the word level and to calculate it you divide the total number of incorrect words in the prediction by the total number of words in the reference.
We compute the word error rate as

.. math::

    \text{WER} = \frac{N^{(\text{w})}_i + N^{(\text{w})}_d + N^{(\text{w})}_s}{N^{(\text{t})}_\text{ref}},

where :math:`N^{(\text{w})}_i` is the number of inserted *words* in the predicted string, :math:`N^{(\text{w})}_d` is the number of deleted *words* in the reference, :math:`N^{(\text{c})}_s` is the number of substituted *words* in the reference and :math:`N^{(\text{w})}_\text{ref}` is the total number of *words* in the reference.

Let's consider the same strings as above ``"This is a sentence"`` and the predicted string ``"Tis iss a sentemce"``.
This time, there is three word substitutions, no word insertions, no word deletions and the reference has in total four words.
Consequently, the WER is

.. math::

    \text{WER} = \frac{0 + 0 + 3}{4} = \frac{3}{4} = 0.75.

You might notice that the formula for WER and CER are very similar, and the only difference is whether we're counting characters or words.
This is because they ar both examples of what we denote the *token error rate*.

Token error rate (TER)
----------------------
You might notice that the formula for WER and CER are very similar.
This is because both CER and WER are special cases of TER were the tokenizing is done on character level or word level, respectivly.
You can calculate TER for any form of tokenization.

.. math::

    \text{WER} = \frac{N^{(\text{t})}_i + N^{(\text{t})}_d + N^{(\text{t})}_s}{N^{(\text{t})}_\text{ref}},

where :math:`N^{(\text{t})}_i` is the number of inserted *tokens* in the predicted string,
:math:`N^{(\text{t})}_d` is the number of deleted *tokens* in the reference,
:math:`N^{(\text{t})}_s` is the number of substituted *tokens* in the reference and
:math:`N^{(\text{t})}_\text{ref}` is the total number of *tokens* in the reference.


Ambiguity of TER/CER/WER
------------------------

One clear challenge with reporting TER is that it does not give a full picture without also reporting the tokenization strategy.
It would not be possible for someone else to reproduce or compare with the results without tokenizing in the exact same way.

However, this problem is also present for CER and WER.
In particular for WER as word segmentation is not well defined (for example, how do you consider punctuation? Should the parentheses be counted as separate words? What about hyphenation?)
And even the CER can change depending on whether you segment characters based on code-points or :ref:`grapheme clusters <grapheme_clusters>` and how you handle :ref:`unicode normalization <unicode_normalization>`.
To ensure reproducable results, you should therefore always report how the characters and words are processed and tokenized whenever you report the CER, WER or TER.

Because of this, Stringalign focuses on transparency whenever these metrics are computed.
Tokenization is explicit, and whenever the :func:`stringalign.evaluate.compute_cer`, :func:`stringalign.evaluate.compute_wer` or :func:`stringalign.evaluate.compute_ter` convenience functions are used, the user also gets an :class:`stringalign.evaluate.AlignmentAnalyzer` object that displays tokenization details when it is printed.
See :ref:`cer_example` for an example of how this works in Stringalign.


.. note::

    There are two ways of estimating the WER and CER when you have multiple string-pairs to compute:
    You can either sum up the number of insertions, deletions, substitutions and tokens in total, or you can compute WER and CER for each string-pair and average them.
    Stringalign has built-in support for the former (see :ref:`cer_example` for more information).
