from inspect import cleandoc

import stringalign.normalize


def test_with_example() -> None:
    normalizer = stringalign.normalize.StringNormalizer(
        normalization="NFKC",
        case_insensitive=True,
        normalize_whitespace=True,
        remove_whitespace=True,
        remove_non_word_characters=True,
        resolve_confusables="intentional",
    )
    expected_repr = cleandoc("""StringNormalizer(
    normalization='NFKC',
    case_insensitive=True,
    normalize_whitespace=True,
    remove_whitespace=True,
    remove_non_word_characters=True,
    resolve_confusables='intentional',
)
""")
    assert repr(normalizer) == expected_repr
