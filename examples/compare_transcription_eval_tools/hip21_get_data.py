import csv
import xml.etree.ElementTree as ET
from collections.abc import Generator
from pathlib import Path

from tqdm import tqdm


def get_page_text(file: Path) -> Generator[str]:
    root = ET.parse(file)
    ns = {"PAGE": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2010-03-19"}
    unicode_tags = root.findall(".//PAGE:TextRegion/PAGE:TextEquiv/PAGE:Unicode", ns)
    for unicode_tag in unicode_tags:
        if text := unicode_tag.text.strip():  # type: ignore
            yield text + "\n"


def get_alto_text(file: Path) -> Generator[str]:
    root = ET.parse(file)
    ns = "http://www.loc.gov/standards/alto/ns-v3#"
    text_line_tags = root.findall(".//ALTO:TextLine", {"ALTO": ns})
    for text_line_tag in text_line_tags:
        out = []
        for tag in text_line_tag:
            tag_type = tag.tag.casefold()
            if tag_type == f"{{{ns}}}string":
                out.append(tag.attrib["CONTENT"])
            elif tag_type == f"{{{ns}}}sp":
                out.append(" ")
            elif tag_type == f"{{{ns}}}hyp":
                out.append(tag.attrib["CONTENT"])
            else:
                raise ValueError()

        if text := "".join(out).strip():
            yield text + "\n"


repo_parent = Path(__file__).parent / "hip21_ocrevaluation"
data_parent = repo_parent / "data"
output_dir = Path(__file__).parent / "ocr_results"
output_dir.mkdir(exist_ok=True)

with open(repo_parent / "primaID.csv") as f:
    reader = csv.DictReader(f)
    stems = [row["\ufeffprimaID"] for row in reader if row["dataset"] == "impact"]

for stem in tqdm(sorted(stems)):
    gt_xml = data_parent / f"{stem}.gt.xml"
    gt4hist_xml = data_parent / f"{stem}.gt4hist.xml"

    with open(output_dir / f"{stem}.ref.txt", "w", encoding="utf-8") as f:
        f.writelines(get_page_text(gt_xml))

    with open(output_dir / f"{stem}.pred.txt", "w", encoding="utf-8") as f:
        f.writelines(get_alto_text(gt4hist_xml))
