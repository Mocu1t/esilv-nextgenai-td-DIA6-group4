# Cross-review 2 of Pair C, by Pair B (Raphael DEMOUGE, Grégoire LEGROS)

Status: **to be completed by Pair B**. Pair C prepared the checklist; only Pair B fills in the result column and the sign-off.

| Check | How | Result (Pair B) |
|---|---|---|
| The age families require a deterministic check, not a quorum | our cases: C02 is wrong under 3-of-5 and C09 under 2-of-3 | |
| We can explain the supplied `choose` priority (subscription before defer) | branch 1 (`included`) returns before branch 2 (`defer`) is evaluated | |
| We can state when to reverse it | scarce subscription allocation with an opportunity cost, and a reliable free refill before the deadline | |
| The "before" output is reproducible | `python td1/atelier-routage.py` gives exactly `simulator-before.jsonl` | |

Sign-off (names, date):
