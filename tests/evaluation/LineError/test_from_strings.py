import pytest
from stringalign.align import Delete, Insert, Keep, Replace, align_strings
from stringalign.evaluation import FrozenDict, LineError
from stringalign.tokenize import UnicodeWordTokenizer


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
                raw_alignment=tuple(align_strings("Hello, world!", "Hello, world!")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                case_errors=(),
                metadata=None,
                tokenizer=None,
            ),
        ),
        (
            "Hello, world!",
            "Hello, world",
            LineError(
                reference="Hello, world!",
                predicted="Hello, world",
                alignment=(Keep("Hello, world"), Insert("!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Hello, world")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(Insert("!"),),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                case_errors=(),
                metadata=None,
                tokenizer=None,
            ),
        ),
        (
            "Hello, world!",
            "hello, world",
            LineError(
                reference="Hello, world!",
                predicted="hello, world",
                alignment=(Replace("h", "H"), Keep("ello, world"), Insert("!")),
                raw_alignment=tuple(align_strings("Hello, world!", "hello, world")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(
                    Replace("h", "H"),
                    Insert("!"),
                ),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                case_errors=(Replace("h", "H"),),
                metadata=None,
                tokenizer=None,
            ),
        ),
        (
            "Hello, world!",
            "Helllo, world!",
            LineError(
                reference="Hello, world!",
                predicted="Helllo, world!",
                alignment=(Keep("He"), Delete("l"), Keep("llo, world!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Helllo, world!")[0]),
                unique_alignment=False,
                horisontal_segmentation_errors=(),
                character_duplication_errors=(Delete("l"),),
                removed_duplicate_character_errors=(),
                case_errors=(),
                metadata=None,
                tokenizer=None,
            ),
        ),
        (
            "Hello, world!",
            "Helo, world!",
            LineError(
                reference="Hello, world!",
                predicted="Helo, world!",
                alignment=(Keep("He"), Insert("l"), Keep("lo, world!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Helo, world!")[0]),
                unique_alignment=False,
                horisontal_segmentation_errors=(),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(Insert("l"),),
                case_errors=(),
                metadata=None,
                tokenizer=None,
            ),
        ),
        (  # With UnicodeWordTokenizer
            "Hello, world!",
            "Helo, world!",
            LineError(
                reference="Hello, world!",
                predicted="Helo, world!",
                alignment=(Replace("Helo", "Hello"), Keep("world")),
                raw_alignment=tuple(
                    align_strings("Hello, world!", "Helo, world!", tokenizer=UnicodeWordTokenizer())[0]
                ),
                unique_alignment=True,
                horisontal_segmentation_errors=(Replace("Helo", "Hello"),),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(Replace("Helo", "Hello"),),
                case_errors=(),
                metadata=None,
                tokenizer=UnicodeWordTokenizer(),
            ),
        ),
    ],
)
def test_from_strings_with_example(reference: str, predicted: str, line_error: LineError) -> None:
    assert LineError.from_strings(reference, predicted, tokenizer=line_error.tokenizer) == line_error


def test_from_strings_with_metadata():
    reference = "Hello, world!"
    predicted = "Helo, world!"
    metadata = {"a": 3}
    line_error = LineError(
        reference="Hello, world!",
        predicted="Helo, world!",
        alignment=(Keep("He"), Insert("l"), Keep("lo, world!")),
        raw_alignment=tuple(align_strings("Hello, world!", "Helo, world!")[0]),
        unique_alignment=False,
        horisontal_segmentation_errors=(),
        character_duplication_errors=(),
        removed_duplicate_character_errors=(Insert("l"),),
        case_errors=(),
        metadata=FrozenDict({"a": 3}),
        tokenizer=None,
    )

    assert LineError.from_strings(reference, predicted, tokenizer=None, metadata=metadata) == line_error
