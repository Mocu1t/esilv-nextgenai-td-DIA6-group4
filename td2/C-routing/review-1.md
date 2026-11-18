# Cross-review 1 of Pair C, by Pair A (Aurelien PAYEN, Thibault ALLORY)

Status: **to be completed by Pair A**. Pair C prepared the checklist; only Pair A fills in the result column and the sign-off.

| Check | How | Result (Pair A) |
|---|---|---|
| The rates per family match the comparison table | `python td2/C-routing/cd_family_rates.py`, then compare with `td1/model-question-comparison-en.csv` | |
| The "after" outputs are reproducible | `python td2/C-routing/atelier-routage.py` gives exactly `simulator-after.jsonl` | |
| We can explain why F2 starts on 120b and F1 on 20b | eligible = 100 % on the family; tie broken on the paid-route price (0.000712 $ vs 0.000914 $) | |
| We can explain why "budget exhausted" abstains instead of calling 20b | 20b erred on C02 (F2): no fallback to a model that erred on the family | |
| The rule's checks are consistent with our vote table | 2-of-3 for a customer figure on F1/F3, where every 2-of-3 decision was correct | |

Sign-off (names, date):
