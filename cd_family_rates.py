#!/usr/bin/env python3
"""TD 2, step 3: exact TD 1 accuracy per question family and per model.

Reads model-question-comparison-en.csv (the scored TD 1 run: last attempt per
cell, five models x twenty questions). A cell that never ran (not_executed) is
not an error of the model: it is counted apart, never in correct/cases.

    python cd_family_rates.py            # Markdown table for the routing rule

Coding assistance used (Claude Code); checked and explained by the sub-group.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TYPES = {q["id"]: q["type"] for q in json.loads((HERE / "questions-td1.json").read_text(encoding="utf-8"))["questions"]}
FAMILIES = {  # the families of the TD 2 assignment, from the official question types
    "F1 period": "period",
    "F2 age on a reference date": "age on a reference date",
    "F2b age at the time of the order": "age at the time of the order",
    "F3 product list": "product list",
    "F4 combinations": None,  # any type containing "+"
}


def family_of(case):
    for family, kind in FAMILIES.items():
        if kind == TYPES[case]:
            return family
    return "F4 combinations"


def main():
    with open(HERE / "model-question-comparison-en.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    models = list(dict.fromkeys(r["model_id"] for r in rows))
    cells = defaultdict(lambda: defaultdict(list))  # family -> model -> [(case, status)]
    for r in rows:
        cells[family_of(r["case_id"])][r["model_id"]].append((r["case_id"], r["status"]))

    short = [m.split("/")[-1] for m in models]
    print("| Family | Cells | " + " | ".join(short) + " | All models |")
    print("|---|---|" + "---|" * (len(models) + 1))
    for family in FAMILIES:
        cases = sorted({c for m in models for c, _ in cells[family][m]})
        parts, total_ok, total_n = [], 0, 0
        for m in models:
            results = cells[family][m]
            unrun = [c for c, s in results if s == "not_executed"]
            scored = [(c, s) for c, s in results if s != "not_executed"]
            ok = sum(s == "correct" for _, s in scored)
            wrong = [c for c, s in scored if s != "correct"]
            total_ok, total_n = total_ok + ok, total_n + len(scored)
            text = f"{ok}/{len(scored)}"
            if wrong:
                text += " (" + ", ".join(wrong) + ")"
            if unrun:
                text += " + " + ", ".join(unrun) + " not run"
            parts.append(text)
        print(f"| {family} | {', '.join(cases)} | " + " | ".join(parts) + f" | {total_ok}/{total_n} |")
    print("\nIn brackets: cells where the model was wrong (incorrect or invalid SQL). "
          "'not run': no final value (HTTP 429 twice), excluded from correct/cases.")


if __name__ == "__main__":
    main()
