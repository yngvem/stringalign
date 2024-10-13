import pytest
from stringalign.align import Delete, Insert, Keep, Replace
from stringalign.evaluation import LineError


@pytest.mark.parametrize(
    "reference, predicted, line_error",
    [
        (
            "Hello, world!",
            "Hello, world!",
            LineError(
                reference="Hello, world!",
                prediction="Hello, world!",
                alignment=(Keep("Hello, world!"),),
                horisontal_segmentation_errors=(),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                case_errors=(),
            ),
        ),
        (
            "Hello, world!",
            "Hello, world",
            LineError(
                reference="Hello, world!",
                prediction="Hello, world",
                alignment=(Keep("Hello, world"), Insert("!")),
                horisontal_segmentation_errors=(Insert("!"),),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                case_errors=(),
            ),
        ),
        (
            "Hello, world!",
            "hello, world",
            LineError(
                reference="Hello, world!",
                prediction="hello, world",
                alignment=(Replace("h", "H"), Keep("ello, world"), Insert("!")),
                horisontal_segmentation_errors=(
                    Replace("h", "H"),
                    Insert("!"),
                ),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                case_errors=(Replace("h", "H"),),
            ),
        ),
        (
            "Hello, world!",
            "Helllo, world!",
            LineError(
                reference="Hello, world!",
                prediction="Helllo, world!",
                alignment=(Keep("He"), Delete("l"), Keep("llo, world!")),
                horisontal_segmentation_errors=(),
                character_duplication_errors=(Delete("l"),),
                removed_duplicate_character_errors=(),
                case_errors=(),
            ),
        ),
        (
            "Hello, world!",
            "Helo, world!",
            LineError(
                reference="Hello, world!",
                prediction="Helo, world!",
                alignment=(Keep("He"), Insert("l"), Keep("lo, world!")),
                horisontal_segmentation_errors=(),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(Insert("l"),),
                case_errors=(),
            ),
        ),
    ],
)
def test_from_strings_with_example(reference: str, predicted: str, line_error: LineError) -> None:
    assert LineError.from_strings(reference, predicted, tokenizer=None) == line_error
