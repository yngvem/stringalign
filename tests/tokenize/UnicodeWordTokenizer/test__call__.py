import hypothesis
import hypothesis.strategies as st
from stringalign.tokenize import UnicodeWordTokenizer

word_separator_whitespace_strategy = st.characters(
    categories=["Zs"],
    exclude_characters=["\u202f", "\u00a0"],
)
word_strategy = st.text(
    alphabet=st.characters(blacklist_categories=["Zs", "Cc"]),  # No whitespace or control characters
    min_size=1,
)
simple_word_strategy = st.text(
    alphabet=st.characters(categories=["L"]),  # Only letters and numbers
    min_size=1,
)
list_of_random_words_strategy = st.lists(word_strategy, min_size=1)
list_of_simple_words_strategy = st.lists(simple_word_strategy, min_size=1)


def test_simple_example() -> None:
    assert UnicodeWordTokenizer()("Hello World") == ["Hello", "World"]


def test_simple_example_with_punctuation() -> None:
    assert UnicodeWordTokenizer()("'Hello', (World)!") == ["Hello", "World"]


@hypothesis.given(separator=word_separator_whitespace_strategy)
def test_nonspace_whitespace(separator) -> None:
    hello_world = "Hello" + separator + "World"
    assert UnicodeWordTokenizer()(hello_world) == ["Hello", "World"]


@hypothesis.given(text=st.text())
def test_tokens_are_atomic(text):
    """Tokenizing a token should not change the token"""
    tokenizer = UnicodeWordTokenizer()
    tokens = tokenizer(text)
    hypothesis.assume(tokens)  # Skip test if there are no tokens (i.e. only whitespace in text)
    assert all(
        tokenizer(token)
        == [
            token,
        ]
        for token in tokens
    )
