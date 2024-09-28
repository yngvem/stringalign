import hypothesis.strategies as st
from hypothesis import given

from stringalign.align import Delete, Insert, Replace, character_align_strings


@given(st.text(), st.text())
def test_align_strings_length(reference, predicted):
    alignment = character_align_strings(reference, predicted)
    assert len(alignment) >= max(len(reference), len(predicted))


@given(st.text(), st.text())
def test_align_strings_types(reference, predicted):
    alignment = character_align_strings(reference, predicted)
    for op in alignment:
        assert isinstance(op, (Insert, Delete, Replace)) or op is None


@given(st.text(), st.text())
def test_align_strings_reconstruct(reference, predicted):
    alignment = character_align_strings(reference, predicted)

    rec_predicted = ""
    rec_reference = ""
    pred_iter = iter(predicted)
    ref_iter = iter(reference)
    for op in alignment:
        if op is None:
            rec_predicted += next(ref_iter)
            rec_reference += next(pred_iter)

        elif isinstance(op, Replace):
            ref_char = next(ref_iter)
            pred_char = next(pred_iter)

            assert ref_char == op.replacement
            assert pred_char == op.substring

            rec_predicted += op.substring
            rec_reference += op.replacement

        elif isinstance(op, Insert):
            char = next(ref_iter)
            assert char == op.substring
            rec_reference += char

        elif isinstance(op, Delete):
            char = next(pred_iter)
            assert char == op.substring
            rec_predicted += char

    assert rec_reference == reference
    assert rec_predicted == predicted


@given(st.text())
def test_align_strings_identical(text):
    alignment = character_align_strings(text, text)
    assert all(op is None for op in alignment)
    assert len(alignment) == len(text)


def test_normalise_unicode():
    a_with_ring = "Å"
    letter_å = "Å"

    assert a_with_ring != letter_å
    assert character_align_strings(a_with_ring, letter_å) == [None]


def test_align_combining_grapheme():
    """Test that graphemes that consist of multiple code-points are handled as a single character.

    See e.g. https://tonsky.me/blog/unicode/ and https://grapheme.readthedocs.io/en/latest/grapheme.html
    """
    assert character_align_strings("ą́", "a") == [Replace("a", "ą́")]


def test_align_emojis():
    """Test that emojis that consist of multiple code-points are handled as a single character.

    See e.g. https://tonsky.me/blog/unicode/ and https://grapheme.readthedocs.io/en/latest/grapheme.html
    """
    rainbow_flag = "🏳️‍🌈"
    assert rainbow_flag == "".join(["🏳", "️", "‍", "🌈"])

    rainbow = "🌈"

    alignment = character_align_strings(rainbow_flag, rainbow)
    assert alignment == [Replace("🌈", "🏳️‍🌈")]
