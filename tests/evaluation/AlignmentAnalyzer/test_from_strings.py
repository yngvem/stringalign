import pytest
from stringalign.align import Deleted, Inserted, Kept, Replaced, align_strings
from stringalign.evaluation import AlignmentAnalyzer, FrozenDict
from stringalign.tokenize import DEFAULT_TOKENIZER, UnicodeWordTokenizer


@pytest.mark.parametrize(
    "reference, predicted, alignment_analyzer",
    [
        (
            "Hello, world!",
            "Hello, world!",
            AlignmentAnalyzer(
                reference="Hello, world!",
                predicted="Hello, world!",
                combined_alignment=(Kept("Hello, world!"),),
                raw_alignment=tuple(align_strings("Hello, world!", "Hello, world!")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(),
                token_duplication_errors=(),
                removed_duplicate_token_errors=(),
                diacritic_errors=(),
                confusable_errors=(),
                case_errors=(),
                metadata=None,
                tokenizer=DEFAULT_TOKENIZER,
            ),
        ),
        (
            "Hello, world!",
            "Hello, world",
            AlignmentAnalyzer(
                reference="Hello, world!",
                predicted="Hello, world",
                combined_alignment=(Kept("Hello, world"), Deleted("!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Hello, world")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(Deleted("!"),),
                token_duplication_errors=(),
                removed_duplicate_token_errors=(),
                diacritic_errors=(),
                confusable_errors=(),
                case_errors=(),
                metadata=None,
                tokenizer=DEFAULT_TOKENIZER,
            ),
        ),
        (
            "Hello, world!",
            "hello, world",
            AlignmentAnalyzer(
                reference="Hello, world!",
                predicted="hello, world",
                combined_alignment=(Replaced("H", "h"), Kept("ello, world"), Deleted("!")),
                raw_alignment=tuple(align_strings("Hello, world!", "hello, world")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(
                    Replaced("H", "h"),
                    Deleted("!"),
                ),
                token_duplication_errors=(),
                diacritic_errors=(),
                removed_duplicate_token_errors=(),
                case_errors=(Replaced("H", "h"),),
                confusable_errors=(),
                metadata=None,
                tokenizer=DEFAULT_TOKENIZER,
            ),
        ),
        (
            "Hello, world!",
            "Helllo, world!",
            AlignmentAnalyzer(
                reference="Hello, world!",
                predicted="Helllo, world!",
                combined_alignment=(Kept("He"), Inserted("l"), Kept("llo, world!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Helllo, world!")[0]),
                unique_alignment=False,
                horisontal_segmentation_errors=(),
                token_duplication_errors=(Inserted("l"),),
                removed_duplicate_token_errors=(),
                diacritic_errors=(),
                confusable_errors=(),
                case_errors=(),
                metadata=None,
                tokenizer=DEFAULT_TOKENIZER,
            ),
        ),
        (
            "Hello, world!",
            "Helo, world!",
            AlignmentAnalyzer(
                reference="Hello, world!",
                predicted="Helo, world!",
                combined_alignment=(Kept("He"), Deleted("l"), Kept("lo, world!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Helo, world!")[0]),
                unique_alignment=False,
                horisontal_segmentation_errors=(),
                token_duplication_errors=(),
                removed_duplicate_token_errors=(Deleted("l"),),
                diacritic_errors=(),
                confusable_errors=(),
                case_errors=(),
                metadata=None,
                tokenizer=DEFAULT_TOKENIZER,
            ),
        ),
        (
            "Hello, world!",
            "Helło, world!",
            AlignmentAnalyzer(
                reference="Hello, world!",
                predicted="Helło, world!",
                combined_alignment=(Kept("Hel"), Replaced("l", "ł"), Kept("o, world!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Helło, world!")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(),
                token_duplication_errors=(),
                removed_duplicate_token_errors=(),
                diacritic_errors=(Replaced("l", "ł"),),
                confusable_errors=(),
                case_errors=(),
                metadata=None,
                tokenizer=DEFAULT_TOKENIZER,
            ),
        ),
        (
            "Hello, world!",
            "Hel1o, world!",
            AlignmentAnalyzer(
                reference="Hello, world!",
                predicted="Hel1o, world!",
                combined_alignment=(Kept("Hel"), Replaced("l", "1"), Kept("o, world!")),
                raw_alignment=tuple(align_strings("Hello, world!", "Hel1o, world!")[0]),
                unique_alignment=True,
                horisontal_segmentation_errors=(),
                token_duplication_errors=(),
                removed_duplicate_token_errors=(),
                diacritic_errors=(),
                confusable_errors=(Replaced("l", "1"),),
                case_errors=(),
                metadata=None,
                tokenizer=DEFAULT_TOKENIZER,
            ),
        ),
        (  # With UnicodeWordTokenizer
            "Hello, world!",
            "Helo, world!",
            AlignmentAnalyzer(
                reference="Hello, world!",
                predicted="Helo, world!",
                combined_alignment=(Replaced(reference="Hello", predicted="Helo"), Kept("world")),
                raw_alignment=tuple(
                    align_strings("Hello, world!", "Helo, world!", tokenizer=UnicodeWordTokenizer())[0]
                ),
                unique_alignment=True,
                horisontal_segmentation_errors=(Replaced(reference="Hello", predicted="Helo"),),
                token_duplication_errors=(),
                removed_duplicate_token_errors=(),
                diacritic_errors=(),
                confusable_errors=(),
                case_errors=(),
                metadata=None,
                tokenizer=UnicodeWordTokenizer(),
            ),
        ),
    ],
)
def test_from_strings_with_example(reference: str, predicted: str, alignment_analyzer: AlignmentAnalyzer) -> None:
    assert (
        AlignmentAnalyzer.from_strings(reference, predicted, tokenizer=alignment_analyzer.tokenizer)
        == alignment_analyzer
    )


def test_from_strings_with_metadata():
    reference = "Hello, world!"
    predicted = "Helo, world!"
    metadata = {"a": 3}
    alignment_analyzer = AlignmentAnalyzer(
        reference="Hello, world!",
        predicted="Helo, world!",
        combined_alignment=(Kept("He"), Deleted("l"), Kept("lo, world!")),
        raw_alignment=tuple(align_strings("Hello, world!", "Helo, world!")[0]),
        unique_alignment=False,
        horisontal_segmentation_errors=(),
        token_duplication_errors=(),
        removed_duplicate_token_errors=(Deleted("l"),),
        diacritic_errors=(),
        confusable_errors=(),
        case_errors=(),
        metadata=FrozenDict({"a": 3}),
        tokenizer=DEFAULT_TOKENIZER,
    )

    assert (
        AlignmentAnalyzer.from_strings(reference, predicted, tokenizer=DEFAULT_TOKENIZER, metadata=metadata)
        == alignment_analyzer
    )


def test_from_empty_strings() -> None:
    alignment_analyzer1 = AlignmentAnalyzer.from_strings("", "", tokenizer=DEFAULT_TOKENIZER)
    alignment_analyzer2 = AlignmentAnalyzer(
        reference="",
        predicted="",
        combined_alignment=(),
        raw_alignment=(),
        unique_alignment=True,
        horisontal_segmentation_errors=(),
        token_duplication_errors=(),
        removed_duplicate_token_errors=(),
        diacritic_errors=(),
        confusable_errors=(),
        case_errors=(),
        metadata=None,
        tokenizer=DEFAULT_TOKENIZER,
    )
    assert alignment_analyzer1 == alignment_analyzer2
