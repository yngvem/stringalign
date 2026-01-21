import warnings
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from numbers import Number
from typing import Self, cast

import stringalign
from stringalign.align import AlignmentOperation, Kept, Replaced, align_strings
from stringalign.tokenize import Tokenizer

__all__ = ["CombinedAlignmentWarning", "StringConfusionMatrix"]


def sort_by_values(d: dict[str, float], reverse=False) -> dict[str, float]:
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))


def _is_combined_alignment(alignment: Iterable[AlignmentOperation], tokenizer: Tokenizer) -> bool:
    """Check if the alignment is combined, i.e., no adjacent operations can be merged."""
    for op in alignment:
        if isinstance(op, Kept) and next(iter(tokenizer(op.substring)), None) != op.substring:
            return True
        elif isinstance(op, Kept):
            continue

        op = op.generalize()
        if next(iter(tokenizer(op.reference)), "") != op.reference:
            return True
        if next(iter(tokenizer(op.predicted)), "") != op.predicted:
            return True

    return False


def _compute_f1_from_tpr_and_ppv(tpr: float, ppv: float) -> float:
    # If either tpr or ppv is 0, then the F1-score is zero.
    # However, the ppv or tpr can be NAN if any of the computations would involve dividing by zero.
    # Therefore, we need to explicitly return zero in this case to avoid return NAN (as 0 * NAN / (0 * NAN) = NAN).
    #
    # This can, e.g. happen if the model never predicts a given token. The positive predicted value, or precision
    # is defined as TP / (TP + FP), however, if the model e.g. never predicted ``ø``, then TP=0 AND FP=0, which results
    # in PPV = 0/0 = NAN
    # However, the F1 score for ``ø`` should be 0.
    if tpr == 0 or ppv == 0:
        return 0.0
    return (tpr * ppv) / (0.5 * (tpr + ppv))


class CombinedAlignmentWarning(UserWarning):
    """Used to warn when passing alignments with potentially combined operations to the confusion matrix."""


