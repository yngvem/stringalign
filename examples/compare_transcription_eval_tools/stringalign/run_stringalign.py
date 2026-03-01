# /// script
# requires-python = "==3.14.*"
# dependencies = ["stringalign"]
# ///

import json
import pathlib

import stringalign

input_dir = pathlib.Path("ocr_results")
out_dir = pathlib.Path("output")
char_tokenizer = stringalign.tokenize.GraphemeClusterTokenizer()
word_tokenizer = stringalign.tokenize.SplitAtWhitespaceTokenizer()

dinglehopper_normalizer = stringalign.normalize.StringNormalizer(
    # These confusable mappings are copied from Dinglehopper's source code.
    # Dinglehopper is Apache 2.0 licensed, which is compatible with the MIT license.
    # See the Dinglehopper source code for more information
    # https://github.com/qurator-spk/dinglehopper/blob/master/src/dinglehopper/extracted_text.py
    resolve_confusables={
        "": "ſſ",
        "\ueba7": "ſſi",  # MUFI: LATIN SMALL LIGATURE LONG S LONG S I
        "": "ch",
        "": "ck",
        "": "ll",
        "": "ſi",
        "": "ſt",
        "ﬁ": "fi",
        "ﬀ": "ff",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "": "ct",
        "": "tz",  # MUFI: LATIN SMALL LIGATURE TZ
        "\uf532": "as",  # eMOP: Latin small ligature as
        "\uf533": "is",  # eMOP: Latin small ligature is
        "\uf534": "us",  # eMOP: Latin small ligature us
        "\uf535": "Qu",  # eMOP: Latin ligature capital Q small u
        "ĳ": "ij",  # U+0133 LATIN SMALL LIGATURE IJ
        "\ue8bf": "q&",
        # MUFI: LATIN SMALL LETTER Q LIGATED WITH FINAL ET
        # XXX How to replace this correctly?
        "\ueba5": "ſp",  # MUFI: LATIN SMALL LIGATURE LONG S P
        "ﬆ": "st",  # U+FB06 LATIN SMALL LIGATURE ST
    }
    | {
        "": "ü",
        "": "ä",
        "==": "–",  # → en-dash
        "—": "–",  # em-dash → en-dash
        "": "ö",
        "’": "'",
        "⸗": "-",
        "aͤ": "ä",  # LATIN SMALL LETTER A, COMBINING LATIN SMALL LETTER E
        "oͤ": "ö",  # LATIN SMALL LETTER O, COMBINING LATIN SMALL LETTER E
        "uͤ": "ü",  # LATIN SMALL LETTER U, COMBINING LATIN SMALL LETTER E
        "\uf50e": "q́",  # U+F50E LATIN SMALL LETTER Q WITH ACUTE ACCENT
    }
)
dinglehopper_char_tokenizer = stringalign.tokenize.GraphemeClusterTokenizer(
    pre_tokenization_normalizer=dinglehopper_normalizer
)
dinglehopper_word_tokenizer = stringalign.tokenize.UnicodeWordTokenizer(
    pre_tokenization_normalizer=dinglehopper_normalizer
)

char_report_files = []
word_report_files = []

all_ref = []
all_pred = []

result = {}
result_dinglehopper_confusable_handling = {}
for ref_file in input_dir.glob("*.ref.txt"):
    name = ref_file.name.partition(".")[0]
    ref = "\n".join((input_dir / f"{name}.ref.txt").read_text(encoding="utf-8").splitlines())
    pred = "\n".join((input_dir / f"{name}.pred.txt").read_text(encoding="utf-8").splitlines())

    all_ref.append(ref)
    all_pred.append(pred)

    result[name] = {
        "cer": (
            stringalign.statistics.StringConfusionMatrix.from_strings(
                reference=ref, predicted=pred, tokenizer=char_tokenizer
            ).compute_token_error_rate()
        ),
        "wer": (
            stringalign.statistics.StringConfusionMatrix.from_strings(
                reference=ref, predicted=pred, tokenizer=word_tokenizer
            ).compute_token_error_rate()
        ),
    }
    result_dinglehopper_confusable_handling[name] = {
        "cer": (
            stringalign.statistics.StringConfusionMatrix.from_strings(
                reference=ref, predicted=pred, tokenizer=dinglehopper_char_tokenizer
            ).compute_token_error_rate()
        ),
        "wer": (
            stringalign.statistics.StringConfusionMatrix.from_strings(
                reference=ref, predicted=pred, tokenizer=dinglehopper_word_tokenizer
            ).compute_token_error_rate()
        ),
    }

result["overall"] = {
    "cer": (
        stringalign.statistics.StringConfusionMatrix.from_string_collections(
            references=all_ref, predictions=all_pred, tokenizer=char_tokenizer
        ).compute_token_error_rate()
    ),
    "wer": (
        stringalign.statistics.StringConfusionMatrix.from_string_collections(
            references=all_ref, predictions=all_pred, tokenizer=word_tokenizer
        ).compute_token_error_rate()
    ),
}
result_dinglehopper_confusable_handling["overall"] = {
    "cer": (
        stringalign.statistics.StringConfusionMatrix.from_string_collections(
            references=all_ref, predictions=all_pred, tokenizer=dinglehopper_char_tokenizer
        ).compute_token_error_rate()
    ),
    "wer": (
        stringalign.statistics.StringConfusionMatrix.from_string_collections(
            references=all_ref, predictions=all_pred, tokenizer=dinglehopper_word_tokenizer
        ).compute_token_error_rate()
    ),
}

with open(out_dir / "result.json", "w") as f:
    json.dump(result, f)
with open(out_dir / "result_dinglehopper_processing.json", "w") as f:
    json.dump(result_dinglehopper_confusable_handling, f)
