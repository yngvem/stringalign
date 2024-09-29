from pprint import pprint

import stringalign

reference = "heeei du er kul"
predicted = "hei du er cool"

alignment = stringalign.align.align_strings(reference, predicted)
confusion_matrix = stringalign.statistics.StringConfusionMatrix.from_strings_and_alignment(
    reference, predicted, alignment
)
merged_alignment = list(stringalign.align.aggregate_alignment(alignment))

print(reference)
print(predicted)
pprint(alignment)
pprint(merged_alignment)

print("Sensitivity:")
pprint(confusion_matrix.compute_sensitivity())
print("Precision:")
pprint(confusion_matrix.compute_precision())
print("F1-score:")
pprint(confusion_matrix.compute_f1_score())


print("Sensitivity (ku):")
print(confusion_matrix.compute_sensitivity("ku"))
print("Precision (ku):")
print(confusion_matrix.compute_precision("ku"))
print("F1-score (ku):")
print(confusion_matrix.compute_f1_score("ku"))
