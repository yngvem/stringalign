from collections import Counter, defaultdict, deque
from collections.abc import Generator, Hashable, Iterator, Mapping
from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from typing import Any, Iterable, Literal, Self, TypeVar

import stringalign
from stringalign.align import (
    AlignmentOperation,
    AlignmentTuple,
    Kept,
    Replaced,
    align_strings,
    combine_alignment_ops,
)
from stringalign.error_classification.case_error import count_case_errors
from stringalign.error_classification.confusable_error import count_confusable_errors
from stringalign.error_classification.diacritic_error import count_diacritic_errors
from stringalign.error_classification.duplication_error import check_ngram_duplication_errors
from stringalign.normalize import StringNormalizer
from stringalign.statistics import StringConfusionMatrix
from stringalign.tokenize import Tokenizer
from stringalign.visualize import HtmlString, create_alignment_html

T = TypeVar("T")


def join_windows(center_string: str, previous_operation: Kept | None, next_operation: Kept | None) -> str:
    """Join the text in from the center alignment operation with the previous and next operation (if possible).

    Paramters
    ---------
    center_string
        The text in the center string, must come from an edit operation.
    previous_operation
        The previous alignment operation. Since the error classification algorithms use combined alignments, this is
        guaranteed to be a :class:`Kept`-operation or ``None``.
    next_operation
        The next alignment operation. Since the error classification algorithms use combined alignments, this is
        guaranteed to be a :class:`Kept`-operation or ``None``.
    """
    window_text = ""
    if previous_operation is not None:
        window_text += previous_operation.substring
    window_text += center_string
    if next_operation is not None:
        window_text += next_operation.substring
    return window_text


def check_operation_for_case_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
) -> int:
    """Check if this alignment operation is an edit due to mistaken casing.

    This function resolves resolves case errors by casefolding. This means that certain characters are changed even if
    they are lowercase already (like ``'ß'`` being changed into ``'ss'``).

    .. note::
        Error classification should be performed on combined alignment operations so edit operations and
        kept operations alternate.

    Parameters
    ----------
    previous_operation
        The previous alignment operation. If ``current_operation`` is the first alignment operation in an alignment,
        this is ``None``.
    current_operation
        The alignment operation to check for case errors.
    next_operation
        The next alignment operation. If ``current_operation`` is the last alignment operation in an alignment, this is
        ``None``.
    tokenizer
        The tokenizer used for the original alignment.

    Returns
    -------
    int:
        The number of edits that are due to mistaken diacritics.

    See also
    --------
    :func:`stringalign.error_classification.case_error.count_case_errors`
    """
    if not isinstance(current_operation, Replaced):
        return False
    current_operation = current_operation.generalize()
    assert isinstance(current_operation, Replaced)
    return count_case_errors(current_operation.reference, current_operation.predicted)


def check_operation_for_diacritic_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
) -> int:
    """Check if this alignment operation is an edit due to mistaken diacritics.

    This function resolves confusables with the ``"confusables"``-list as well (otherwise it would not be possible to
    remove the diacritics).

    .. note::
        Error classification should be performed on combined alignment operations so edit operations and
        kept operations alternate.

    Parameters
    ----------
    previous_operation
        The previous alignment operation. If ``current_operation`` is the first alignment operation in an alignment,
        this is ``None``
    current_operation
        The alignment operation to check for diacritic errors.
    next_operation
        The next alignment operation. If ``current_operation`` is the last alignment operation in an alignment, this is
        ``None``
    tokenizer
        The tokenizer used for the original alignment.

    Returns
    -------
    int:
        The number of edits that are due to mistaken diacritics.

    See also
    --------
    :func:`stringalign.error_classification.diacritic_error.count_diacritic_errors`
    """
    current_operation = current_operation.generalize()
    if isinstance(current_operation, Kept):
        return False

    return count_diacritic_errors(current_operation.reference, current_operation.predicted)


