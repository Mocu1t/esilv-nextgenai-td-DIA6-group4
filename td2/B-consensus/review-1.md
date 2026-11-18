# Cross-review 1 of Pair B, by Pair C (Mathias COUDER, with Claude Code)

Date: 18 November 2026. Reviewed: commit `7aa7ded` (`TD2/td2_wrong_consensus.ipynb`, now `td2/B-consensus/`).

## Checks run

| Check | Result |
|---|---|
| Shared wrong values in the 100 cells | Same three as the notebook: C02 (B, C, E on 0), C09 (C, D on 0), C11 (C, E on 0). |
| C11 votes against Pair A's method | 2-of-3: 446690 (A, D); 3-of-5: 446690 (A, B, D). Same as the notebook's hand count. |
| Faulty queries re-executed read-only on `boutique.sqlite` | Both 0, equal to the traces. |
| Reference query | 446690 = `reference-td1.csv`. |
| Delta query, both directions | 6 customers, 446690 missed, 0 added. Explained to the cent. |
| Independent pandas check | 446690. The age rule is cross-checked with a date window; boundary customer C007 excluded. |
| DEMO-VOTE | `>` gives 0, `>=` gives 100; `[0, 0, 100]` with k = 2 gives 0. Labelled synthetic. |

## Remarks and changes made

- **Paths**: after the move to `td2/B-consensus/`, the three paths in cell 0 now point to `../../td1/`. No other change to the notebook.
- **Dots row**: cell 9 takes `iloc[0]` per model. On C11 this is the scored run (traces-E.csv, 0) only because of the row order. The cell 7 comment says "the last attempt counts", but the real rule is that **only the scored run counts**: the second E run (traces-E-Mathias.csv, 446690) is excluded. The conclusion does not change, but the report states the rule explicitly.
- **Choice of case**: C11 meets the deliverable, but the shared 0 loses both quorums there. We added C02 (0 wins the 3-of-5) and C09 (0 wins the fixed 2-of-3 panel) with the same evidence, in `cd_shared_wrong_values.py`. The panel and quorum consequences are clearer on those two cases.
- **DEMO-SQL-C11**: not needed, because our batch has its own shared wrong values. Note that the pilot's M1 query (20b, `birth_date = '2001-12-01'`) has the same "birthday on the day" flaw as our E/C11.
