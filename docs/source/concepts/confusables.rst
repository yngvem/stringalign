
Confusables
===========

Confusables, also known as homoglyphs or homographs, are characters that look the same or similar, but are different characters and can't be normalized to the same code points.
For example Đ (``U+0110``) and Ð (``U+00D0``)

These only look similar when capitalized and in lower case they are easily distinguished (đ and ð).
However, there are also instances where the characters look the same in both upper and lower case. For instance the latin A/a and the cyrilic А/а.

The choice of font can sometimes impact how similar confusables appear.
For example, lowercase ``l`` and uppercase ``I`` look the same in many sans serif fonts, like Arial and Helvetica, (l vs I), while they look more different in serif fonts.

The existence of confusables can in some cases be a security problem, so the Unicode consortium has created lists of characters that are similar in many fonts.
In particular, they have created the ``confusables.txt``-list, which contains "a mapping for visual confusables for use in detecting possible security problems." and the ``intentional.txt``-list, which contains "A selection of characters whose glyphs in any particular typeface would probably be designed to be identical in shape when using a harmonized typeface design."
The former contains, for example, a mapping between ``l`` and ``I``, while the latter does not. See :cite:p:`unicode-annex-39` for more details.

The importance of confusables when evaluating transcription models
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When evaluating a model, you should consider how you expect the model to handle confusable characters.
An :abbr:`OCR (Optical character recognition)` model that is purely visual, classifying character by character, would not be able to distinguish between identical confusable characters,
so it might make the most sense to normalize them to the same character before evaluating.
On the other hand, if you are looking at an OCR model that also models language, you might want it to be able to choose correctly among confusables.
And if you are evaluating an :abbr:`ASR (Automatic speech recognition)` model you might want it to "hear" the difference between visually confusable characters.
It depends on what type of model you evaluate and what application you are evaluating it for.
Either way it is good to reflect on, and be aware of, how you treat confusable characters when evaluating.
In Stringalign you can enable confusable normalisation in the :class:`stringalign.normalize.StringNormalizer`,
either based on the unicode ``confusables.txt`` list or the ``intentional.txt`` list or input a custom dictionary with a confusable normalisation mapping.
For an example, see :ref:`confusables_example`.

.. note::

    The ``intentional.txt`` list does not specify a normalised character, just that two characters are similar.
    In Stringalign, the character with the lowest code point is selected as an arbitrary way to obtain a stable normalization mapping.

.. note::

    If you are training your own model, you should think about how you are treating confusables already in the data processing step before training the model
