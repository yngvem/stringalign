# /// script
# requires-python = ">=3.13"
# dependencies = ["regex"]
# ///

import unicodedata
from pathlib import Path

import regex

text = Path("data.txt").read_text()
matches = regex.findall(r"\X", text)
for match in matches:
    if len(unicodedata.normalize("NFC", match)) > 1:
        print(match)
