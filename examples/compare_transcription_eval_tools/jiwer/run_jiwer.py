# /// script
# requires-python = "==3.14.*"
# dependencies = ["jiwer==4.0.0"]
# ///

import json
import pathlib

import jiwer

input_dir = pathlib.Path("ocr_results")
out_dir = pathlib.Path("output")

char_report_files = []
word_report_files = []

all_ref = []
all_pred = []

result = {}
for ref_file in input_dir.glob("*.ref.txt"):
    name = ref_file.name.partition(".")[0]
    ref = (input_dir / f"{name}.ref.txt").read_text(encoding="utf-8")
    pred = (input_dir / f"{name}.pred.txt").read_text(encoding="utf-8")

    all_ref.append(ref)
    all_pred.append(pred)

    result[name] = {"cer": jiwer.cer(reference=ref, hypothesis=pred), "wer": jiwer.wer(reference=ref, hypothesis=pred)}

result["overall"] = {
    "cer": jiwer.cer(reference=all_ref, hypothesis=all_pred),
    "wer": jiwer.wer(reference=all_ref, hypothesis=all_pred),
}

with open(out_dir / "result.json", "w") as f:
    json.dump(result, f)
