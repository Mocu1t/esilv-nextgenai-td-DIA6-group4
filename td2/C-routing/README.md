# Pair C - The routing rule (Step 3)

Members: Mathias COUDER, Carl-Edouard AUDUSSEAU. Summary: [reports/td2.md, section 4](../../reports/td2.md#4-step-3---the-routing-rule-pair-c).

| File | Content |
|---|---|
| [cd_family_rates.py](cd_family_rates.py) | Exact TD 1 rates per family and model, from [td1/model-question-comparison-en.csv](../../td1/model-question-comparison-en.csv) |
| [routing-rule.md](routing-rule.md) | **The one-page rule**. Per family: rates with cells, first model, fallback, and the check for each use. |
| [atelier-routage.py](atelier-routage.py) | The simulator, adapted to the rule: `RESOURCES` = the five TD 1 models plus the paid 120b route; `choose` = eligibility from TD 1 evidence, and every reason quotes the cells. |
| [simulator-before.jsonl](simulator-before.jsonl) | Output of the supplied simulator (kept runnable as [td1/atelier-routage.py](../../td1/atelier-routage.py)) |
| [simulator-after.jsonl](simulator-after.jsonl) | Output of the adapted simulator, 8 scenarios |
| [simulator-analysis.md](simulator-analysis.md) | Before/after reading, and why available included capacity comes before deferral in `choose` (and when to reverse it) |
| [review-1.md](review-1.md), [review-2.md](review-2.md) | Cross-reviews by Pair A and Pair B |

```bash
python td2/C-routing/cd_family_rates.py
python td1/atelier-routage.py        > td2/C-routing/simulator-before.jsonl
python td2/C-routing/atelier-routage.py > td2/C-routing/simulator-after.jsonl
python td2/C-routing/atelier-routage.py --scenario deferrable
```
