#!/usr/bin/env python3
"""TD 1: check every operator's raw trace (CSV) and state (JSONL) before merging.

    python cd_check_traces.py A=traces-A.csv:state-A.jsonl B=... E=traces-E.csv:state-E.jsonl

For each pair: header, expected provider/model, the twenty questions, prompt
fingerprint (identical per question across ALL files, and equal to the one the
skeleton computes now), reference equal to reference-td1.csv, nature, attempts,
verdict consistent with value/reference, CSV equal to JSONL, no API key.

Coding assistance used (Claude Code); checked and explained by the sub-group.
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = {
    "A": ("groq", "openai/gpt-oss-120b"),
    "B": ("groq", "openai/gpt-oss-20b"),
    "C": ("openrouter", "cohere/north-mini-code:free"),
    "D": ("groq", "qwen/qwen3.8-27b"),
    "E": ("openrouter", "dots-studio/dots-3-note-preview:free"),
}
CASES = [f"C{i:02d}" for i in range(1, 21)]
VERDICTS = {"correct", "incorrect", "sql_invalid", "sql_rejected", "access_error", "not_executed"}
SECRET = re.compile(r"gsk_[A-Za-z0-9]{10,}|sk-or-v1-[A-Za-z0-9]{10,}")


def current_prompt_shas():
    """Fingerprints the unchanged skeleton gives today, from its own build_prompt."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("skeleton", HERE / "skeleton-multi-llm-en.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["skeleton"] = module
    spec.loader.exec_module(module)
    schema = (HERE / "schema.sql").read_text(encoding="utf-8")
    questions = json.loads((HERE / "questions-td1.json").read_text(encoding="utf-8"))["questions"]
    return {q["id"]: module.build_prompt(schema, q["question"])[2] for q in questions}


def main(pairs):
    references = {r["case_id"]: r["revenue_cents"] for r in csv.DictReader(open(HERE / "reference-td1.csv", newline="", encoding="utf-8"))}
    try:
        expected_sha = current_prompt_shas()
    except Exception as exc:  # the comparison across files below still runs
        print(f"(could not recompute the prompt fingerprints: {exc})")
        expected_sha = {}
    shas, headers, problems = defaultdict(set), {}, 0

    for pair in pairs:
        member, files = pair.split("=", 1)
        csv_path, jsonl_path = (HERE / p for p in files.split(":"))
        issues = []
        text = csv_path.read_text(encoding="utf-8") + jsonl_path.read_text(encoding="utf-8")
        if SECRET.search(text):
            issues.append("API KEY FOUND IN FILE")
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers[member] = reader.fieldnames
            rows = list(reader)
        records = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]

        provider, model = EXPECTED[member]
        if len(rows) != len(records):
            issues.append(f"CSV has {len(rows)} rows, JSONL {len(records)}")
        # Git with core.autocrlf=true turns LF into CRLF inside the CSV fields on checkout: same content.
        crlf = sum("\r\n" in v for row in rows for v in row.values())
        for row, rec in zip(rows, records):
            for key in row:
                value = row[key].replace("\r\n", "\n")
                if str(rec.get(key, "")) != value and not (value == "" and rec.get(key) in (None, "")):
                    try:
                        if float(value) == float(rec.get(key)):
                            continue
                    except (TypeError, ValueError):
                        pass
                    issues.append(f"{row['cell_id']}: CSV/JSONL differ on {key}")
        per_case = defaultdict(list)
        for row in rows:
            per_case[row["case_id"]].append(row)
            shas[row["case_id"]].add(row["prompt_sha256"])
            if (row["provider"], row["model_requested"]) != (provider, model):
                issues.append(f"{row['cell_id']}: model {row['provider']}:{row['model_requested']}, expected {provider}:{model}")
            if row["nature"] != "real":
                issues.append(f"{row['cell_id']}: nature {row['nature']}")
            if row["reference"] != references.get(row["case_id"]):
                issues.append(f"{row['cell_id']}: reference {row['reference']} != {references.get(row['case_id'])}")
            if expected_sha and row["prompt_sha256"] != expected_sha.get(row["case_id"]):
                issues.append(f"{row['cell_id']}: prompt fingerprint differs from the unchanged skeleton")
            if row["verdict"] not in VERDICTS:
                issues.append(f"{row['cell_id']}: unknown verdict {row['verdict']!r}")
            if row["verdict"] == "correct" and row["value"] != row["reference"]:
                issues.append(f"{row['cell_id']}: 'correct' but value {row['value']} != reference")
            if row["verdict"] == "incorrect" and row["value"] == row["reference"]:
                issues.append(f"{row['cell_id']}: 'incorrect' but value equals reference")
        missing = [c for c in CASES if c not in per_case]
        if missing:
            issues.append(f"missing questions: {','.join(missing)}")
        for case, attempts in per_case.items():
            numbers = sorted(int(r["attempts"]) for r in attempts)
            if numbers != list(range(1, len(numbers) + 1)) or len(numbers) > 2:
                issues.append(f"{case}: attempts {numbers} (expected [1] or [1, 2])")

        final = {c: max(rs, key=lambda r: int(r["attempts"])) for c, rs in per_case.items()}
        counts = defaultdict(int)
        for r in final.values():
            counts[r["verdict"]] += 1
        retries = sum(len(rs) - 1 for rs in per_case.values())
        http = sorted({r["http_status"] for r in rows})
        dates = sorted(r["date_utc"] for r in rows)
        summary = ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
        print(f"\n[{member}] {csv_path.name} + {jsonl_path.name}: {provider}:{model}")
        print(f"    {len(rows)} attempt(s), {len(per_case)} question(s), {retries} retry(ies), HTTP {http}, {dates[0] if dates else '-'} -> {dates[-1] if dates else '-'}")
        print(f"    final: {summary}")
        if crlf:
            print(f"    note: {crlf} field(s) with CRLF line endings (Git checkout); content equal to the JSONL")
        for issue in issues:
            print(f"    !! {issue}")
        if not issues:
            print("    OK")
        problems += len(issues)

    print()
    first = next(iter(headers.values()))
    for member, header in headers.items():
        if header != first:
            print(f"!! header of {member} differs from the others")
            problems += 1
    for case in CASES:
        if len(shas[case]) > 1:
            print(f"!! {case}: {len(shas[case])} different prompt fingerprints across files")
            problems += 1
    print("ALL CHECKS PASSED" if problems == 0 else f"{problems} problem(s) found")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
