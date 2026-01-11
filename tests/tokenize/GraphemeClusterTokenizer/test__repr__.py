from inspect import cleandoc

from stringalign.normalize import StringNormalizer
from stringalign.tokenize import GraphemeClusterTokenizer


def test_with_example() -> None:
    pre_token_normalizer = StringNormalizer(
        normalization="NFC",
        case_insensitive=False,
        normalize_whitespace=False,
        remove_whitespace=False,
        remove_non_word_characters=False,
        resolve_confusables=None,
    )
    post_token_normalizer = StringNormalizer(
        normalization="NFKD",
        case_insensitive=False,
        normalize_whitespace=False,
        remove_whitespace=False,
        remove_non_word_characters=False,
        resolve_confusables=None,
    )
    tokenizer = GraphemeClusterTokenizer(
        pre_tokenization_normalizer=pre_token_normalizer, post_tokenization_normalizer=post_token_normalizer
    )
    expected_repr = cleandoc("""GraphemeClusterTokenizer(
                                pre_tokenization_normalizer=StringNormalizer(
                                    normalization='NFC',
                                    case_insensitive=False,
                                    normalize_whitespace=False,
                                    remove_whitespace=False,
                                    remove_non_word_characters=False,
                                    resolve_confusables=None,
                                ),
                                post_tokenization_normalizer=StringNormalizer(
                                    normalization='NFKD',
                                    case_insensitive=False,
                                    normalize_whitespace=False,
                                    remove_whitespace=False,
                                    remove_non_word_characters=False,
                                    resolve_confusables=None,
                                )
                            )""")
    assert repr(tokenizer) == expected_repr
