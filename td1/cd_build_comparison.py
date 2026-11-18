#!/usr/bin/env python3
"""TD 1, steps 2-3: merge the operators' raw traces and build the comparison.

    python cd_build_comparison.py traces-A.csv traces-B.csv traces-C.csv traces-D-corrected.csv traces-E.csv \
        --extra traces-E-Mathias.csv

Each traces-X.csv comes with its state-X.jsonl (same suffix). Writes:
  - traces-td1.csv and traces-td1.jsonl: every attempt of every file (main and
    --extra), rows unchanged, plus a `source_file` column so that two runs of
    the same model stay distinguishable;
  - model-question-comparison-en.csv: one final row per (model, question), the
    last attempt of each cell of the MAIN files only (an --extra run is a
    second experiment, kept as evidence, not scored). Explanations already
    written in the existing file are kept when the cell and status are
    unchanged; new failures get a `TODO` to complete from the SQL/error;
  - cd_pivot-td1.md: the models x questions view for the plenary;
and prints the per-family counts used in five-model-summary-en.csv.

Coding assistance used (Claude Code); checked and explained by the sub-group.
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUESTIONS = json.loads((HERE / "questions-td1.json").read_text(encoding="utf-8"))["questions"]
TYPE = {q["id"]: q["type"] for q in QUESTIONS}
CASES = [q["id"] for q in QUESTIONS]
FAMILIES = {  # by the official type; a combined question counts in each family it touches, and in "combined"
    "period": lambda t: "period" in t,
    "age": lambda t: "age" in t,
    "product": lambda t: "product" in t,
    "combined": lambda t: "+" in t,
}
COMPARISON = HERE / "model-question-comparison-en.csv"
COMPARISON_FIELDS = ["case_id", "model_id", "trace_file", "cell_id", "nature", "status",
                     "value_cents", "reference_cents", "explanation"]


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def state_of(csv_path):
    return csv_path.with_name(csv_path.name.replace("traces-", "state-", 1)).with_suffix(".jsonl")


def draft_explanation(row, attempts):
    verdict = row["verdict"]
    if verdict == "correct" and len(attempts) == 1:
        return "Value matches reference (HTTP 200, 1 attempt, no retry)."
    evidence = "; ".join(x.replace("\r\n", " ") for x in (row["verdict_detail"], row["error"]) if x)
    if row["http_status"] and row["http_status"] != "200":
        evidence = f"HTTP {row['http_status']}: {evidence}"
    return f"TODO cause from SQL/error - {evidence}; last attempt {row['attempts']} ({row['date_utc']})"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("traces", nargs="+", type=Path, help="main trace CSVs, one per model")
    parser.add_argument("--extra", nargs="*", type=Path, default=[], help="other runs: merged into the raw traces, not scored")
    args = parser.parse_args()

    header, merged, jsonl_lines, main_rows = None, [], [], []
    for path in args.traces + args.extra:
        fields, rows = read(HERE / path)
        if header is None:
            header = fields
        elif fields != header:
            raise SystemExit(f"{path}: header differs from {args.traces[0]}")
        for row in rows:
            merged.append({**row, "source_file": path.name})
            if path in args.traces:
                main_rows.append((row, path.name))
        state = HERE / state_of(path)
        for line in state.read_text(encoding="utf-8").splitlines():
            if line.strip():
                jsonl_lines.append(json.dumps({**json.loads(line), "source_file": state.name}, ensure_ascii=False))

    with open(HERE / "traces-td1.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header + ["source_file"])
        writer.writeheader()
        writer.writerows(merged)
    (HERE / "traces-td1.jsonl").write_text("\n".join(jsonl_lines) + "\n", encoding="utf-8")

    # Same question => same prompt fingerprint, across every model, run and attempt.
    for case in CASES:
        shas = {r["prompt_sha256"] for r in merged if r["case_id"] == case and r["nature"] != "simulation"}
        if len(shas) > 1:
            print(f"WARNING {case}: {len(shas)} different prompt fingerprints", file=sys.stderr)

    # Last attempt per cell of the main files (real and replay never mix).
    cells = defaultdict(list)
    for row, source in main_rows:
        cells[(row["provider"], row["model_requested"], row["case_id"], row["nature"])].append((row, source))
    previous = {}
    if COMPARISON.exists():
        previous = {(r["model_id"], r["case_id"]): r for r in read(COMPARISON)[1]}

    comparison = []
    for (provider, model, case, nature), attempts in cells.items():
        row, source = max(attempts, key=lambda a: (int(a[0]["attempts"]), a[0]["date_utc"]))
        status = row["verdict"] or "not_executed"
        model_id = f"{provider}:{model}"
        old = previous.get((model_id, case))
        keep = old and old["status"] == status and old["cell_id"] == row["cell_id"] and old["explanation"]
        comparison.append({
            "case_id": case, "model_id": model_id, "trace_file": source,
            "cell_id": row["cell_id"], "nature": nature, "status": status,
            "value_cents": row["value"], "reference_cents": row["reference"],
            "explanation": old["explanation"] if keep else draft_explanation(row, attempts),
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
    order = {model_id: i for i, model_id in enumerate(dict.fromkeys(r["model_id"] for r in comparison))}
    comparison.sort(key=lambda r: (order[r["model_id"]], r["case_id"]))
    with open(COMPARISON, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COMPARISON_FIELDS)
        writer.writeheader()
        writer.writerows(comparison)

    # Pivot view and family counts.
    status = defaultdict(dict)
    for row in comparison:
        status[(row["model_id"], row["nature"])][row["case_id"]] = row["status"]
    short = {"correct": "OK", "incorrect": "WRONG", "sql_invalid": "INV", "sql_rejected": "REJ",
             "access_error": "ACC", "not_executed": "N/E"}
    lines = ["| model | nature | " + " | ".join(CASES) + " | correct |", "|---|---|" + "---|" * (len(CASES) + 1)]
    for (model, nature), row_cells in status.items():
        correct = sum(v == "correct" for v in row_cells.values())
        lines.append(f"| {model} | {nature} | " + " | ".join(short.get(row_cells.get(c, ""), row_cells.get(c, "")) for c in CASES)
                     + f" | {correct}/{len(CASES)} |")
    legend = ("\n\nOK correct, WRONG incorrect value, INV invalid SQL, REJ rejected by sandbox, ACC access error, N/E not executed."
              "\nSource: model-question-comparison-en.csv (last attempt per cell); raw attempts in traces-td1.csv.\n")
    types = "\n\nQuestion types: " + "; ".join(f"{c} {TYPE[c]}" for c in CASES) + "\n"
    (HERE / "cd_pivot-td1.md").write_text("# TD 1 - models x questions\n\n" + "\n".join(lines) + legend + types, encoding="utf-8")

    print("\n".join(lines))
    print("\nPer family: correct/evaluated, then unreached cells (combined questions counted in each family)")
    for (model, nature), row_cells in status.items():
        parts = []
        for family, member in FAMILIES.items():
            cases = [c for c in CASES if member(TYPE[c]) and c in row_cells]
            unreached = [c for c in cases if row_cells[c] in ("access_error", "not_executed")]
            evaluated = [c for c in cases if c not in unreached]
            wrong = [c for c in evaluated if row_cells[c] != "correct"]
            parts.append(f"{family} {len(evaluated) - len(wrong)}/{len(evaluated)}"
                         + (f" wrong {','.join(wrong)}" if wrong else "")
                         + (f" unreached {','.join(unreached)}" if unreached else ""))
        print(f"  {model} [{nature}]: " + " | ".join(parts))
    print(f"\n{len(merged)} attempt(s) -> traces-td1.csv / traces-td1.jsonl; {len(comparison)} final row(s) -> "
          f"{COMPARISON.name}; cd_pivot-td1.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
