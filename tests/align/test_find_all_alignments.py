import pytest
from stringalign.align import AlignmentOperation, Delete, Insert, Keep, Replace, find_all_alignments


@pytest.mark.parametrize(
    "reference, predicted, alignments",
    [
        (
            "ab",
            "ba",
            (
                (Replace("b", "a"), Replace("a", "b")),
                (Insert("a"), Keep("b"), Delete("a")),
                (Delete("b"), Keep("a"), Insert("b")),
            ),
        )
    ],
)
def test_find_all_alignments_with_examples(
    reference: str, predicted: str, alignments: tuple[tuple[AlignmentOperation, ...], ...]
) -> None:
    """All expected aligmments should be found."""
    all_aligments = tuple(find_all_alignments(reference, predicted))

    assert len(all_aligments) == len(alignments)
    assert set(all_aligments) == set(alignments)
