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

pages = [f.stem.partition(".")[0] for f in pathlib.Path("ocr_results").iterdir()]

results = {}


# Load Calamari results
with open("calamari/calamari_results/result.json", "r") as f:
    calamari = json.load(f)
results["Calamari"] = {key: {"cer": value["avg_ler"]} for key, value in calamari.items()}


# Load Dinglehopper results
dinglehopper_path = pathlib.Path("dinglehopper/dinglehopper_results")
results["Dinglehopper"] = {}

for page in pages:
    with open(dinglehopper_path / f"{page}.txt-report.json", "r") as f:
        page_data = json.load(f)

    results["Dinglehopper"][page] = {"cer": page_data["cer"], "wer": page_data["wer"]}

with open(dinglehopper_path / "summary.json", "r") as f:
    summary_data = json.load(f)
results["Dinglehopper"]["overall"] = {"cer": summary_data["cer_avg"], "wer": summary_data["wer_avg"]}

# Load ISRI results
isri_path = pathlib.Path("isri/isri_results")
results["ISRI"] = {}


def get_isri_error_rate(file: pathlib.Path) -> float:
    with open(file, "r") as f:
        report = f.readlines()

    accuracy_line = report[4]
    (accuracy_match,) = re.findall(r"(\d+(?:\.\d+)?)%\s+Accuracy", accuracy_line)
    return 1 - float(accuracy_match) / 100


results["ISRI"]["overall"] = {
    "cer": get_isri_error_rate(isri_path / "character_report.txt"),
    "wer": get_isri_error_rate(isri_path / "word_report.txt"),
}

for page in pages:
    results["ISRI"][page] = {
        "cer": get_isri_error_rate(isri_path / f"{page}.char_report.txt"),
        "wer": get_isri_error_rate(isri_path / f"{page}.word_report.txt"),
    }

# Load jiwer
with open("jiwer/jiwer_results/result.json", "r") as f:
    results["Jiwer"] = json.load(f)

# Load meeteval
with open("meeteval/meeteval_results/result.json", "r") as f:
    results["Meeteval"] = json.load(f)


# Load ocrevalUAtion
def parse_ocrevalUAtion_report(file: pathlib.Path) -> dict[str, float]:
    with open(file, "r") as f:
        report = f.readlines()
    cer_line = report[10]
    (cer,) = re.findall(r"<td>CER</td><td>(\d+(?:\.\d+)?)</td>", cer_line)

    wer_line = report[13]
    (wer,) = re.findall(r"<td>WER</td><td>(\d+(?:\.\d+)?)</td>", wer_line)

    return {"cer": float(cer) / 100, "wer": float(wer) / 100}


ocrevalUAtion_path = pathlib.Path("ocrevalUAtion/ocrevalUAtion_results")
results["ocrevalUAtion"] = {
    page: parse_ocrevalUAtion_report(ocrevalUAtion_path / f"{page}.report.html") for page in pages
}

# Load stringalign
with open("stringalign/stringalign_results/result.json", "r") as f:
    results["Stringalign"] = json.load(f)
# Load stringalign
with open("stringalign/stringalign_results/result_dinglehopper_processing.json", "r") as f:
    results["Stringalign (Dinglehopper)"] = json.load(f)

# Convert results to records
result_records = []
for method, single_method_results in results.items():
    for sample, sample_result in single_method_results.items():
        result_records.append({"method": method, "sample": sample, **sample_result})

# Assemble in DataFrame
df = pd.DataFrame(result_records).sort_values(["sample", "method"]).set_index(["sample", "method"])
df_no_overall = df.drop("overall", level="sample", errors="ignore")
df.loc[("overall", "ocrevalUAtion"),] = df.loc[(slice(None), "ocrevalUAtion"),].mean()

dinglehopper_diff_df = df.loc[(slice(None), "Dinglehopper"),].reset_index(level="method", drop=True) - df.loc[
    (slice(None), "Stringalign (Dinglehopper)"),
].reset_index(level="method", drop=True)
df = df.drop("Stringalign (Dinglehopper)", level="method", errors="ignore")

# Get dispersion measures
mean_absolute_deviation_from_mean = (
    df.drop("overall", level="sample", errors="ignore")  # This time without the Dinglehopper data as well
    .groupby("sample")  # Get dataframes for each sample with all methods
    .transform(
        lambda s: abs(s - s.median())
    )  # For each method, compute its absolute deviation from the mean in that sample
    .groupby("method")  # Get dataframes for each tools with all samples
    .mean()
)

overall_res = df.loc["overall"].copy()
overall_res.columns = pd.MultiIndex.from_tuples([("Overall measure", metric.upper()) for metric in df.columns])
mean_absolute_deviation_from_mean.columns = pd.MultiIndex.from_tuples(
    [("MADM", metric.upper()) for metric in df.columns]
)

out_df = pd.merge(overall_res, mean_absolute_deviation_from_mean, how="outer", on="method")
with open("hip21_table.tex", "w", encoding="utf-8") as f:
    f.write(out_df.to_latex(na_rep="--", float_format="%.4f"))

print(out_df)
print(
    "Diff between Stringalign and Dinglehopper when confusables are resolved equally\n",
    dinglehopper_diff_df.drop("overall", errors="ignore").max(),
)
