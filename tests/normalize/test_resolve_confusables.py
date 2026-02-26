from stringalign.normalize import resolve_confusables


def test_simple_example() -> None:
    """Confusable characters are replaced with their intended counterparts for a known example"""
    confusables = {"𝓦": "W", "t": "𝓽"}
    example_text = "Hello, 𝓦orld! Here is a 𝓽est."
    expected_output = "Hello, World! Here is a 𝓽es𝓽."
    assert resolve_confusables(example_text, confusables) == expected_output


def test_multi_token_input() -> None:
    """Multi-codepoint confusables are resolved correctly"""
    confusables = {"ø": "oe", "aa": "å"}
    example_text = "Brunost paa grovbrød"
    expected_output = "Brunost på grovbroed"
    assert resolve_confusables(example_text, confusables) == expected_output


# Note: The tests for the StringNormalizer class test various aspects of confusable resolving also
# but we keep this file as a simple example of how the resolve_confusables-function works.
