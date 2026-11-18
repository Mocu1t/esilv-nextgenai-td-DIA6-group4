#!/usr/bin/env python3
"""TD 2, step 1: the twenty decisions of the fixed 2-of-3 panel and of the 3-of-5 quorum.

Uses the vote_k_sur_n method of skeleton-multi-llm-en.py (Pair A), on the stored
TD 1 traces only, no network. For each model, its last attempt on the question
is its proposal (same rule as atelier-vote.py). The unscored second run of E
(source_file traces-E-Mathias.csv) is excluded: one row per model, otherwise
the method would refuse the duplicate. The reference is read AFTER the vote.

    python cd_vote_table.py            # Markdown table
    python cd_vote_table.py --csv out  # also write the table as CSV

Coding assistance used (Claude Code); checked and explained by the sub-group.
"""
import argparse
import csv
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
TD1 = HERE.parent.parent / "td1"  # TD 1 kit, traces and references
PANEL_3 = [("groq", "openai/gpt-oss-120b"), ("openrouter", "cohere/north-mini-code:free"),
           ("groq", "qwen/qwen3.8-27b")]
ALL_5 = [("groq", "openai/gpt-oss-120b"), ("groq", "openai/gpt-oss-20b"),
         ("openrouter", "cohere/north-mini-code:free"), ("groq", "qwen/qwen3.8-27b"),
         ("openrouter", "dots-studio/dots-3-note-preview:free")]
LETTER = {"openai/gpt-oss-120b": "A", "openai/gpt-oss-20b": "B", "cohere/north-mini-code:free": "C",
          "qwen/qwen3.8-27b": "D", "dots-studio/dots-3-note-preview:free": "E"}
UNSCORED = {"traces-E-Mathias.csv"}


def load_vote():
    spec = importlib.util.spec_from_file_location("student_skeleton", TD1 / "skeleton-multi-llm-en.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return lambda proposals, k: module.Orchestrateur.vote_k_sur_n(None, proposals, k)


def last_rows(rows, case):
    last = {}
    for row in rows:  # chronological export: the last row is the last attempt
        if row["case_id"] == case and row["nature"] == "real" and row["source_file"] not in UNSCORED:
            last[(row["provider"], row["model_requested"])] = row
    return last


def proposals(last, panel):
    out = []
    for provider, model in panel:
        row = last.get((provider, model), {})
        value = row.get("value", "")
        valid = row.get("verdict") in {"correct", "incorrect"} and value != ""
        out.append(SimpleNamespace(provider=provider, model_requested=model,
                                   value=int(value) if valid else None,
                                   verdict="executed" if valid else "error"))
    return out


def label(row):
    if not row:
        return "missing"
    if row["verdict"] in {"correct", "incorrect"}:
        return f"{row['value']} ({row['verdict']})"
    detail = row["verdict_detail"] or row["error"] or row["http_status"]
    return f"no vote ({row['verdict']}: {detail[:40]})"


def decision(result, reference):
    if not result["consensus"]:
        return f"abstain (max {result['votes']})", "-"
    ok = "yes" if result["value"] == reference else "NO"
    return f"{result['value']} ({result['votes']} votes)", ok


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    vote = load_vote()
    with open(TD1 / "traces-td1.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open(TD1 / "reference-td1.csv", newline="", encoding="utf-8") as f:
        refs = {r["case_id"]: int(r["revenue_cents"]) for r in csv.DictReader(f)}
    table = []
    for i in range(1, 21):
        case = f"C{i:02d}"
        last = last_rows(rows, case)
        r3 = vote(proposals(last, PANEL_3), 2)
        r5 = vote(proposals(last, ALL_5), 3)
        ref = refs[case]  # read after both decisions
        d3, ok3 = decision(r3, ref)
        d5, ok5 = decision(r5, ref)
        changed = (r3["consensus"], r3["value"]) != (r5["consensus"], r5["value"])
        values = "; ".join(f"{LETTER[m]}={label(last.get((p, m)))}" for p, m in ALL_5)
        table.append({"case_id": case, "reference": ref, "2of3": d3, "2of3_ok": ok3, "3of5": d5,
                      "3of5_ok": ok5, "decision_changed": "yes" if changed else "no", "proposals": values})
    print("| Case | Reference | 2-of-3 (A, C, D) | OK | 3-of-5 (A-E) | OK | Changed | Proposals (last attempt) |")
    print("|---|---:|---|---|---|---|---|---|")
    for t in table:
        bold = {"NO": "**NO**"}
        print(f"| {t['case_id']} | {t['reference']} | {t['2of3']} | {bold.get(t['2of3_ok'], t['2of3_ok'])} | "
              f"{t['3of5']} | {bold.get(t['3of5_ok'], t['3of5_ok'])} | {t['decision_changed']} | {t['proposals']} |")
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(table[0]))
            writer.writeheader()
            writer.writerows(table)


if __name__ == "__main__":
    main()
