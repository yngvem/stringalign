"""
Custom tokenization with Norwegian stemmer
==========================================

For some applications, it might be useful to `stem <https://en.wikipedia.org/wiki/Stemming>`_ the words before calculating the word error rate.
For example, if you are evaluating a speech to text model and there are multiple acceptable written forms of a word.
In Norwegian Bokmål, the word ``boken`` and ``boka`` are both permitted forms of ``the book`` and depending on your application it might be unimportant which version the model uses.
"""

import nltk
import stringalign
from stringalign.normalize import StringNormalizer
from stringalign.tokenize import SplitAtWhitespaceTokenizer

# %%
# Lets say we have a data sample with the following ground truth reference and want to compare the output of two models:

example_reference = "Hun henta boka fra bokhylla"  # She fetched the book from the bookshelf
example_prediction_1 = "Hun hentet boken fra bokhyllen"  # She fetched the book from the bookshelf
example_prediction_2 = "Hun løp vekk fra regnet"  # She ran away from the rain

# %%
# Here we see that one model has hallucinated completely different content while the other model has the exact same content with different equivalent inflections.
# However, if we compare the models using just WER they appear to perform the same.

tokenizer = SplitAtWhitespaceTokenizer()
wer_1, evaluator_1 = stringalign.evaluation.compute_wer(example_reference, example_prediction_1)
wer_2, evaluator_1 = stringalign.evaluation.compute_wer(example_reference, example_prediction_2)
print(f"WER for example prediction 1: {wer_1:4.2f}, WER for example prediction 2: {wer_2:4.2f}")

# %%
# If we instead use a tokenizer that includes a stemming step, essentially removing affixes from each word to obtain their base form, we see that one model seems to behave much better than the other.


class NorwegianStemmerTokenizer:
    def __init__(self):
        # The nltk Snowball stemming code assumes NFC-normalised text, so we explicitly normalise the text before
        # stemming.
        self.pre_tokenization_normalizer = StringNormalizer(normalization="NFC")
        self.word_split_tokenizer = SplitAtWhitespaceTokenizer()
        self.stemmer = nltk.stem.snowball.NorwegianStemmer()

    def __call__(self, text):
        return [self.stemmer.stem(word) for word in self.word_split_tokenizer(text)]

    def join(self, words):
        return " ".join(words)


stem_tokenizer = NorwegianStemmerTokenizer()

stemmed_wer_1, evaluator_1 = stringalign.evaluation.compute_ter(
    example_reference, example_prediction_1, tokenizer=NorwegianStemmerTokenizer()
)
stemmed_wer_2, evaluator_2 = stringalign.evaluation.compute_ter(
    example_reference, example_prediction_2, tokenizer=NorwegianStemmerTokenizer()
)
print(
    f"Stemmed WER for example prediction 1: {stemmed_wer_1:4.2f}, stemmed WER for example prediction 2: {stemmed_wer_2:4.2f}"
)


# %%
# Stemming will not always give a perfect result and will not solve all problems arising from multiple equivalent inflections.
# However, looking at the WER after stemming could give useful insights that could be lost from looking at unprocessed WER.
#
# .. note::
#     You may want to consider other ways of reducing other ways of reducing morphological variants into a base form.
#     For example, `spaCy’s lemmatizer module <https://spacy.io/api/lemmatizer>`_ contains various pre-trained lemmatizers that can be more robust than the simple Snowball stemmer used in this example.
