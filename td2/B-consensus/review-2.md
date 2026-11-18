# Cross-review 2 of Pair B, by Pair A (Aurelien PAYEN, Thibault ALLORY)

Status: **to be completed by Pair A**. Pair C prepared the checklist; only Pair A fills in the result column and the sign-off.

| Check | How | Result (Pair A) |
|---|---|---|
| The quorum verdicts of C02, C09 and C11 match our 20-question table | compare [shared-wrong-values.md](shared-wrong-values.md) with [../A-quorum/td2_step1_comparaison.csv](../A-quorum/td2_step1_comparaison.csv) | |
| We can explain in one sentence why cohere's C11 query returns 0 | it compares the year difference with the 0/1 correction, not with 25 | |
| We can explain why `NOT COALESCE(cond, 0)` and not `NOT cond` in the delta query | `NOT NULL` is NULL, so the row would be dropped | |
| The delta sums equal reference - wrong value | `python td2/B-consensus/cd_shared_wrong_values.py` | |

Sign-off (names, date):
