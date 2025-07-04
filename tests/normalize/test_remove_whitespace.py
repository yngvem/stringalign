from stringalign.normalize import remove_whitespace


def test_simple_example():
    """Different whitespaces are removed for simple known example"""

    example_text = "Hello, \t\nworld!\u2002Here is a\u001ftest."
    expected_output = "Hello,world!Hereisatest."
    assert remove_whitespace(example_text) == expected_output


# Note: The tests for the StringNormalizer class test various aspects of whitespace normalization also
# but we keep this file as a simple example of how the remove_whitespace-function works.
