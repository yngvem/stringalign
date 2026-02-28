import json
import pathlib

import meeteval

input_dir = pathlib.Path("ocr_results")
out_dir = pathlib.Path("output")

char_report_files = []
word_report_files = []

result = {}
error_rates = []
for ref_file in input_dir.glob("*.ref.txt"):
    name = ref_file.name.partition(".")[0]
    ref = (input_dir / f"{name}.ref.txt").read_text(encoding="utf-8")
    pred = (input_dir / f"{name}.pred.txt").read_text(encoding="utf-8")

    wer = meeteval.wer.wer.siso.siso_word_error_rate(
        reference=ref,
        hypothesis=pred,
    )
    result[name] = {"wer": wer.error_rate}
    error_rates.append(wer)

avg = meeteval.wer.combine_error_rates(error_rates)
result["overall"] = {"wer": avg.error_rate}

with open(out_dir / "result.json", "w") as f:
    json.dump(result, f, indent=2)
