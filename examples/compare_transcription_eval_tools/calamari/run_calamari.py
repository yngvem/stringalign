import json
import pathlib

import evaluate

input_dir = pathlib.Path("ocr_results")
out_dir = pathlib.Path("output")

char_report_files = []
word_report_files = []

all_ref = {}
all_pred = {}

result = {}
for i, ref_file in enumerate(input_dir.glob("*.ref.txt")):
    print(f"Analysing file {i}")
    name = ref_file.name.partition(".")[0]
    ref = {name: (input_dir / f"{name}.ref.txt").read_text(encoding="utf-8")}
    pred = {name: (input_dir / f"{name}.pred.txt").read_text(encoding="utf-8")}

    all_ref |= ref
    all_pred |= pred

    result[name] = evaluate.Evaluator().evaluate(gt_data=ref, pred_data=pred)

result["overall"] = evaluate.Evaluator().evaluate(gt_data=all_ref, pred_data=all_pred)

with open(out_dir / "result.json", "w") as f:
    json.dump(result, f, indent=2)
