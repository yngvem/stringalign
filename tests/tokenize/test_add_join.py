from hypothesis import given
from hypothesis import strategies as st
from stringalign.tokenize import add_join


def tokenizer(text: str) -> list[str]:
    return text.split()


def test_join_method_is_added_to_tokenizer() -> None:
    """The `join` method is added to the tokenizer"""

    wrapped_tokenizer = add_join()(tokenizer)
    assert hasattr(wrapped_tokenizer, "join")


@given(string=st.text(alphabet=st.characters()))
def test_add_join_preserves_original_tokenizer(string: str) -> None:
    """The original tokenizer is preserved after adding the `join` method"""

    wrapped_tokenizer = add_join()(tokenizer)
    assert wrapped_tokenizer(string) == tokenizer(string)


def test_join_method_joins_tokens_for_simple_example() -> None:
    """The `join` method joins tokens with a space"""

    wrapped_tokenizer = add_join()(tokenizer)
    tokens = ["Hello", "world"]
    assert wrapped_tokenizer.join(tokens) == "Hello world"


@given(string=st.text(alphabet=st.characters()), sep=st.characters())
def test_join_method_joins_tokens_with_custom_separator(string: str, sep: str) -> None:
    """The `join` method joins tokens with a custom separator"""

    wrapped_tokenizer = add_join(sep=sep)(tokenizer)
    tokens = string.split()
    assert wrapped_tokenizer.join(tokens) == sep.join(tokens)
