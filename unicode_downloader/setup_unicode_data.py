import argparse
import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import networkx as nx

if TYPE_CHECKING:
    from collections.abc import Iterable

PATH = Path(__file__).parent.parent / "python/stringalign/unicode_data"


def download_unicode_license() -> str:
    """Download the Unicode license file."""
    response = httpx.get("https://www.unicode.org/license.txt")
    response.raise_for_status()
    return response.text


def download_security_data(filename: str, version: str) -> str:
    """Download the Unicode confusables data file."""
    url = f"https://www.unicode.org/Public/security/{version}/{filename}"
    response = httpx.get(url)
    response.raise_for_status()
    return response.text


def read_csv(confusables_data) -> list[dict[str, str]]:
    lines = [line.partition("#")[0] for line in confusables_data.splitlines() if line.partition("#")[0].strip()]
    reader = csv.DictReader(lines, fieldnames=["confusable", "replacement", "NA"], delimiter=";")
    return [row for row in reader]


CodePointDict = dict[str, tuple[str, ...]]


def read_confusable_csv(confusables_def: str) -> list[CodePointDict]:
    """Read the confusables data from the unicode_data/confusables.txt file."""
    return [
        {"confusable": tuple(row["confusable"].split()), "replacement": tuple(row["replacement"].split())}
        for row in read_csv(confusables_def)
    ]


def clean_intentional(unprocessed_intentional: list[CodePointDict]) -> list[CodePointDict]:
    graph = nx.Graph()
    for row in unprocessed_intentional:
        graph.add_edge(row["confusable"], row["replacement"])

    intentional = []

    def sort_by(code_points: tuple[str, ...]) -> tuple[int, ...]:
        """Prefer code point sequences with higher degrees, breaking ties with lower summed code points"""
        return graph.degree[code_points], -sum(int(cp, 16) for cp in code_points)

    cc: Iterable[tuple[str, ...]]
    for cc in nx.connected_components(graph):
        cc = sorted(cc)
        replacement = max(cc, key=sort_by)
        for node in cc:
            if node == replacement:
                continue
            intentional.append(({"confusable": node, "replacement": replacement}))

    assert len(intentional) == len(unprocessed_intentional)
    return intentional


def code_point_tuple_to_str(code_points: tuple[str, ...]) -> str:
    return "".join(chr(int(cp, 16)) for cp in code_points)


def build_confusable_map(confusables: list[CodePointDict]) -> dict[str, str]:
    confusable_map = {}
    for confusable in confusables:
        confusable_map[code_point_tuple_to_str(confusable["confusable"])] = code_point_tuple_to_str(
            confusable["replacement"]
        )
    # Sort the keys in case we want to do a binary search on the keys later
    return {k: confusable_map[k] for k in sorted(confusable_map.keys())}


def test_build_confusable_map(confusables: list[CodePointDict]) -> None:
    confusable_map = build_confusable_map(confusables)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        type=str,
        required=True,
        help="Unicode version to download confusables data for",
    )
    args = parser.parse_args()

    download_unicode_license()
    confusables_raw = download_security_data("confusables.txt", args.version)
    intentional_raw = download_security_data("intentional.txt", args.version)
    confusables = read_confusable_csv(confusables_raw)
    intentional = read_confusable_csv(intentional_raw)
    cleaned_intentional = clean_intentional(intentional)
    confusable_map = build_confusable_map(confusables)
    intentional_map = build_confusable_map(cleaned_intentional)

    # Here are some simple assertions to validate data integrity
    ## Each confusable only occurs once in the confusable maps
    assert all(len(confusable["confusable"]) == 1 for confusable in confusables)
    assert all(len(confusable["confusable"]) == 1 for confusable in cleaned_intentional)

    ## The cleaning process should not change the number of confusables
    assert len(intentional) == len(cleaned_intentional)

    ## The confusable map has the correct number of entries, it's sorted by key,
    ## and no key is equal to its value
    assert len(confusable_map) == len(confusables)
    assert len(intentional_map) == len(cleaned_intentional)
    assert sorted(confusable_map.keys()) == list(confusable_map.keys())
    assert sorted(intentional_map.keys()) == list(intentional_map.keys())
    assert all(k != v for k, v in confusable_map.items())
    assert all(k != v for k, v in intentional_map.items())

    # Write the data to files
    (PATH / "license.txt").write_text(download_unicode_license(), encoding="utf-8")
    (PATH / "confusables.txt").write_text(confusables_raw)
    (PATH / "intentional.txt").write_text(intentional_raw)
    (PATH / "confusables.json").write_text(json.dumps(confusable_map, ensure_ascii=False), encoding="utf-8")
    (PATH / "intentional.json").write_text(json.dumps(intentional_map, ensure_ascii=False), encoding="utf-8")
    (PATH / "version.txt").write_text(args.version, encoding="utf-8")


if __name__ == "__main__":
    main()
