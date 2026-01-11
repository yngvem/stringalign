from inspect import cleandoc

import stringalign
from stringalign.evaluation import MultiAlignmentAnalyzer


def test_with_example() -> None:
    evaluator = MultiAlignmentAnalyzer.from_strings(
        references=["abc", "def", "aaa"],
        predictions=["bbc", "deg", "abb"],
        tokenizer=stringalign.tokenize.UnicodeWordTokenizer(),
    )

    expected_repr = cleandoc(
        """MultiAlignmentAnalyzer(
            len=3,
            tokenizer=UnicodeWordTokenizer(
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

    assert repr(evaluator) == expected_repr
