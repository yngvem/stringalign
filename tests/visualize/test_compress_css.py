from stringalign.visualize import compress_css


def test_simple_example_is_compressed_correctly():
    """Test that a simple CSS example is compressed correctly."""
    css = """
    .example {
        color: red;
        font-size: 16px;
        font-weight: bold;
    }
    .example2 {
        color: blue;
        font-size: 14px;
    }
    """
    expected_compressed = (
        ".example { color: red; font-size: 16px; font-weight: bold; } .example2 { color: blue; font-size: 14px; }"
    )
    compressed_css = compress_css(css)
    assert compressed_css == expected_compressed
