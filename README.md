# Stringalign

<img src="https://stringalign.com/_images/logo_flat.svg" width="600px" alt="Two cute caterpillars dancing under bunting with the letters 'STRING ALIGN'" role="img"/>

**A string comparison library that adhers to the quirks of Unicode.**

## What is this?

Stringalign is a library for comparing strings.
At its base, Stringalign takes two strings, a reference string and a predicted string, and aligns them.
Based on this alignment, we can then compute many interesting performance metrics, such as the edit distance (Levenshtein), error rates and much more.

For more information, see Stringalign's extensive documentation on [http://stringalign.com/](http://stringalign.com/).

### A little example

For example, if the `reference` string is `Banana pancakes` and the `predicted` string is `bananana pancake`, then string align will align it

```raw
 Reference: B--anana pancakes
Prediction: bananana pancake-
```

This alignment is stored as a collection of *replacements*, *insertions*, *deletions* and *keeps*, that describe what we need to do with the predicted string to make it equal to the reference string. For the string above, we get

```raw
[Replaced('B', 'b'), Inserted('a'), Inserted('n'), Kept('a'), Kept('n'), Kept('a'), Kept('n'), Kept('a'), Kept(' '), Kept('p'), Kept('a'), Kept('n'), Kept('c'), Kept('a'), Kept('k'), Kept('e'), Deleted('s')]
```

or, if we join consequtive the `Deleted`, `Inserted` and `Replaced`:

```raw
[Replaced('B', 'ban'), Kept('anana pancake'), Deleted('s')]
```

Based on these alignments, we can compute standard string comparison metrics such as the *Levenshtein distance* and *character error rate*.
However, Stringalign also contains functions to do more in-depth analysis of the types of errors that occur when you have a whole collection of reference and predicted strings.
Examples of this is: the most common character confusions, the letters most often omitted in the prediction, the letters most often incorrectly included in the prediction, etc.
See our [gallery of examples](http://stringalign.com/examples.html) for more information.

## What's the point?

Stringalign might sound similar to other Python libraries, like Jiwer and Levenshtein (which both use Rapidfuzz behind-the-scenes).
However, what puts Stringalign apart is that it handles Unicode "correctly" and provides easy-to-use tools for going in-depth in the analysis.

Take this example:

```python
import Levenshtein

print(Levenshtein.distance('ñ', 'ñ'))
```

```raw
2
```

What happened here?
The first `'ñ'` consists of two code points: an `n` and a "put a tilde on the previous character" code point, while the second `'ñ'` only consists of the single code point `'ñ'`.
Let's try it with Stringalign instead:

```python
from stringalign.align import levenshtein_distance

print(levenshtein_distance('ñ', 'ñ'))
```

```raw
0
```

We see the expected behaviour.
By default, Stringalign will normalize your text and segment it into *Unicode extended grapheme clusters* before aligning.
An extended grapheme cluster is essentially just what a computer should display as one letter, and while a grapheme cluster usually is just one code-point, it's not always that.
Since tools like Jiwer and Levenshtein work directly on the code-points, they will miss these edge cases.

### Emojis

Often, we don't need to worry about separating between code-points and grapheme clusters.
However, the moment emojis come into the picture, this changes.
Many emojis are just the single code point.
However, some are created by combining two or more other emojis --- like `'🏳️‍🌈'`, which is created by combining the white-flag emoji, `'🏳'`, a *variant selector* `'\uFE0F'`, a *zero width joiner* `'\u200D'` and the rainbow emoji, `'🌈'`.
Because Stringalign takes care of aligning normalized grapheme clusters automatically, it will also work correctly with emoiis

```python
import Levenshtein
from stringalign.align import levenshtein_distance

print("Levenshtein", Levenshtein.distance('🏳️‍🌈', '🌈'))
print("Stringalign", levenshtein_distance('🏳️‍🌈', '🌈'))
```

```raw
Levenshtein 3
stringalign 1
```

## How does it work?

Stringalign works in a two-step process: first, the input strings are tokenized into normalised extended grapheme clusters, before they are aligned using the Needleman-Wunsch algorithm.
You can customise this if you want, e.g. switching out the tokenizer with one that casefolds all extended grapheme clusters, to get a case-insensitive alignment, or words to e.g. compute the word-error rate.

We use an extension module written in Rust for two important parts of Stringalign: grouping unicode code-points into extended grapheme clusters (with the [unicode_segmentation](https://docs.rs/unicode-segmentation/latest/unicode_segmentation/index.html) crate) and assembling the Needleman-Wunsch cost-matrix (which has O(n²) time- and memory-complexity).

## Citing Stringalign

If you use Stringalign for your research, then please cite this repo. For example:

```
Moe, Y. M., & Roald, M. (2024). Stringalign [Computer software]. https://github.com/yngvem/stringalign
```
