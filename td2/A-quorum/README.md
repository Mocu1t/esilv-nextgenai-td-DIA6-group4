# Pair A - The k-of-n vote (Step 1)

Members: Aurelien PAYEN, Thibault ALLORY. Analysis and commentary: [reports/td2.md, section 2](../../reports/td2.md#2-step-1---the-k-of-n-vote-pair-a).

| File | Content |
|---|---|
| [../../td1/skeleton-multi-llm-en.py](../../td1/skeleton-multi-llm-en.py) | `Orchestrateur.vote_k_sur_n`, line 603. The skeleton stays in the kit: `atelier-vote.py` loads it from its own folder, and it imports `sandbox_sqlite.py`. |
| [td2_step1_comparaison.csv](td2_step1_comparaison.csv) | Pair A's 20-question table, 2-of-3 vs 3-of-5, with comments in French, as delivered |
| [cd_vote_table.py](cd_vote_table.py) | Regenerates the table with the method, from the stored traces (cross-review, Pair C) |
| [vote-2of3-vs-3of5.csv](vote-2of3-vs-3of5.csv) | Output of `cd_vote_table.py --csv`; same decisions as Pair A's table |
| [review-1.md](review-1.md), [review-2.md](review-2.md) | Cross-reviews by Pair C and Pair B |

```bash
python td1/atelier-vote.py                                         # 4 synthetic examples (nature = simulation)
for c in C01 C02 ... C20: python td1/atelier-vote.py --traces td1/traces-td1.csv --case $c   # fixed 2-of-3 panel
python td2/A-quorum/cd_vote_table.py --csv td2/A-quorum/vote-2of3-vs-3of5.csv              # 2-of-3 and 3-of-5
```

## Results in one line each

- **2-of-3 panel** (120b, north, qwen): 17 correct, 1 wrong consensus (**C09**, 0), 2 abstentions (C17, C19).
- **3-of-5 quorum**: 17 correct, 1 wrong consensus (**C02**, 0), 2 abstentions (C09, C17).
- **Changed decisions:** C02 (correct to wrong), C09 (wrong to abstention), C19 (abstention to correct).
- **Margins only:** C07, C10 and C20 (invalid SQL and HTTP 429 stay in n without a vote).
