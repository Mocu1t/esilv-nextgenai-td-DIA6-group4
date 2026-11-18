# Cross-review 2 of Pair A, by Pair B (Raphael DEMOUGE, Grégoire LEGROS)

Status: **to be completed by Pair B**. Pair C prepared the checklist; only Pair B fills in the result column and the sign-off.

| Check | How | Result (Pair B) |
|---|---|---|
| Our hand count on C11 matches the method | `python td1/atelier-vote.py --traces td1/traces-td1.csv --case C11`: 446690 with 2 votes (A, D) | |
| Same for C02 and C09, the cases where 0 wins a quorum | `python td2/B-consensus/cd_shared_wrong_values.py` | |
| Can we explain why C20 stays at n = 3 under 2-of-3 despite the HTTP 429? | read `vote_k_sur_n`, contract point 1 | |
| Can we explain why k = 2 of 5 is refused? | `n // 2 < k` | |

Sign-off (names, date):