def check_operation_for_confusable_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
    *,
    tokenizer: Tokenizer,
) -> int:
    """Check if this alignment operation is an edit due to confusable characters.

    This function uses the ``"confusables"``-list. If you want to check with a different set of confusables, then you
    should use :func:`stringalign.error_classification.confusable_error.count_confusable_errors` directly.

    .. note::
        Error classification should be performed on combined alignment operations so edit operations and
        kept operations alternate.

    Parameters
    ----------
    previous_operation
        The previous alignment operation. If ``current_operation`` is the first alignment operation in an alignment,
        this is ``None``
    current_operation
        The alignment operation to check for confusable errors.
    next_operation
        The next alignment operation. If ``current_operation`` is the last alignment operation in an alignment, this is
        ``None``
    tokenizer
        The tokenizer used for the original alignment.

    Returns
    -------
    int:
        The number of edits that are due to confusable characters.

    See also
    --------
    :func:`stringalign.error_classification.confusable_error.count_confusable_errors`
    """
    current_operation = current_operation.generalize()
    if isinstance(current_operation, Kept):
        return False
    return count_confusable_errors(
        current_operation.reference,
        current_operation.predicted,
        tokenizer=tokenizer,
        consider_confusables="confusables",
    )


def check_operation_for_horizontal_segmentation_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
) -> bool:
    """Check if the alignment error is likely due to a horisontal segmentation error.

    This is checked by seeing if the alignment operation is an edit at the start or end of the string.

    .. note::
        Error classification should be performed on combined alignment operations so edit operations and
        kept operations alternate.

    Parameters
    ----------
    previous_operation
        The previous alignment operation. If ``current_operation`` is the first alignment operation in an alignment,
        this is ``None``
    current_operation
        The alignment operation to check for horisontal segmentation errors.
    next_operation
        The next alignment operation. If ``current_operation`` is the last alignment operation in an alignment, this is
        ``None``

    Returns
    -------
    bool:
        True if the alignment error is likely due to a horisontal segmentation error. Else false.
    """
    is_boundary = (previous_operation is None) or (next_operation is None)
    return is_boundary and not isinstance(current_operation, Kept)


def check_operation_for_ngram_duplication_error(
    previous_operation: AlignmentOperation | None,
    current_operation: AlignmentOperation,
    next_operation: AlignmentOperation | None,
    *,
    n: int,
    error_type: Literal["inserted", "deleted"] = "inserted",
    tokenizer: Tokenizer,
) -> bool:
    """Check if this alignment operation is an n-gram duplication error or missing duplicate n-gram error.

    This function checks if the only reason for the alignment operation is due to an n-gram duplication or missing
    duplicate n-gram.

    .. note::
        Error classification should be performed on combined alignment operations so edit operations and
        kept operations alternate.

    Parameters
    ----------
    previous_operation
        The previous alignment operation. If ``current_operation`` is the first alignment operation in an alignment,
        this is ``None``.
    current_operation
        The alignment operation to check for n-gram duplication errors.
    next_operation
        The next alignment operation. If ``current_operation`` is the last alignment operation in an alignment, this is
        ``None``.
    n
        The number of tokens in the n-grams we evaluate. For single token duplication errors, this should be 1.
    error_type
        ``"inserted"`` if we are checking for inserted duplicates and ``"deleted"`` if we are checking for deleted
        duplicates.
    tokenizer
        The tokenizer used for the original alignment.

    Returns
    -------
    bool:
        True if the only reason for the alignment operation is due to an n-gram duplication or missing
        duplicate n-gram. Else false.

    See also
    --------
    :func:`stringalign.error_classification.duplication_error.check_ngram_duplication_errors`
    """
    if isinstance(current_operation, Kept):
        return False
    current_operation = current_operation.generalize()
    assert isinstance(current_operation, Replaced)
    assert isinstance(next_operation, (Kept, type(None)))
    assert isinstance(previous_operation, (Kept, type(None)))

    window_text_reference = join_windows(current_operation.reference, previous_operation, next_operation)
    window_text_prediction = join_windows(current_operation.predicted, previous_operation, next_operation)
    return check_ngram_duplication_errors(
        window_text_reference, window_text_prediction, n=n, error_type=error_type, tokenizer=tokenizer
    )


def _safe_hash(value: Any) -> int:
    try:
        return hash(value)
    except TypeError:
        import pickle

        return hash(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))


class FrozenDict(Mapping[Hashable, Any]):
    """An immutable and hashable dictionary.

    Pickle is used to create hashes for non-hashable values.
    """

    def __init__(self, data: Mapping[Hashable, Any] | None = None):
        if not data:
            data = {}
        self._data = deepcopy(data)
        self._hash: int | None = None

    def __getitem__(self, key: Hashable) -> Any:
        return self._data[key]

    def __iter__(self) -> Iterator[Hashable]:
        return iter(self._data)

    def __contains__(self, value: Any) -> bool:
        return value in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __hash__(self) -> int:
        if self._hash is not None:
            return self._hash

        keys = tuple(self.keys())
        values = tuple(_safe_hash(v) for v in self.values())
        self._hash = hash((keys, values))
        return self._hash

    def __repr__(self):
        return f"{type(self).__name__}({self._data!r})"


