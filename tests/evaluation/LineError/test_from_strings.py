import pytest
from stringalign.align import Delete, Insert, Keep, Replace, align_strings
from stringalign.evaluation import LineError


@pytest.mark.parametrize(
    "reference, predicted, line_error",
    [
        (
            "Hello, world!",
            "Hello, world!",
            LineError(
                reference="Hello, world!",
                predicted="Hello, world!",
                alignment=(Keep("Hello, world!"),),
                raw_alignment=tuple(align_strings("Hello, world!", "Hello, world!")),
                horisontal_segmentation_errors=(),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                case_errors=(),
                metadata=None,
            ),
        ),
        (
            "Hello, world!",
            "Hello, world",
            LineError(
                reference="Hello, world!",
                predicted="Hello, world",
                alignment=(Keep("Hello, world"), Insert("!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Hello, world")),
                horisontal_segmentation_errors=(Insert("!"),),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                case_errors=(),
                metadata=None,
            ),
        ),
        (
            "Hello, world!",
            "hello, world",
            LineError(
                reference="Hello, world!",
                predicted="hello, world",
                alignment=(Replace("h", "H"), Keep("ello, world"), Insert("!")),
                raw_alignment=tuple(align_strings("Hello, world!", "hello, world")),
                horisontal_segmentation_errors=(
                    Replace("h", "H"),
                    Insert("!"),
                ),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                case_errors=(Replace("h", "H"),),
                metadata=None,
            ),
        ),
        (
            "Hello, world!",
            "Helllo, world!",
            LineError(
                reference="Hello, world!",
                predicted="Helllo, world!",
                alignment=(Keep("He"), Delete("l"), Keep("llo, world!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Helllo, world!")),
                horisontal_segmentation_errors=(),
                character_duplication_errors=(Delete("l"),),
                removed_duplicate_character_errors=(),
                case_errors=(),
                metadata=None,
            ),
        ),
        (
            "Hello, world!",
            "Helo, world!",
            LineError(
                reference="Hello, world!",
                predicted="Helo, world!",
                alignment=(Keep("He"), Insert("l"), Keep("lo, world!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Helo, world!")),
                horisontal_segmentation_errors=(),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(Insert("l"),),
                case_errors=(),
                metadata=None,
            ),
        ),
    ],
)
def test_from_strings_with_example(reference: str, predicted: str, line_error: LineError) -> None:
    assert LineError.from_strings(reference, predicted, tokenizer=None) == line_error
