import pathlib
import subprocess

input_dir = pathlib.Path("ocr_results")
out_dir = pathlib.Path("output")

char_report_files = []
word_report_files = []

for ref_file in input_dir.glob("*.ref.txt"):
    name = ref_file.name.partition(".")[0]
    ref = str(input_dir / f"{name}.ref.txt")
    pred = str(input_dir / f"{name}.pred.txt")

    char_report_file = str(out_dir / f"{name}.char_report.txt")
    word_report_file = str(out_dir / f"{name}.word_report.txt")

    subprocess.run(["accuracy", f"ocr_results/{name}.ref.txt", f"ocr_results/{name}.pred.txt", char_report_file])

    subprocess.run(["wordacc", f"ocr_results/{name}.ref.txt", f"ocr_results/{name}.pred.txt", word_report_file])

    char_report_files.append(char_report_file)
    word_report_files.append(word_report_file)


with open(out_dir / "character_report.txt", "w") as f:
    subprocess.run(["accsum"] + char_report_files, stdout=f)

with open(out_dir / "word_report.txt", "w") as f:
    subprocess.run(["wordaccsum"] + word_report_files, stdout=f)