@dataclass(frozen=True, slots=False)
class AlignmentError:
    """Utility data class that represents the errors for a single sample (reference/predicted pair)

    Parameters
    ----------
    reference
        The reference string, also known as gold standard and ground truth

    predicted
        The predicted string

    combined_alignment
        The combined alignment for the reference and predicted string

    raw_alignment
        The uncombined alignment for the reference and predicted string

    unique_alignment
        Boolean flag which is true if the alignment is unique.

    horisontal_segmentation_errors
        The alignment operations that likely are wrong due to segmentation errors. Corresponds to edits in the start or
        end of the string.

    token_duplication_errors
        Alignment operations that correspond to tokens that were repeated more times in the prediction than in the
        reference.

    removed_duplicate_token_errors
        Alignment operations that correspond to tokens that were repeated fewer times in the prediction than in the
        reference.

    diacritic_errors
        Alignment operations that correspond to diacritics being added or removed (e.g. ``"ë" -> "e"``).

    confusable_errors
        Alignment operations that correspond to confusable tplems being predicted.

    case_errors
        Alignment operations that correspond to case errors (i.e. errors that are resolved by casefolding the strings).

    metadata
        Optional metadata to include with the line error, useful if you e.g. want to include a text line ID.

    tokenizer
        The tokenizer used prior to alignment. Included for reproducibility purposes.
    """

    reference: str
    predicted: str
    combined_alignment: AlignmentTuple
    raw_alignment: AlignmentTuple
    unique_alignment: bool

    horisontal_segmentation_errors: AlignmentTuple
    token_duplication_errors: AlignmentTuple
    removed_duplicate_token_errors: AlignmentTuple
    diacritic_errors: AlignmentTuple
    confusable_errors: AlignmentTuple
    case_errors: AlignmentTuple

    metadata: FrozenDict | None
    tokenizer: Tokenizer | None

    def summarise(self) -> dict[Hashable, Hashable]:
        """Convert this utility class to a dictionary, where the error classifications are converted to booleans.

        This is useful if we, for example, want to know the number of many samples with at least one suspected diacritic
        error. However, it removes information about what the errors might be.

        Returns
        -------
        summary : dict[Hashable, Hashable]
        """
        metadata = self.metadata
        if metadata is None:
            metadata = FrozenDict()

        return {
            "reference": self.reference,
            "predicted": self.predicted,
            "horisontal_segmentation_error": bool(self.horisontal_segmentation_errors),
            "token_duplication_error": bool(self.token_duplication_errors),
            "removed_duplicate_token_error": bool(self.removed_duplicate_token_errors),
            "diacritic_error": bool(self.diacritic_errors),
            "confusable_error": bool(self.confusable_errors),
            "case_error": bool(self.case_errors),
            **metadata,
        }

    @cached_property
    def confusion_matrix(self) -> StringConfusionMatrix:
        """The string confusion matrix for this string pair.

        Returns
        -------
        string_confusion_matrix : StringConfusionMatrix
        """
        return StringConfusionMatrix.from_strings_and_alignment(
            reference=self.reference, predicted=self.predicted, alignment=self.raw_alignment, tokenizer=self.tokenizer
        )

    @classmethod
    def from_strings(
        cls,
        reference: str,
        predicted: str,
        tokenizer: Tokenizer | None,
        metadata: Mapping[Hashable, Hashable] | None = None,
    ) -> Self:
        """
        Create a AlignmentError based on a reference string and a predicted string given a tokenizer.

        Parameters
        ----------
        reference
            The reference string, also known as gold standard or ground truth.
        predicted
            The string to align with the reference.
        alignment
            An optimal alignment for these strings
        tokenizer : optional
            A tokenizer that turns a string into an iterable of tokens. For this function, it is sufficient that it is a
            callable that turns a string into an iterable of tokens. If not provided, then
            ``stringalign.tokenize.DEFAULT_TOKENIZER`` is used instead, which by default is a grapheme cluster (character)
            tokenizer.
        metadata
            Additional metadata about the sample, e.g. sample id.


        Returns
        -------
        alignment_error : AlignmentError
            The AlignmentError object.
        """
        if tokenizer is None:
            tokenizer = stringalign.tokenize.DEFAULT_TOKENIZER

        raw_alignment, unique_alignment = align_strings(reference, predicted, tokenizer=tokenizer)
        combined_alignment = tuple(combine_alignment_ops(raw_alignment, tokenizer=tokenizer))
        if metadata is not None:
            frozen_metadata = FrozenDict(metadata)
        else:
            frozen_metadata = None

        if not combined_alignment:
            return cls(
                reference=reference,
                predicted=predicted,
                combined_alignment=tuple(),
                raw_alignment=tuple(),
                unique_alignment=True,
                horisontal_segmentation_errors=tuple(),
                token_duplication_errors=tuple(),
                removed_duplicate_token_errors=tuple(),
                diacritic_errors=tuple(),
                confusable_errors=tuple(),
                case_errors=tuple(),
                metadata=frozen_metadata,
                tokenizer=tokenizer,
            )

        alignment_iterator = iter(combined_alignment)
        window: deque[AlignmentOperation | None] = deque(maxlen=3)
        window.append(None)
        window.append(next(alignment_iterator))

        horisontal_segmentation_errors = []
        token_duplication_errors = []
        removed_duplicate_token_errors = []
        diacritic_errors = []
        confusable_errors = []
        case_errors = []
        op: AlignmentOperation | None
        for op in chain(alignment_iterator, (None, None)):
            window.append(op)
            if window[1] is None:
                break

            if check_operation_for_horizontal_segmentation_error(window[0], window[1], window[2]):
                horisontal_segmentation_errors.append(window[1])
            if check_operation_for_ngram_duplication_error(
                window[0], window[1], window[2], n=1, error_type="inserted", tokenizer=tokenizer
            ):
                token_duplication_errors.append(window[1])
            if check_operation_for_ngram_duplication_error(
                window[0], window[1], window[2], n=1, error_type="deleted", tokenizer=tokenizer
            ):
                removed_duplicate_token_errors.append(window[1])
            if check_operation_for_diacritic_error(window[0], window[1], window[2]):
                diacritic_errors.append(window[1])
            if check_operation_for_confusable_error(window[0], window[1], window[2], tokenizer=tokenizer):
                confusable_errors.append(window[1])
            if check_operation_for_case_error(window[0], window[1], window[2]):
                case_errors.append(window[1])

        return cls(
            reference=reference,
            predicted=predicted,
            combined_alignment=combined_alignment,
            raw_alignment=tuple(raw_alignment),
            unique_alignment=unique_alignment,
            horisontal_segmentation_errors=tuple(horisontal_segmentation_errors),
            token_duplication_errors=tuple(token_duplication_errors),
            removed_duplicate_token_errors=tuple(removed_duplicate_token_errors),
            diacritic_errors=tuple(diacritic_errors),
            confusable_errors=tuple(confusable_errors),
            case_errors=tuple(case_errors),
            metadata=frozen_metadata,
            tokenizer=tokenizer,
        )

    def visualize(self, which: Literal["raw", "combined"] = "raw", space_alignment_ops: bool = False) -> HtmlString:
        """Visualize the alignment (for Jupyter Notebooks).

        This is a simple wrapper around :func:`stringalign.visualize.create_alignment_html`. Use that function if you
        want to customise the visualisation further.

        Parameters
        ----------
        which
            If ``which="raw"``, then the raw alignment is visualised and if ``which="combined"`` then the combined
            alignment is visualised.
        space_alignment_ops
            If this is True, then there will be a small space between each alignment operation.

        Returns
        -------
        HtmlString
            A special string type that is interpreted as HTML by Jupyter. It contains HTML for visualising the specified
            alignment.
        """
        if which == "raw":
            alignment = self.raw_alignment
        else:
            alignment = self.combined_alignment

        return create_alignment_html(alignment=alignment, space_alignment_ops=space_alignment_ops)

    def __repr__(self) -> str:
        return f"LineError('{self.reference}', '{self.predicted}', metadata={self.metadata})"

    __str__ = __repr__


