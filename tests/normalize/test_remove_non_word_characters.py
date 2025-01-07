from stringalign.normalize import remove_non_word_characters


def test_simple_example():
    """Different whitespaces are turned into a standard space for known example"""

    example_text = "Hello, \t\nworld!\u2002Here is a\u001ftest."
    expected_output = "Hello \t\nworld\u2002Here is a\u001ftest"
    assert remove_non_word_characters(example_text) == expected_output


# Note: The tests for the StringNormalizer class test various aspects of whitespace normalization also
# but we keep this file as a simple example of how the remove_non_word_characters-function works.
