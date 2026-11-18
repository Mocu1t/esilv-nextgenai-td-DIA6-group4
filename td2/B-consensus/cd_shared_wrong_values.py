#!/usr/bin/env python3
"""TD 2, step 2 (complement to Pair B's notebook): every shared wrong value of the batch.

For each question where at least two models return the same incorrect value,
on the scored TD 1 traces (last attempt per model; the unscored second E run
is excluded):
  1. the quorum verdicts, computed with vote_k_sur_n (Pair A): fixed 2-of-3
     panel (gpt-oss-120b, north-mini-code, qwen3.8-27b) and 3-of-5 quorum;
  2. each faulty query re-executed AS RETURNED on data/boutique.sqlite
     (read-only), to check it gives the traced value;
  3. a delta query: order lines counted by the reference condition (completed
     age = 25 on the reference date) AND NOT by the faulty WHERE condition,
     grouped by customer, plus the opposite direction (wrongly added lines).
     Missed - added must equal reference - wrong value, to the cent.

    python cd_shared_wrong_values.py      # Markdown, no network

Coding assistance used (Claude Code); checked and explained by the sub-group.
"""
import csv
import importlib.util
import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
TD1 = HERE.parent.parent / "td1"
PANEL_3 = ["openai/gpt-oss-120b", "cohere/north-mini-code:free", "qwen/qwen3.8-27b"]
LETTER = {"openai/gpt-oss-120b": "A", "openai/gpt-oss-20b": "B", "cohere/north-mini-code:free": "C",
          "qwen/qwen3.8-27b": "D", "dots-studio/dots-3-note-preview:free": "E"}
ORDER = list(LETTER)

FROM = """FROM orders o
JOIN product p   ON p.product_id = o.product_id
JOIN customers c ON c.customer_id = o.customer_id"""


def ref_condition(day):
    """Completed age on `day` = year difference - (birthday not reached yet)."""
    return (f"(CAST(substr('{day}', 1, 4) AS INTEGER) - CAST(substr(c.birth_date, 1, 4) AS INTEGER)"
            f" - (substr('{day}', 6, 5) < substr(c.birth_date, 6, 5))) = 25")


def where_of(sql):
    """The WHERE condition of a returned query, as written by the model."""
    parts = re.split(r"\bWHERE\b", sql, flags=re.IGNORECASE)
    if len(parts) != 2:
        raise ValueError("expected exactly one WHERE")
    return parts[1].strip().rstrip(";").strip()


def load_vote():
    spec = importlib.util.spec_from_file_location("student_skeleton", TD1 / "skeleton-multi-llm-en.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return lambda proposals, k: module.Orchestrateur.vote_k_sur_n(None, proposals, k)


def main():
    vote = load_vote()
    questions = {q["id"]: q["question"] for q in
                 json.loads((TD1 / "questions-td1.json").read_text(encoding="utf-8"))["questions"]}
    with open(TD1 / "reference-td1.csv", newline="", encoding="utf-8") as f:
        refs = {r["case_id"]: int(r["revenue_cents"]) for r in csv.DictReader(f)}
    last = defaultdict(dict)
    with open(TD1 / "traces-td1.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["nature"] == "real" and r["source_file"] != "traces-E-Mathias.csv":
                last[r["case_id"]][r["model_requested"]] = r  # chronological: last attempt wins
    db = sqlite3.connect((TD1 / "data" / "boutique.sqlite").as_uri() + "?mode=ro", uri=True)

    for case in sorted(last):
        groups = defaultdict(list)
        for model, r in last[case].items():
            if r["verdict"] == "incorrect":
                groups[int(r["value"])].append(model)
        for wrong, models in groups.items():
            if len(models) < 2:
                continue
            models.sort(key=ORDER.index)
            ref = refs[case]
            day = re.search(r"reference date (\d{4}-\d{2}-\d{2})", questions[case]).group(1)

            def proposals(panel):
                out = []
                for m in panel:
                    r = last[case].get(m, {})
                    ok = r.get("verdict") in {"correct", "incorrect"} and r.get("value", "") != ""
                    out.append(SimpleNamespace(provider=r.get("provider", "?"), model_requested=m,
                                               value=int(r["value"]) if ok else None,
                                               verdict="executed" if ok else "error"))
                return out

            def show(res):
                if not res["consensus"]:
                    return f"abstains (largest count {res['votes']})"
                tag = "the shared WRONG value wins" if res["value"] == wrong else (
                    "the reference wins" if res["value"] == ref else "another value wins")
                return f"{res['value']} with {res['votes']} votes: {tag}"

            print(f"## {case}: shared wrong value {wrong}, reference {ref}\n")
            print(f"Question: {questions[case]}\n")
            print("Proposals (last attempt): " + "; ".join(
                f"{LETTER[m]}={last[case][m]['value'] or '-'} ({last[case][m]['verdict']})"
                for m in ORDER if m in last[case]) + "\n")
            print(f"- Agreeing on {wrong}: " + ", ".join(f"{LETTER[m]} `{m}`" for m in models))
            print(f"- Fixed 2-of-3 panel (A, C, D), k = 2: {show(vote(proposals(PANEL_3), 2))}")
            print(f"- 3-of-5 quorum (A to E), k = 3: {show(vote(proposals(ORDER), 3))}\n")

            assert db.execute(f"SELECT COALESCE(SUM(o.quantity_product * p.price), 0) {FROM} "
                              f"WHERE {ref_condition(day)}").fetchone()[0] == ref, "reference query"
            for m in models:
                sql = last[case][m]["sql"]
                rerun = db.execute(sql).fetchone()[0]
                cond = where_of(sql)
                missed = db.execute(
                    f"SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) {FROM}\n"
                    f"WHERE {ref_condition(day)}\n  AND NOT COALESCE((\n{cond}\n), 0)\n"
                    f"GROUP BY c.customer_id, c.birth_date ORDER BY c.customer_id").fetchall()
                added = db.execute(
                    f"SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) {FROM}\n"
                    f"WHERE COALESCE((\n{cond}\n), 0) AND NOT ({ref_condition(day)})\n"
                    f"GROUP BY c.customer_id, c.birth_date ORDER BY c.customer_id").fetchall()
                total_missed = sum(x[2] for x in missed)
                total_added = sum(x[2] for x in added)
                print(f"### {LETTER[m]} `{m}`: re-executed = {rerun} (trace: {wrong})\n")
                print("Faulty WHERE, as returned:\n\n```sql\n" + cond + "\n```\n")
                print("| customer_id | birth_date | revenue missed (cents) |\n|---|---|---:|")
                for cid, bd, rev in missed:
                    print(f"| {cid} | {bd} | {rev} |")
                print(f"| **total** | | **{total_missed}** |\n")
                print(f"Wrongly added: {total_added} cents ({len(added)} customers). "
                      f"Missed - added = {total_missed - total_added} = reference - wrong "
                      f"({ref - wrong}): {'gap explained to the cent' if total_missed - total_added == ref - wrong else 'UNEXPLAINED'}.\n")
    print("Delta query pattern (executed above for each faulty query):\n\n```sql\n"
          f"SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) AS revenue_cents\n{FROM}\n"
          f"WHERE {ref_condition('<reference date>')}\n  AND NOT COALESCE((<faulty WHERE, as returned>), 0)\n"
          "GROUP BY c.customer_id, c.birth_date ORDER BY c.customer_id;\n```\n\n"
          "`COALESCE(..., 0)` keeps the rows where the faulty condition is NULL: `NOT NULL` would drop them.")


if __name__ == "__main__":
    main()
