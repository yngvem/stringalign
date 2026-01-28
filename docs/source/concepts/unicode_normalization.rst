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
The ``"å" == "å"`` equivalence mentioned above is an example of this type of equivalence.
See Table 1 below for more examples.

There is also another type of equivalence, compatibility equivalence, that denotes whether characters or sequences of characters represent the same abstract character but with different visual appearances.
The difference between compatibility equivalent forms can be purely stylistic in some contexts, but not in others.
For example can they be used in mathematical notation to represent different information.
So we need to be careful when deciding if using compatibility equivalence is appropriate.
See Table 1 for some examples.

.. table:: **Table 1:** Equivalent code points

    +-----------------+----------------------+----------------------+----------------------+----------------------+
    | Character       | NFC                  | NFD                  | NFKC                 | NFKD                 |
    +=================+======================+======================+======================+======================+
    | | **Å**         | | **Å**              | | **A ̊**             | | **Å**              | | **A ̊**             |
    | | ``212B``      | | ``00C5``           | | ``0041 030A``      | | ``00C5``           | | ``0041 030A``      |
    +-----------------+----------------------+----------------------+----------------------+----------------------+
    | | **Ω**         | | **Ω**              | | **Ω**              | | **Ω**              | | **Ω**              |
    | | ``2126``      | | ``03A9``           | | ``03A9``           | | ``03A9``           | | ``03A9``           |
    +-----------------+----------------------+----------------------+----------------------+----------------------+
    | | **ñ**         | | **ñ**              | | **n ̃**             | | **ñ**              | | **n ̃**             |
    | | ``00F1``      | | ``00F1``           | | ``006E 0303``      | | ``00F1``           | | ``006E 0303``      |
    +-----------------+----------------------+----------------------+----------------------+----------------------+
    | | **ṩ**         | | **ṩ**              | | **s ̣ ̇**            | | **ṩ**              | | **s ̣ ̇**            |
    | | ``1E69``      | | ``1E69``           | | ``0073 0323 0307`` | | ``1E69``           | | ``0073 0323 0307`` |
    +-----------------+----------------------+----------------------+----------------------+----------------------+
    | | **ḍ̇**         | | **ḍ ̇**             | | **d ̣ ̇**            | | **ḍ ̇**             | | **d ̣ ̇**            |
    | | ``1E0B 0323`` | | ``1E0D 0307``      | | ``0064 0323 0307`` | | ``1E0D 0307``      | | ``0064 0323 0307`` |
    +-----------------+----------------------+----------------------+----------------------+----------------------+
    | | **ﬁ**         | | **ﬁ**              | | **ﬁ**              | | **fi**             | | **fi**             |
    | | ``FB01``      | | ``FB01``           | | ``FB01``           | | ``0066 0069``      | | ``0066 0069``      |
    +-----------------+----------------------+----------------------+----------------------+----------------------+
    | | **4²**        | | **4²**             | | **4²**             | | **42**             | | **42**             |
    | | ``0034 00B2`` | | ``0034 00B2``      | | ``0034 00B2``      | | ``0034 0032``      | | ``0034 0032``      |
    +-----------------+----------------------+----------------------+----------------------+----------------------+
    | | **ſ**         | | **ſ**              | | **ſ**              | | **s**              | | **s**              |
    | | ``017F``      | | ``017F``           | | ``017F``           | | ``0073``           | | ``0073``           |
    +-----------------+----------------------+----------------------+----------------------+----------------------+

.. note::
    Two characters can be distinct, even after normalisation, and still look the same.
    See :ref:`confusables` for more information.
