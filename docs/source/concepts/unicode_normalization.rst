.. _unicode_normalization:

Unicode normalization
=====================

Some characters can be represented in unicode in several ways.
Here is one example for the Norwegian letter ``å``:

.. code:: python

    print("å" == "å")

.. code:: raw

    False

This can naturally lead to some ambiguities when comparing strings and calculating string metrics. To counteract these ambiguities, the Unicode Consortium has defined normalized forms for equivalent characters.

Equivalence
-----------

To understand the normalized forms it's useful to first look at what Unicode defines as equivalent characters.
The unicode standard defines two types of equivalence: *canonical equivalence* and *compatibility equivalence* :cite:p:`unicode-standard{Chapter 2.12}` and :cite:p:`unicode-annex-15`
If code points or sequences of code points represent the same abstract character and should always look the same, that is canonical equivalence.
The `"å" == "å"` equivalence mentioned above is an example of this type of equivalence.
See Table X below for more examples.

+-------------+-----+-----+------+------+
| Equivalence | NFC | NFD | NFKC | NFKD |
| Character   |     |     |      |      |
+=============+=====+=====+======+======+
|             |     |     |      |      |
+-------------+-----+-----+------+------+
|             |     |     |      |      |
+-------------+-----+-----+------+------+
|             |     |     |      |      |
+-------------+-----+-----+------+------+
|             |     |     |      |      |
+-------------+-----+-----+------+------+
|             |     |     |      |      |
+-------------+-----+-----+------+------+

There is also another type of equivalence, compatibility equivalence, that denotes whether characters or sequences of characters represent the same abstract character but with different visual appearances.
The difference between compatibility equivalent forms can be purely stylistic in some contexts, but not in others.
For example can they be used in mathematical notation to represent different information.
So we need to be careful when deciding if using compatibility equivalence is appropriate.
See table X for some examples.

.. note::
    Two characters can be distinct, even after normalisation, and still look the same.
    See :ref:`confusables` for more information.