@dataclass(eq=True)
class StringConfusionMatrix:
    """A confusion-matrix like object that counts edit operations for aligned strings.

    The string confusion matrix counts the number of true positives, false positives and false negatives for two aligned
    strings. However, the number of true negatives does not make sense in the context of string alignment, as it would
    correspond to the number of times a token occurs in neither strings.

    We use the following definitions of true positives, false positives and false negatives:

    * **True positives:** The number of times a token occurs in the "same place" in both strings, i.e. the number of
      :class:`stringalign.align.Kept` operations with the given token as the substring.
    * **False positives:** The number of times a token occurs in the predicted string but not the reference, i.e. number
      of :class:`stringalign.align.Inserted` operations with the given token as the substring plus the number of
      :class:`stringalign.align.Replaced` operations with the given token as the predicted token.
    * **False negatives:** The number of times a token occurs in the reference string but not the predicted, i.e. number
      of :class:`stringalign.align.Deleted` operations with the given token as the substring plus the number of
      :class:`stringalign.align.Replaced` operations with the given token as the reference token.
    * **Edit count:** The number of edit operations (:class:`stringalign.align.Inserted`,
      :class:`stringalign.align.Deleted` or :class:`stringalign.align.Replaced`)

    In general, you should not initialize this class with the default constructor, but rather use some of the utility
    constructors:

    * :meth:`from_strings_and_alignment`
    * :meth:`from_strings`
    * :meth:`from_string_collections`
    * :meth:`get_empty`
    """

    true_positives: Counter[str]
    false_positives: Counter[str]  # Added tokens
    false_negatives: Counter[str]  # Removed/missed tokens
    edit_counts: Counter[AlignmentOperation]  # Count of each operation type
    # There is no true negatives when we compare strings.
    # Either, a character is in the string or it is not.

    @classmethod
    def from_strings_and_alignment(
        cls, reference: str, predicted: str, alignment: Iterable[AlignmentOperation], tokenizer: Tokenizer | None = None
    ) -> Self:
        """Create confusion matrix based on a reference string, a predicted string and their alignment.

        .. important::

            The string metrics are not well defined if we include combined alginments. This is because the true positive
            count etc. is not well defined for multi-token strings. For example, how many true positives is it for the
            ``'ll'`` substring in the string ``'llllll'``. The answer is most likely either 3 or 5 depending on whether
            we count overlapping substrings.

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
            ``stringalign.tokenize.DEFAULT_TOKENIZER`` is used instead, which by default is a grapheme cluster
            (character) tokenizer.

        Returns
        -------
        confusion_matrix : StringConfusionMatrix
            The confusion matrix.
        """
        if tokenizer is None:
            tokenizer = stringalign.tokenize.DEFAULT_TOKENIZER

        ref_iter = iter(tokenizer(reference))
        pred_iter = iter(tokenizer(predicted))

        true_positives: Counter[str] = Counter()
        false_positives: Counter[str] = Counter()
        false_negatives: Counter[str] = Counter()
        edit_counts: Counter[AlignmentOperation] = Counter()

        if _is_combined_alignment(alignment, tokenizer):
            warnings.warn(
                "The substrings of the alignment operation do not contain single tokens. This indicates that the"
                " alignments have either been combined, which means that the string confusion matrix is ill defined,"
                " and some metrics might be confusing or wrong. Alternatively, the your tokenizer might not provide"
                " atomic tokens, (i.e. the tokens can be tokenized again:"
                " `tokenize(tokenize(s)[0])[0] != tokenize(s)[0]`). If that is the case, then you may ignore this"
                " warning.",
                CombinedAlignmentWarning,
                stacklevel=2,
            )

        for op in alignment:
            if isinstance(op, Kept):
                for char in tokenizer(op.substring):
                    true_positives[next(ref_iter)] += 1
                    next(pred_iter)
                continue

            edit_counts[op] += 1

            op = cast(Replaced, op.generalize())
            for char in tokenizer(op.predicted):
                false_positives[char] += 1
                next(pred_iter)

            for char in tokenizer(op.reference):
                false_negatives[char] += 1
                next(ref_iter)
        return cls(
            true_positives=true_positives,
            false_positives=false_positives,
            false_negatives=false_negatives,
            edit_counts=edit_counts,
        )

    @classmethod
    def from_strings(cls, reference: str, predicted: str, tokenizer: Tokenizer | None = None) -> Self:
        """Create confusion matrix based on a reference string and a predicted string.

        .. note::

            This method will first align the strings and then create the confusion matrix.
            If you already have computed the alignment, you can use
            :meth:`StringConfusionMatrix.from_strings_and_alignment` instead.

        Parameters
        ----------
        reference
            The reference string, also known as gold standard or ground truth.
        predicted
            The string to align with the reference.
        tokenizer : optional
            A tokenizer that turns a string into an iterable of tokens. For this function, it is sufficient that it is a
            callable that turns a string into an iterable of tokens. If not provided, then
            ``stringalign.tokenize.DEFAULT_TOKENIZER`` is used instead, which by default is a grapheme cluster
            (character) tokenizer.

        Returns
        -------
        confusion_matrix : StringConfusionMatrix
            The confusion matrix.
        """
        if tokenizer is None:
            tokenizer = stringalign.tokenize.DEFAULT_TOKENIZER

        alignment = align_strings(reference, predicted, tokenizer=tokenizer)[0]
        return cls.from_strings_and_alignment(reference, predicted, alignment, tokenizer=tokenizer)

    @classmethod
    def from_string_collections(
        cls,
        references: Iterable[str],
        predictions: Iterable[str],
        tokenizer: Tokenizer | None = None,
    ) -> Self:
        """Create confusion matrix for many strings, summing statistics across pairs of references and predictions.

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

        Returns
        -------
        confusion_matrix : StringConfusionMatrix
            The confusion matrix.
        """
        if tokenizer is None:
            tokenizer = stringalign.tokenize.DEFAULT_TOKENIZER

        confusion_matrices = (
            cls.from_strings(reference, predicted, tokenizer=tokenizer)
            for reference, predicted in zip(references, predictions, strict=True)
        )
        return sum(confusion_matrices, start=cls.get_empty())

    @classmethod
    def get_empty(cls) -> Self:
        """Make an empty confusion matrix (equivalent to that of two empty strings).

        This can be used as a starting point for summing multiple confusion matrices when computing micro-averaged
        metrics over multiple string pairs.

        Returns
        -------
        confusion_matrix : StringConfusionMatrix
            An empty confusion matrix.
        """
        return cls(
            true_positives=Counter(),
            false_positives=Counter(),
            false_negatives=Counter(),
            edit_counts=Counter(),
        )

    def compute_true_positive_rate(self, aggregate_over: Iterable[str] | None = None) -> dict[str, float] | float:
        """Compute the true positive rate, also known as sensitivity or recall.

        The true positive rate is given by the number of true positives divided by the total number of positives.

        Parameters
        ----------
        aggregate_over : optional
            If provided, this function returns only a single number, which is the true positive rate for the tokens in
            the `aggregate_over` iterable. This is useful e.g. if you want to compute the true positive rate for a set
            of special characters.

        Returns
        -------
        true_positive_rate : dict[str, float] | float
            Either a dictionary that maps tokens to their true positive rate, or, if `aggregate_over` is provided, a
            single float that represent the true positive rate aggregated for the specified tokens.

        Examples
        --------

        If we compute the true positive rate without aggregating over tokens, we get a dict of true positive rates

        >>> cm = StringConfusionMatrix.from_strings("ostehøvel", "ostehovl")
        >>> cm.compute_true_positive_rate()
        {'o': 1.0, 's': 1.0, 't': 1.0, 'h': 1.0, 'v': 1.0, 'l': 1.0, 'e': 0.5, 'ø': 0.0}

        If we specify an iterable of tokens to aggregate over, we get the total true positive rate for those tokens. In
        this case, we aggregate over ``["æ", "ø", "å"]``, and the prediction did not find any of those tokens, so the
        true positive rate is zero.

        >>> cm.compute_true_positive_rate(aggregate_over=["æ", "ø", "å"])
        0.0

        The aggregated statistics is micro averaged, so the function counts the number of true and false negatives for
        all tokens, sums them and then computes the true positive rate.

        >>> cm = StringConfusionMatrix.from_strings("blåbær- og bringebærsyltetøy", "blabaer- og bringebærsyltetoy")
        >>> cm.compute_true_positive_rate(aggregate_over=["æ", "ø", "å"])
        0.25
        """
        if aggregate_over is not None and (aggregate_over := list(aggregate_over)):
            tp = sum(self.true_positives[c] for c in aggregate_over)
            fn = sum(self.false_negatives[c] for c in aggregate_over)
            if tp + fn == 0:
                return float("nan")

            return tp / (tp + fn)

        char_count = self.true_positives + self.false_negatives
        all_tokens = set(char_count) | set(self.false_positives)
        return sort_by_values(
            {key: self.true_positives[key] / char_count.get(key, float("nan")) for key in all_tokens},
            reverse=True,
        )

    compute_recall = compute_true_positive_rate
    compute_sensitivity = compute_true_positive_rate

    def compute_positive_predictive_value(self, aggregate_over: str | None = None) -> dict[str, float] | float:
        """Compute the positive predicted value, also known as precision.

        The positive predicted value is given by the number of true positives divided by the total number of predicted
        positives.

        Parameters
        ----------
        aggregate_over : optional
            If provided, this function returns only a single number, which is the positive predicted value for the
            tokens in the `aggregate_over` iterable. This is useful e.g. if you want to compute the  positive
            predicted value for a set of special characters. See
            :meth:`StringConfusionMatrix.compute_true_positive_rate` for examples of how this argument works.

        Returns
        -------
        positive_predictive_value : dict[str, float] | float
            Either a dictionary that maps tokens to their positive predicted value, or, if `aggregate_over` is provided,
            a single float that represent the positive predicted value aggregated for the specified tokens.
        """
        if aggregate_over:
            tp = sum(self.true_positives[c] for c in aggregate_over)
            fp = sum(self.false_positives[c] for c in aggregate_over)
            if tp + fp == 0:
                return float("nan")

            return tp / (tp + fp)

        predicted_positive = self.true_positives + self.false_positives
        all_tokens = set(predicted_positive) | set(self.false_negatives)
        return sort_by_values(
            {key: self.true_positives[key] / predicted_positive.get(key, float("nan")) for key in all_tokens},
            reverse=True,
        )

    compute_precision = compute_positive_predictive_value

    def compute_false_discovery_rate(self, aggregate_over: str | None = None) -> dict[str, float] | float:
        """Compute the false discovery rate.

        The false discovery rate is given by the number of false positives divided by the total number of predicted
        positives.

        Parameters
        ----------
        aggregate_over : optional
            If provided, this function returns only a single number, which is the false discovery rate for the
            tokens in the `aggregate_over` iterable. This is useful e.g. if you want to compute the false
            discovery rate for a set of special characters. See
            :meth:`StringConfusionMatrix.compute_true_positive_rate` for examples of how this argument works.

        Returns
        -------
        false_discovery_rate : dict[str, float] | float
            Either a dictionary that maps tokens to their false discovery rate, or, if `aggregate_over` is provided, a
            single float that represent the false discovery rate aggregated for the specified tokens.
        """
        if aggregate_over:
            tp = sum(self.true_positives[c] for c in aggregate_over)
            fp = sum(self.false_positives[c] for c in aggregate_over)
            if tp + fp == 0:
                return float("nan")

            return fp / (tp + fp)

        predicted_positive = self.true_positives + self.false_positives
        all_tokens = set(predicted_positive) | set(self.false_negatives)
        return sort_by_values(
            {key: self.false_positives[key] / predicted_positive[key] for key in all_tokens}, reverse=True
        )

    def compute_f1_score(self, aggregate_over: str | None = None) -> dict[str, float] | float:
        """Compute the F1 score, also known as the Dice score.

        The F1 score is given by the harmonic mean of the true positive rate and positive predictive value.
        Alternatively, you can interpret it as the number of true positives divided by the average number of predicted
        positives and the number of positives in the reference.

        Parameters
        ----------
        aggregate_over : optional
            If provided, this function returns only a single number, which is the f1 score aggregated for the tokens in
            the `aggregate_over` iterable. This is useful e.g. if you want to compute the false  discovery rate for a
            set of special characters. See :meth:`StringConfusionMatrix.compute_true_positive_rate` for examples of how
            this argument works.

        Returns
        -------
        f1_score : dict[str, float] | float
            Either a dictionary that maps tokens to their f1 score rate, or, if `aggregate_over`  is provided, a single
            float that represent the f1 score aggregated for the specified tokens.
        """
        tpr = self.compute_true_positive_rate(aggregate_over=aggregate_over)
        ppv = self.compute_positive_predictive_value(aggregate_over=aggregate_over)

        if aggregate_over:
            assert isinstance(tpr, Number) and isinstance(ppv, Number)
            return _compute_f1_from_tpr_and_ppv(tpr, ppv)

        assert isinstance(tpr, dict) and isinstance(ppv, dict)
        all_chars = set(self.true_positives) | set(self.false_positives) | set(self.false_negatives)
        tpr, ppv = defaultdict(int, tpr), defaultdict(int, ppv)
        return sort_by_values(
            {c: _compute_f1_from_tpr_and_ppv(tpr[c], ppv[c]) for c in all_chars},
            reverse=True,
        )

    compute_dice = compute_f1_score

    def compute_token_error_rate(self) -> float:
        """Compute the token error rate (a generalisation of CER and WER).

        The token error rate is the number of token edits divided by the total number of tokens in the reference.

        If the tokenizer tokenizes the string into characters, this is equivalent to the character error rate (CER).

        Returns
        -------
        token_error_rate : dict[str, float] | float
            The token error rate.
        """
        total_tokens = sum(self.true_positives.values()) + sum(self.false_negatives.values())
        total_edit_counts = sum(self.edit_counts.values())
        if total_edit_counts == 0 and total_tokens == 0:
            return 0.0
        elif total_tokens == 0:
            return float("inf")
        return total_edit_counts / total_tokens

    def __add__(self, other: Self) -> Self:
        """Create a new confusion matrix, adding the true positives, false positives, false negatives, and edit counts.

        We use this to compute micro-averaged metrics over multiple string pairs.

        Parameters
        ----------
        other
            The other confusion matrix.

        Returns
        -------
        confusion_matrix : StringConfusionMatrix
            A new confusion matrix where the number of true positive, false positive, false negatives and the edit
            counts are given by the sum of the corresponding attributes of the two added matrices.
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(
            true_positives=self.true_positives + other.true_positives,
            false_positives=self.false_positives + other.false_positives,
            false_negatives=self.false_negatives + other.false_negatives,
            edit_counts=self.edit_counts + other.edit_counts,
        )

    __radd__ = __add__
