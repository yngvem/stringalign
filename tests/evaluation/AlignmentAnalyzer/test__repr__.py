from inspect import cleandoc

import stringalign
from stringalign.evaluation import AlignmentAnalyzer


def test_from_strings_with_example() -> None:
    alignment_analyzer = AlignmentAnalyzer.from_strings(
        reference="Hello",
        predicted="Hi",
        tokenizer=stringalign.tokenize.GraphemeClusterTokenizer(),
        metadata={"a": 3},
    )
    expected_repr = cleandoc(
        """AlignmentAnalyzer(
            reference='Hello',
            predicted='Hi',
            metadata=FrozenDict({'a': 3}),
            tokenizer=GraphemeClusterTokenizer(
                pre_tokenization_normalizer=StringNormalizer(
                    normalization='NFC',
                    case_insensitive=False,
                    normalize_whitespace=False,
                    remove_whitespace=False,
                    remove_non_word_characters=False,
                    resolve_confusables=None,
                ),
                post_tokenization_normalizer=StringNormalizer(
                    normalization='NFC',
                    case_insensitive=False,
                    normalize_whitespace=False,
                    remove_whitespace=False,
                    remove_non_word_characters=False,
                    resolve_confusables=None,
                )
            )
        )
        """
    )
    assert repr(alignment_analyzer) == expected_repr
