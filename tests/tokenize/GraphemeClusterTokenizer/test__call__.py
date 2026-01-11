import hypothesis
import hypothesis.strategies as st
from stringalign.tokenize import GraphemeClusterTokenizer

whitespace_strategy = st.characters(whitelist_categories=["Zs"])
string_strategy = st.text(min_size=1)
word_strategy = st.text(
    alphabet=st.characters(blacklist_categories=["Zs", "Cc"]),  # No whitespace or control characters
    min_size=1,
)
list_of_random_words_strategy = st.lists(word_strategy, min_size=1)


def test_simple_example() -> None:
    """A string consisting of single- and multi-code point grapheme clusters is tokenized correctly."""
    assert GraphemeClusterTokenizer()("abc🏳️‍🌈🏳️‍⚧️❤️‍🔥") == ["a", "b", "c", "🏳️‍🌈", "🏳️‍⚧️", "❤️‍🔥"]


@hypothesis.given(text=string_strategy)
def test_join_roundtrip(text):
    tokenizer = GraphemeClusterTokenizer()
    text = tokenizer.pre_tokenization_normalizer(text)

    tokens = tokenizer(text)
    assert tokenizer.join(tokens) == text


@hypothesis.given(text=string_strategy)
def test_tokens_are_atomic(text):
    """Tokenizing a token should not change the token"""
    tokenizer = GraphemeClusterTokenizer()
    text = tokenizer.pre_tokenization_normalizer(text)

    tokens = tokenizer(text)
    hypothesis.assume(tokens)  # Skip test if there are no tokens (i.e. only whitespace in text)
    assert all(
        tokenizer(token)
        == [
            token,
        ]
        for token in tokens
    )
