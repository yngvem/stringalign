import pytest
from stringalign.align import Deleted, Inserted, Kept, Replaced, align_strings
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
                alignment=(Kept("Hello, world!"),),
                raw_alignment=tuple(align_strings("Hello, world!", "Hello, world!")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                diacritic_errors=(),
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
                alignment=(Kept("Hello, world"), Deleted("!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Hello, world")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(Deleted("!"),),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                diacritic_errors=(),
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
                alignment=(Replaced("H", "h"), Kept("ello, world"), Deleted("!")),
                raw_alignment=tuple(align_strings("Hello, world!", "hello, world")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(
                    Replaced("H", "h"),
                    Deleted("!"),
                ),
                character_duplication_errors=(),
                diacritic_errors=(),
                removed_duplicate_character_errors=(),
                case_errors=(Replaced("H", "h"),),
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
                alignment=(Kept("He"), Inserted("l"), Kept("llo, world!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Helllo, world!")[0]),
                unique_alignment=False,
                horisontal_segmentation_errors=(),
                character_duplication_errors=(Inserted("l"),),
                removed_duplicate_character_errors=(),
                diacritic_errors=(),
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
                alignment=(Kept("He"), Deleted("l"), Kept("lo, world!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Helo, world!")[0]),
                unique_alignment=False,
                horisontal_segmentation_errors=(),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(Deleted("l"),),
                diacritic_errors=(),
                case_errors=(),
                metadata=None,
                tokenizer=None,
            ),
        ),
        (
            "Hello, world!",
            "Helło, world!",
            LineError(
                reference="Hello, world!",
                predicted="Helło, world!",
                alignment=(Kept("Hel"), Replaced("l", "ł"), Kept("o, world!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Helło, world!")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(),
                diacritic_errors=(Replaced("l", "ł"),),
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
                alignment=(Replaced(reference="Hello", predicted="Helo"), Kept("world")),
                raw_alignment=tuple(
                    align_strings("Hello, world!", "Helo, world!", tokenizer=UnicodeWordTokenizer())[0]
                ),
                unique_alignment=True,
                horisontal_segmentation_errors=(Replaced(reference="Hello", predicted="Helo"),),
                character_duplication_errors=(),
                removed_duplicate_character_errors=(Replaced(reference="Hello", predicted="Helo"),),
                diacritic_errors=(),
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
        alignment=(Kept("He"), Deleted("l"), Kept("lo, world!")),
        raw_alignment=tuple(align_strings("Hello, world!", "Helo, world!")[0]),
        unique_alignment=False,
        horisontal_segmentation_errors=(),
        character_duplication_errors=(),
        removed_duplicate_character_errors=(Deleted("l"),),
        diacritic_errors=(),
        case_errors=(),
        metadata=FrozenDict({"a": 3}),
        tokenizer=None,
    )

    assert LineError.from_strings(reference, predicted, tokenizer=None, metadata=metadata) == line_error
