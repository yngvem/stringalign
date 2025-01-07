from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from numbers import Number
from typing import Self, cast

from stringalign.align import AlignmentOperation, Keep, Replace, aggregate_alignment, align_strings
from stringalign.tokenize import GraphemeClusterTokenizer, Tokenizer


def sort_by_values(d: dict[str, float], reverse=False) -> dict[str, float]:
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))


@dataclass(eq=True)
class StringConfusionMatrix:
    true_positives: Counter[str]
    false_positives: Counter[str]  # Added characters
    false_negatives: Counter[str]  # Removed/missed characters
    edit_counts: Counter[AlignmentOperation]  # Count of each operation type
    # There is no true negatives when we compare strings.
    # Either, a character is in the string or it is not.

    @classmethod
    def from_strings_and_alignment(
        cls, reference: str, predicted: str, alignment: Iterable[AlignmentOperation], tokenizer: Tokenizer | None = None
    ) -> Self:
        if tokenizer is None:
            tokenizer = GraphemeClusterTokenizer()

        ref_iter = iter(tokenizer(reference))
        pred_iter = iter(tokenizer(predicted))

        true_positives: Counter[str] = Counter()
        false_positives: Counter[str] = Counter()
        false_negatives: Counter[str] = Counter()
        edit_counts: Counter[AlignmentOperation] = Counter()
        for op in alignment:
            if isinstance(op, Keep):
                for char in tokenizer(op.substring):
                    true_positives[next(ref_iter)] += 1
                    next(pred_iter)
                continue

            edit_counts[op] += 1

            op = cast(Replace, op.generalize())
            for char in tokenizer(op.substring):
                false_positives[char] += 1
                next(pred_iter)

            for char in tokenizer(op.replacement):
                false_negatives[char] += 1
                next(ref_iter)
        return cls(
            true_positives=true_positives,
            false_positives=false_positives,
            false_negatives=false_negatives,
            edit_counts=edit_counts,
        )

    @classmethod
    def from_strings(
        cls, reference: str, predicted: str, tokenizer: Tokenizer | None = None, aggregate: bool = False
    ) -> Self:
        if tokenizer is None:
            tokenizer = GraphemeClusterTokenizer()

        alignment = align_strings(reference, predicted, tokenizer=tokenizer)[0]
        if aggregate:
            alignment = list(aggregate_alignment(alignment))
        return cls.from_strings_and_alignment(reference, predicted, alignment, tokenizer=tokenizer)

    @classmethod
    def get_empty(cls) -> Self:
        return cls(
            true_positives=Counter(),
            false_positives=Counter(),
            false_negatives=Counter(),
            edit_counts=Counter(),
        )

    def compute_true_positive_rate(self, aggregate_over: str | None = None) -> dict[str, float] | float:
        """The number of true positives divided by the total number of positives"""
        if aggregate_over:
            tp = sum(self.true_positives[c] for c in aggregate_over)
            fn = sum(self.false_negatives[c] for c in aggregate_over)

            return tp / (tp + fn)

        char_count = self.true_positives + self.false_negatives
        return sort_by_values({key: self.true_positives[key] / char_count[key] for key in char_count}, reverse=True)

    compute_recall = compute_true_positive_rate
    compute_sensitivity = compute_true_positive_rate

    def compute_positive_predictive_value(self, aggregate_over: str | None = None) -> dict[str, float] | float:
        """The number of true positives divided by the total number of predicted positives

        Note that the false discovery rate is omitted for characters that have a true positive count of zero.
        """
        if aggregate_over:
            tp = sum(self.true_positives[c] for c in aggregate_over)
            fp = sum(self.false_positives[c] for c in aggregate_over)

            return tp / (tp + fp)

        predicted_positive = self.true_positives + self.false_positives
        return sort_by_values(
            {key: self.true_positives[key] / predicted_positive[key] for key in self.true_positives}, reverse=True
        )

    compute_precision = compute_positive_predictive_value

    def compute_false_discovery_rate(self, aggregate_over: str | None = None) -> dict[str, float] | float:
        """The number of false positives divided by the total number of predicted positives

        Note that the false discovery rate is omitted for characters that have a false positive count of zero.
        """
        if aggregate_over:
            tp = sum(self.true_positives[c] for c in aggregate_over)
            fp = sum(self.false_positives[c] for c in aggregate_over)

            return fp / (tp + fp)

        predicted_positive = self.true_positives + self.false_positives
        return sort_by_values(
            {key: self.false_positives[key] / predicted_positive[key] for key in self.false_positives}, reverse=True
        )

    def compute_f1_score(self, aggregate_over: str | None = None) -> dict[str, float] | float:
        """The harmonic mean of the true positive rate and positive predictive value."""
        tpr = self.compute_true_positive_rate(aggregate_over=aggregate_over)
        ppv = self.compute_positive_predictive_value(aggregate_over=aggregate_over)

        if aggregate_over:
            assert isinstance(tpr, Number) and isinstance(ppv, Number)
            return (tpr * ppv) / (0.5 * (tpr + ppv))

        assert isinstance(tpr, dict) and isinstance(ppv, dict)
        all_chars = set(self.true_positives) | set(self.false_positives) | set(self.false_negatives)
        tpr, ppv = defaultdict(int, tpr), defaultdict(int, ppv)
        return sort_by_values(
            {
                c: (tpr[c] * ppv[c])
                / (0.5 * (tpr[c] + ppv[c] or 1))  # or 1 avoids division by 0, the value is 0 anyways
                for c in all_chars
            },
            reverse=True,
        )

    compute_dice = compute_f1_score

    def __add__(self, other: Self) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(
            true_positives=self.true_positives + other.true_positives,
            false_positives=self.false_positives + other.false_positives,
            false_negatives=self.false_negatives + other.false_negatives,
            edit_counts=self.edit_counts + other.edit_counts,
        )

    __radd__ = __add__