# TODO: consider what we want to do with property docstrings versus attribute docstrings
@dataclass(frozen=True, slots=False)
class TranscriptionEvaluator:
    # TODO consider changing this name
    """Utility class for evaluating all samples in a dataset.

    Parameters
    ----------
    references:
        Reference strings
    predictions:
        Strings to align with corresponding references.
    alignment_errors:
        Alignment errors, one per sample.
    """

    references: tuple[str, ...]
    predictions: tuple[str, ...]
    alignment_errors: tuple[AlignmentError, ...]

    def dump(self) -> list[dict[Hashable, Hashable]]:
        """Convert the alignment errors to dictionaries, where the error classifications are converted to booleans.

        This is useful if we, for example, want to know the number of many samples with at least one suspected diacritic
        error. However, it removes information about what the errors might be.

        Returns
        -------
        summary : list[dict[Hashable, Hashable]]

        """
        return [le.summarise() for le in self.alignment_errors]

    @property
    def horisontal_segmentation_errors(self) -> Generator[AlignmentError, None, None]:
        """:class:`AlignmentError` instances that contain at least one edit due to a segmentation error.

        An alignment is said to contain a horisontal segmentation error if there is an edit at the start or end of the
        alignment. See :func:`check_operation_for_horizontal_segmentation_error` for more information.

        Yields
        ------
        AlignmentError
        """
        return (err for err in self.alignment_errors if err.horisontal_segmentation_errors)

    @property
    def token_duplication_errors(self) -> Generator[AlignmentError, None, None]:
        """:class:`AlignmentError` instances that contain at least one edit due to a duplication error.

        An alignment is said to contain a duplication error if at least one token is duplicated in the prediction
        where it is not duplicated in the reference. For example, transcribing ``"hello"`` as ``"helllo"`` would
        correspond to a duplication error. See :func:`check_operation_for_ngram_duplication_error` for more
        information.

        Yields
        ------
        AlignmentError
        """
        return (err for err in self.alignment_errors if err.token_duplication_errors)

    @property
    def removed_duplicate_token_errors(self) -> Generator[AlignmentError, None, None]:
        """:class:`AlignmentError` instances that contain at least one edit due to a missed duplicated token.

        An alignment is said to contain a removed duplicate token error if at least one token is duplicated in the
        reference where it is duplicated in the prediction. For example, transcribing ``"hello"`` as ``"helo"`` would
        correspond to a removed duplicate token error. See :func:`check_operation_for_ngram_duplication_error` and
        :func:`stringalign.error_classification.duplication_error.check_ngram_duplication_errors` for more information.

        Yields
        ------
        AlignmentError
        """
        return (err for err in self.alignment_errors if err.removed_duplicate_token_errors)

    @property
    def diacritic_errors(self) -> Generator[AlignmentError, None, None]:
        """:class:`AlignmentError` instances that contain at least one edit due to wrongly placed or missing diacritics.

        An alignment is said to contain a diacritic error if at least one of the edits would change into a Kept if we
        remove all diacritics. Note that this function also resolves confusables to be able to correctly remove
        diacritics. See :func:`check_operation_for_diacritic_error` and
        :func:`stringalign.error_classification.diacritic_error.count_diacritic_errors` for more information.

        Yields
        ------
        AlignmentError
        """
        return (err for err in self.alignment_errors if err.diacritic_errors)

    @property
    def confusable_errors(self) -> Generator[AlignmentError, None, None]:
        """:class:`AlignmentError` instances that contain at least one edit from interchanging confusable characters.

        An alignment is said to contain a confusable error if at least one of the edits would change into a Kept if we
        resolve confusables. See :func:`check_operation_for_confusable_error` and
        :func:`stringalign.error_classification.confusable_error.count_confusable_errors` for more information.

        Yields
        ------
        AlignmentError
        """
        return (err for err in self.alignment_errors if err.confusable_errors)

    @property
    def case_errors(self) -> Generator[AlignmentError, None, None]:
        """:class:`AlignmentError` instances that contain at least one edit from mixing upper- and lower-case letters.

        An alignment is said to contain a case error if at least one of the edits would change into a Kept if we
        case fold the contents. See :func:`check_operation_for_case_error` and
        :func:`stringalign.error_classification.confusable_error.count_case_errors` for more information.

        Yields
        ------
        AlignmentError
        """
        return (err for err in self.alignment_errors if err.case_errors)

    @property
    def not_unique_alignments(self) -> Generator[AlignmentError]:
        """:class:`AlignmentError` instances whose alignments are not unique.

        This is useful to assess why alignments might not be unique. For example, whether the non-uniqueness stems from
        duplicated or transposed tokens.

        Yields
        ------
        AlignmentError
        """
        return (err for err in self.alignment_errors if not err.unique_alignment)

    @cached_property
    def alignment_operation_counts(self) -> Counter[AlignmentOperation]:
        """Count the number of times each alignment operation occurs.

        This is useful to identify common mistakes for a transcription model.
        """
        return Counter(op for err in self.alignment_errors for op in err.combined_alignment)

    @cached_property
    def confusion_matrix(self) -> StringConfusionMatrix:
        """The micro-averaged confusion matrix for all samples."""
        return sum((ae.confusion_matrix for ae in self.alignment_errors), start=StringConfusionMatrix.get_empty())

    @cached_property
    def alignment_error_raw_lookup(self) -> dict[AlignmentOperation, frozenset[AlignmentError]]:
        """Mapping from alignment operations to sets of :class:`AlignmentError` with that operation in the raw alignment.

        This function is used to find all samples that contain specific alignment operations. It can, for example be
        used to identify all lines that contain a specific error a transcription model makes, which again can be useful
        for finding mistakes in the references.
        """
        out = defaultdict(set)
        for alignment_error in self.alignment_errors:
            for alignment_op in alignment_error.raw_alignment:
                out[alignment_op].add(alignment_error)

        return {k: frozenset(v) for k, v in out.items()}

    @cached_property
    def alignment_error_combined_lookup(self) -> dict[AlignmentOperation, frozenset[AlignmentError]]:
        """Mapping from alignment operations to sets of :class:`AlignmentError` with that operation in the combined alignment.

        This function is used to find all samples that contain specific alignment operations. It can, for example be
        used to identify all lines that contain a specific error a transcription model makes, which again can be useful
        for finding mistakes in the references.
        """
        out = defaultdict(set)
        for alignment_error in self.alignment_errors:
            for alignment_op in alignment_error.combined_alignment:
                out[alignment_op].add(alignment_error)

        return {k: frozenset(v) for k, v in out.items()}

    @cached_property
    def false_positive_lookup(self) -> dict[str, frozenset[AlignmentError]]:
        """Mapping from tokens to sets of :class:`AlignmentError`s with that false positive token"""
        out = defaultdict(set)
        for alignment_error in self.alignment_errors:
            for token in alignment_error.confusion_matrix.false_positives:
                out[token].add(alignment_error)

        return {k: frozenset(v) for k, v in out.items()}

    @cached_property
    def false_negative_lookup(self) -> dict[str, frozenset[AlignmentError]]:
        """Mapping from tokens to sets of :class:`AlignmentError`s with that false negative token"""
        out = defaultdict(set)
        for alignment_error in self.alignment_errors:
            for token in alignment_error.confusion_matrix.false_negatives:
                out[token].add(alignment_error)

        return {k: frozenset(v) for k, v in out.items()}

    @classmethod
    def from_strings(
        cls,
        references: Iterable[str],
        predictions: Iterable[str],
        tokenizer: Tokenizer | None = None,
        metadata: Iterable[Mapping[Hashable, Hashable] | None] | None = None,
    ) -> Self:
        """Creates a transcription evaluator from iterables containing references and predictions.

        Parameters
        ----------
        references
            Iterable containing the reference strings.
        predictions
            Iterable containing The strings to align with the references.
        tokenizer : optional
            A tokenizer that turns a string into an iterable of tokens. For this function, it is sufficient that it is a
            callable that turns a string into an iterable of tokens. If not provided, then
            ``stringalign.tokenize.DEFAULT_TOKENIZER`` is used instead, which by default is a grapheme cluster
            (character) tokenizer.
        metadata
            Additional metadata about the sample, e.g. sample id.

        Returns
        -------
        transcription_evaluator: TranscriptionEvaluator
        """
        references = tuple(references)
        predictions = tuple(predictions)
        if metadata is None:
            metadata = tuple(None for _ in references)

        alignment_errors = tuple(
            AlignmentError.from_strings(reference, prediction, tokenizer, metadata=metadata)
            for reference, prediction, metadata in zip(references, predictions, metadata, strict=True)
        )

        return cls(
            references=references,
            predictions=predictions,
            alignment_errors=alignment_errors,
        )

    def __len__(self) -> int:
        """The number of samples in the transcription."""
        return len(self.alignment_errors)

    def __repr__(self) -> str:
        return f"TranscriptionEvaluator(len={len(self)})"

    __str__ = __repr__
