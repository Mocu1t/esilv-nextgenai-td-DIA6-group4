#!/usr/bin/env python3
"""TD 1, step 1: compute the twenty reference values and cross-check them.

Two independent computations per question:
  1. a SQLite SELECT run on data/boutique.sqlite opened read-only;
  2. a pure-Python computation on the three CSV files (no SQL), with a
     different age method (anniversary dates instead of year difference).
The script writes reference-td1.csv only if both agree on every question.

Conventions (consigne-etudiante-en.md, section 1):
  - period: date >= start AND date < end (closed left, open right);
  - age: completed years on day D, from month and day;
  - revenue: SUM(quantity_product * price) in cents excluding VAT, 0 when empty.

Coding assistance used (Claude Code); every query is to be read and explained
by the sub-group.

    python cd_build_references.py            # compute, compare, write the CSV
    python cd_build_references.py --check    # compute and compare only
"""
import argparse
import csv
import sqlite3
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "data" / "boutique.sqlite"
OUT = HERE / "reference-td1.csv"

REVENUE = "COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents"
JOIN = "FROM orders o JOIN product p ON p.product_id = o.product_id"
JOIN_C = JOIN + " JOIN customers c ON c.customer_id = o.customer_id"


def period(start, end):
    return f"o.date >= '{start}' AND o.date < '{end}'"


def age_on(day_sql):
    """Completed age on day_sql (an SQL expression 'YYYY-MM-DD'): year difference,
    minus one if the birthday (MM-DD) has not yet come that year."""
    return (f"(CAST(substr({day_sql}, 1, 4) AS INTEGER) - CAST(substr(c.birth_date, 1, 4) AS INTEGER)"
            f" - (substr({day_sql}, 6, 5) < substr(c.birth_date, 6, 5)))")


def aged_25_on(ref):
    return f"{age_on(repr(ref))} = 25"


AGED_25_AT_ORDER = f"{age_on('substr(o.date, 1, 10)')} = 25"


def products(*ids):
    return "o.product_id IN (" + ", ".join(f"'{i}'" for i in ids) + ")"


def select(join, *conditions):
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    return f"SELECT {REVENUE} {join}{where};"


# One spec per question: (period or None, age rule or None, products or None).
# age rule: ("ref", "YYYY-MM-DD") or ("order",).
SPECS = {
    "C01": (("2026-03-01 00:00:00", "2026-06-01 00:00:00"), None, None),
    "C02": (None, ("ref", "2026-09-25"), None),
    "C03": (("2026-01-01 00:00:00", "2026-07-01 00:00:00"), None, ("a", "b", "c")),
    "C04": (("2026-01-01 00:00:00", "2026-10-01 00:00:00"), None, None),
    "C05": (("2026-06-01 00:00:00", "2026-06-02 00:00:00"), None, None),
    "C06": (("2025-01-01 00:00:00", "2026-01-01 00:00:00"), None, None),
    "C07": (("2026-05-31 00:00:00", "2026-06-01 00:00:00"), None, None),
    "C08": (None, ("ref", "2026-09-24"), None),
    "C09": (None, ("ref", "2026-09-26"), None),
    "C10": (None, ("order",), None),
    "C11": (None, ("ref", "2026-12-01"), None),
    "C12": (None, None, ("a", "b", "c")),
    "C13": (("2026-04-01 00:00:00", "2026-05-01 00:00:00"), None, ("a", "c")),
    "C14": (("2026-10-01 00:00:00", "2026-12-01 00:00:00"), None, ("a", "b", "c")),
    "C15": (("2026-03-01 00:00:00", "2026-06-01 00:00:00"), ("ref", "2026-09-25"), None),
    "C16": (None, ("ref", "2026-09-25"), ("a", "b", "c")),
    "C17": (("2026-01-01 00:00:00", "2026-07-01 00:00:00"), ("ref", "2026-09-25"), ("a", "b", "c")),
    "C18": (("2026-05-01 00:00:00", "2026-06-01 00:00:00"), ("order",), None),
    "C19": (("2026-09-01 00:00:00", "2026-10-01 00:00:00"), ("ref", "2026-09-25"), ("d",)),
    "C20": (("2026-06-01 00:00:00", "2026-09-01 00:00:00"), None, None),
}


def sql_for(spec):
    per, age, prods = spec
    conditions = []
    if per:
        conditions.append(period(*per))
    if age:
        conditions.append(aged_25_on(age[1]) if age[0] == "ref" else AGED_25_AT_ORDER)
    if prods:
        conditions.append(products(*prods))
    return select(JOIN_C if age else JOIN, *conditions)


def run_sql(sql):
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        con.execute("PRAGMA query_only = 1")
        rows = con.execute(sql).fetchall()
    finally:
        con.close()
    assert len(rows) == 1 and len(rows[0]) == 1, rows
    return rows[0][0]


# ---- independent check: CSV files, no SQL ---------------------------------

def load_csv(name):
    with open(HERE / "data" / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def is_exactly_25(birth: date, day: date) -> bool:
    """25th anniversary on or before day, 26th anniversary after day.
    A 29 February birthday is celebrated on 1 March in non-leap years."""
    def anniversary(n):
        try:
            return birth.replace(year=birth.year + n)
        except ValueError:
            return date(birth.year + n, 3, 1)
    return anniversary(25) <= day < anniversary(26)


def python_value(spec, orders, prices, births):
    per, age, prods = spec
    total = 0
    for line in orders:
        if per and not (per[0] <= line["date"] < per[1]):
            continue
        if prods and line["product_id"] not in prods:
            continue
        if age:
            day = date.fromisoformat(age[1] if age[0] == "ref" else line["date"][:10])
            if not is_exactly_25(births[line["customer_id"]], day):
                continue
        total += int(line["quantity_product"]) * prices[line["product_id"]]
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="compare only, do not write reference-td1.csv")
    args = parser.parse_args()

    orders = load_csv("orders.csv")
    prices = {r["product_id"]: int(r["price"]) for r in load_csv("product.csv")}
    births = {r["customer_id"]: date.fromisoformat(r["birth_date"]) for r in load_csv("customers.csv")}

    rows, mismatches = [], 0
    for case_id, spec in SPECS.items():
        sql = sql_for(spec)
        sql_value = run_sql(sql)
        py_value = python_value(spec, orders, prices, births)
        status = "OK " if sql_value == py_value else "DIFF"
        mismatches += sql_value != py_value
        print(f"[{status}] {case_id}  sql={sql_value:>10}  csv={py_value:>10}")
        rows.append({"case_id": case_id, "sql": sql, "revenue_cents": sql_value})

    if mismatches:
        print(f"{mismatches} mismatch(es): reference-td1.csv not written.", file=sys.stderr)
        return 1
    if not args.check:
        with open(OUT, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["case_id", "sql", "revenue_cents"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"20/20 agree: written to {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
