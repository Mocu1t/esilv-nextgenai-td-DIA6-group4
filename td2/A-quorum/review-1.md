# Cross-review 1 of Pair A, by Pair C (Mathias COUDER, with Claude Code)

Date: 18 November 2026. Reviewed: commit `0344c0b` (`skeleton-multi-llm-en.py`) and `7f48951` (`td2_step1_comparaison.csv`).

## Checks run

| Check | Result |
|---|---|
| `python atelier-vote.py` on the pushed version | **Failed**: `IndentationError` at line 603. `def vote_k_sur_n` was indented 8 spaces instead of 4, so the docstring had no enclosing block. |
| Fix | One line re-indented; no change to the logic. |
| Contract 1: an error stays in n without a vote | OK: `n = len(traces_question)`, then `continue` when `verdict != "executed"` or `value is None` (synthetic "unavailable": 1 vote, abstains). |
| Contract 2: strict majority, else `ValueError` | OK: `if not (n // 2 < k <= n)`. k = 1 of 3 and k = 2 of 5 are refused. |
| Contract 3: duplicate `(provider, model)`, `ValueError` | OK: checked before the verdict, so a duplicate error row is also refused. |
| Contract 4: consensus dict | OK: `models` lists `provider:model_requested` in panel order. |
| Contract 5: abstention dict, never invents a value | OK: `votes` = largest count (0 if nobody voted). |
| Four synthetic examples | agreement 100 (2), disagreement abstains (1), unavailable abstains (1), wrong consensus 0 (2). As expected. |
| 20 questions, 2-of-3, via `atelier-vote.py` | Identical to the `2of3_*` columns of the CSV. |
| 20 questions, 3-of-5, independent replay (`cd_vote_table.py`, the unscored second E run excluded) | Identical to the `3of5_*` columns of the CSV, including C07 4/5, C10 4/5, C20 4/5. |

## Remarks

- The CSV comments are in French. The English commentary required in `reports/td2.md` was written from the regenerated table.
- C17, 3-of-5: the comment "B and E agree on the reference (2 votes), below k = 3" is correct and is worth keeping. It shows a correct value that a quorum cannot keep.
- The 2-of-3 decision depends on `atelier-vote.py` taking the **last** row per model. The merged file also contains the second E run, but Dots is not in the fixed panel, so the 2-of-3 decisions are not affected.
