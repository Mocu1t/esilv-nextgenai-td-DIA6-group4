#!/usr/bin/env python3
"""TD 1, steps 2-3: merge the operators' raw traces and draft the comparison.

    python cd_build_comparison.py traces-A.csv traces-B.csv traces-C.csv traces-D.csv traces-E.csv

Writes:
  - traces-td1.csv: every attempt of every input file, one header, rows unchanged;
  - model-question-comparison-en.csv: one final row per (model, question), the
    last attempt of each cell; `explanation` is pre-filled from the trace
    (verdict_detail, error, HTTP status) and MUST be completed by hand with the
    cause read from the SQL (broken convention, invalid SQL, truncation, access);
  - cd_pivot-td1.md: the models x questions view for the plenary;
and prints the per-family counts used in five-model-summary-en.csv.

Coding assistance used (Claude Code); checked and explained by the sub-group.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUESTIONS = json.loads((HERE / "questions-td1.json").read_text(encoding="utf-8"))["questions"]
TYPE = {q["id"]: q["type"] for q in QUESTIONS}
CASES = [q["id"] for q in QUESTIONS]
FAMILIES = {  # a combined question counts in each family it touches, and in "combined"
    "period": lambda t: "period" in t,
    "age": lambda t: "age" in t,
    "product": lambda t: "product" in t,
    "combined": lambda t: "+" in t,
}
COMPARISON_FIELDS = ["case_id", "model_id", "trace_file", "cell_id", "nature", "status",
                     "value_cents", "reference_cents", "explanation"]


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def draft_explanation(row):
    attempt = f"last attempt {row['attempts']} ({row['date_utc']})"
    verdict = row["verdict"]
    if verdict == "correct":
        return f"Value equals reference; {attempt}"
    evidence = "; ".join(x for x in (row["verdict_detail"], row["error"]) if x)
    if row["http_status"] and row["http_status"] != "200":
        evidence = f"HTTP {row['http_status']}: {evidence}"
    return f"TODO cause from SQL/error - {evidence}; {attempt}"


def main(paths):
    if not paths:
        print(__doc__)
        return 1
    header, merged, origin = None, [], {}
    for path in paths:
        fields, rows = read(path)
        if header is None:
            header = fields
        elif fields != header:
            raise SystemExit(f"{path}: header differs from {paths[0]}")
        for row in rows:
            merged.append(row)
            origin[id(row)] = Path(path).name

    with open(HERE / "traces-td1.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(merged)

    # Same question => same prompt fingerprint, across every model and attempt.
    for case in CASES:
        shas = {r["prompt_sha256"] for r in merged if r["case_id"] == case and r["nature"] != "simulation"}
        if len(shas) > 1:
            print(f"WARNING {case}: {len(shas)} different prompt fingerprints", file=sys.stderr)

    # Last attempt per cell (and per nature: real and replay never mix).
    final = {}
    for row in merged:
        key = (row["model_requested"], row["provider"], row["case_id"], row["nature"])
        if key not in final or (int(row["attempts"]), row["date_utc"]) >= (int(final[key]["attempts"]), final[key]["date_utc"]):
            final[key] = row

    comparison = []
    for (model, provider, case, nature), row in sorted(final.items(), key=lambda kv: (kv[0][0], kv[0][2])):
        comparison.append({
            "case_id": case, "model_id": f"{provider}:{model}", "trace_file": origin[id(row)],
            "cell_id": row["cell_id"], "nature": nature, "status": row["verdict"] or "not_executed",
            "value_cents": row["value"], "reference_cents": row["reference"],
            "explanation": draft_explanation(row),
        })
    # A model with no trace for a question still gets a row: not_executed, reason to fill in.
    seen = {(r["model_id"], r["nature"]) for r in comparison}
    done = {(r["model_id"], r["nature"], r["case_id"]) for r in comparison}
    references = {r["case_id"]: r["revenue_cents"] for r in read(HERE / "reference-td1.csv")[1]}
    for model_id, nature in sorted(seen):
        for case in CASES:
            if (model_id, nature, case) not in done:
                comparison.append({"case_id": case, "model_id": model_id, "trace_file": "", "cell_id": f"{model_id}:{case}",
                                   "nature": nature, "status": "not_executed", "value_cents": "",
                                   "reference_cents": references.get(case, ""),
                                   "explanation": "TODO reason: no attempt in the raw traces"})
    comparison.sort(key=lambda r: (r["model_id"], r["case_id"]))
    with open(HERE / "model-question-comparison-en.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COMPARISON_FIELDS)
        writer.writeheader()
        writer.writerows(comparison)

    # Pivot view and family counts.
    status = defaultdict(dict)
    for row in comparison:
        status[(row["model_id"], row["nature"])][row["case_id"]] = row["status"]
    short = {"correct": "OK", "incorrect": "WRONG", "sql_invalid": "INV", "sql_rejected": "REJ",
             "access_error": "ACC", "not_executed": "N/E"}
    lines = ["| model | nature | " + " | ".join(CASES) + " |", "|---|---|" + "---|" * len(CASES)]
    for (model, nature), cells in sorted(status.items()):
        lines.append(f"| {model} | {nature} | " + " | ".join(short.get(cells.get(c, ""), cells.get(c, "")) for c in CASES) + " |")
    legend = "\n\nOK correct, WRONG incorrect value, INV invalid SQL, REJ rejected by sandbox, ACC access error, N/E not executed.\n"
    (HERE / "cd_pivot-td1.md").write_text("# TD 1 - models x questions\n\n" + "\n".join(lines) + legend, encoding="utf-8")

    print("\n".join(lines))
    print("\nPer family: correct/evaluated, then access errors or unfinished cells (combined questions counted in each family)")
    for (model, nature), cells in sorted(status.items()):
        parts = []
        for family, member in FAMILIES.items():
            cases = [c for c in CASES if member(TYPE[c]) and c in cells]
            unreached = [c for c in cases if cells[c] in ("access_error", "not_executed")]
            evaluated = [c for c in cases if c not in unreached]
            correct = sum(cells[c] == "correct" for c in evaluated)
            parts.append(f"{family} {correct}/{len(evaluated)}" + (f" (+{len(unreached)} unreached)" if unreached else ""))
        print(f"  {model} [{nature}]: " + ", ".join(parts))
    print(f"\n{len(merged)} attempt(s) -> traces-td1.csv; {len(comparison)} final row(s) -> model-question-comparison-en.csv; cd_pivot-td1.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
