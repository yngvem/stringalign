import hypothesis
import hypothesis.strategies as st
from stringalign.tokenize import SplitAtWhitespaceTokenizer

whitespace_strategy = st.characters(whitelist_categories=["Zs"])
word_strategy = st.text(
    alphabet=st.characters(blacklist_categories=["Zs", "Cc"]),  # No whitespace or control characters
    min_size=1,
)
list_of_random_words_strategy = st.lists(word_strategy, min_size=1)


def test_simple_example() -> None:
    assert SplitAtWhitespaceTokenizer()("Hello World") == ["Hello", "World"]


@hypothesis.given(separator=whitespace_strategy)
def test_nonspace_whitespace(separator) -> None:
    hello_world = "Hello" + separator + "World"
    assert SplitAtWhitespaceTokenizer()(hello_world) == ["Hello", "World"]


@hypothesis.given(words=list_of_random_words_strategy)
def test_join_roundtrip(words):
    tokenizer = SplitAtWhitespaceTokenizer()
    words = [tokenizer.pre_tokenization_normalizer(word) for word in words]
    text = " ".join(words)

    tokens = tokenizer(text)
    assert tokens == words
    assert tokenizer.join(tokens) == text


@hypothesis.given(text=st.text())
def test_tokens_are_atomic(text):
    """Tokenizing a token should not change the token"""
    tokenizer = SplitAtWhitespaceTokenizer()
    tokens = tokenizer(text)
    hypothesis.assume(tokens)  # Skip test if there are no tokens (i.e. only whitespace in text)
    assert all(
        tokenizer(token)
        == [
            token,
        ]
        for token in tokens
    )
