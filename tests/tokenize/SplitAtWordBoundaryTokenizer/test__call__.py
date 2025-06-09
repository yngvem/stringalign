import hypothesis
import hypothesis.strategies as st
from stringalign.tokenize import SplitAtWordBoundaryTokenizer


def test_simple_example() -> None:
    assert SplitAtWordBoundaryTokenizer()("Hello World") == ["Hello", " ", "World"]


def test_simple_example_with_punctuation() -> None:
    assert SplitAtWordBoundaryTokenizer()("'Hello', (World)!") == ["'", "Hello", "'", ",", " ", "(", "World", ")", "!"]


@hypothesis.given(text=st.text(alphabet=st.characters()))
def test_tokens_are_atomic(text):
    """Tokenizing a token should not change the token"""
    tokenizer = SplitAtWordBoundaryTokenizer()
    tokens = tokenizer(text)
    hypothesis.assume(tokens)  # Skip test if there are no tokens (i.e. only whitespace in text)
    assert all(
        tokenizer(token)
        == [
            token,
        ]
        for token in tokens
    )
