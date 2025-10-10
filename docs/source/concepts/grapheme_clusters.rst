.. _grapheme_clusters:

Grapheme clusters
=================

When you measure the length of a string in Python using :external+python:py:func:`len`, what you get is the number of unicode `code points <https://www.unicode.org/versions/latest/core-spec/chapter-2/#G25564>`_ in the string.
However, code points are not characters and what a user thinks of as one character can sometimes be made up of multiple unicode code points. If you combine ``a`` and a `circle <https://www.compart.com/en/unicode/U+030A>`_, for instance, you get ``å``.
Users will think of this as a single character, but it contains two unicode code points under the hood.

.. code:: python

    for character in "å":
        code_point = hex(ord(character))
        print(f"{character!r}: {code_point}")


Therefore, if you are interested in the user perceived length of text, you shouldn't segment the text based on code-points, but based on something called grapheme cluster boundaries.
The Unicode standard has defined a default algorithm for detecting grapheme cluster boundaries in Unicode strings that should work well in most cases[1]_.
The grapheme clusters we obtain with this algorithm are called *extended grapheme clusters*.

Sometimes, we can :ref:`normalize <unicode_normalization>` multi code point grapheme clusters into single code points. For example

.. code:: python

    import unicodedata
    len(unicodedata.normalize("NFC", "å"))

.. code::

    1

However, that is not always possible. For example

.. code:: python

    import unicodedata
    len(unicodedata.normalize("g̈")

.. code::

    2

Cannot be normalized into single code points and neither can `Zero-with-joined emoji-sequences <https://www.unicode.org/reports/tr51/#Emoji_ZWJ_Sequences>`_ :cite:p:`unicode-annex-51`

.. code:: python

    import unicodedata
    len(unicodedata.normalize("🏳️‍🌈"))

.. code::

    4

Grapheme clusters are important to consider when we compute string metrics, like the :ref:`levenshtein_distance`.
If we just naively compute string metrics (like how `Levenshtein <https://rapidfuzz.github.io/Levenshtein/>`_ or `Jiwer <https://jitsi.github.io/jiwer/>`_ does by default), then the metrics will be wrong for multi-codepoint characters.

.. code:: python

    import Levenshtein
    print(Levenshtein.distance("på", "p"))

.. code::

    2

Therefore, Stringalign will, by default, start by tokenising strings into extended grapheme clusters (characters), and compute the character edits required to transform one string into another:

.. code:: python

    import stringalign
    print(stringalign.align.levenshtein_distance("på", "p"))

.. code::

    1

If you're interested in learning more about grapme clusters, then you can read the `Unicode Technical Report #29 <https://unicode.org/reports/tr29/>`_ about segmenting unicode text.

.. rubric:: Footnotes

.. [1] Note that that defining a completely unambiguous concept for user-perceived character is not always possible :cite:p:`unicode-annex-29`
