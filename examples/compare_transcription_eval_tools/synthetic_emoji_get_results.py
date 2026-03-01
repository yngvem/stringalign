# /// script
# requires-python = ">=3.13"
# dependencies = ["pandas", "jinja2"]
# ///

"""
This script gets the results from all the string comparison tools and creates a single DataFrame to display them
"""

import json
import pathlib
import re

import pandas as pd

pages = [
    "page00000",
    "page00001",
    "page00002",
    "page00003",
    "page00004",
    "page00005",
]

results = {}


# Load Calamari results
with open("calamari/calamari_results/result.json", "r") as f:
    results["calamari"] = {"cer": json.load(f)["overall"]["avg_ler"]}


# Load Dinglehopper results
with open("dinglehopper/dinglehopper_results/page00000.txt-report.json", "r") as f:
    summary_data = json.load(f)
results["dinglehopper"] = {"cer": summary_data["cer"], "wer": summary_data["wer"]}


# Load ISRI results
def get_isri_error_rate(file: pathlib.Path) -> float:
    with open(file, "r") as f:
        report = f.readlines()

    accuracy_line = report[4]
    (accuracy_match,) = re.findall(r"(\d+(?:\.\d+)?)%\s+Accuracy", accuracy_line)
    return 1 - float(accuracy_match) / 100


isri_path = pathlib.Path("isri/isri_results")
results["isri"] = {
    "cer": get_isri_error_rate(isri_path / "page00000.char_report.txt"),
    "wer": get_isri_error_rate(isri_path / "page00000.word_report.txt"),
}

# Load jiwer
jiwer_path = pathlib.Path("jiwer/jiwer_results")
with open("jiwer/jiwer_results/result.json", "r") as f:
    results["jiwer"] = json.load(f)["overall"]

# Load meeteval
jiwer_path = pathlib.Path("meeteval/meeteval_results")
with open("meeteval/meeteval_results/result.json", "r") as f:
    results["meeteval"] = json.load(f)["overall"]


# Load ocrevalUAtion
def parse_ocrevalUAtion_report(file: pathlib.Path) -> dict[str, float]:
    with open(file, "r") as f:
        report = f.readlines()
    cer_line = report[10]
    (cer,) = re.findall(r"<td>CER</td><td>(\d+(?:\.\d+)?)</td>", cer_line)

    wer_line = report[13]
    (wer,) = re.findall(r"<td>WER</td><td>(\d+(?:\.\d+)?)</td>", wer_line)

    return {"cer": float(cer) / 100, "wer": float(wer) / 100}


try:
    ocrevalUAtion_path = pathlib.Path("ocrevalUAtion/ocrevalUAtion_results")
    results["ocrevalUAtion"] = parse_ocrevalUAtion_report(ocrevalUAtion_path / "page00000.report.html")
except Exception:
    print("ocrevalUAtion failed")

# Load stringalign
with open("stringalign/stringalign_results/result.json", "r") as f:
    results["stringalign"] = json.load(f)["overall"]

# Convert results to records
result_records = []
for method, single_method_results in results.items():
    result_records.append({"method": method, **single_method_results})

df = pd.DataFrame(result_records).sort_values(["method"]).set_index(["method"])

print(df)
with open("synthetic_emoji_table.tex", "w", encoding="utf-8") as f:
    f.write(df.to_latex(na_rep="--", float_format="%.4f"))
