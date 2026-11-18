# Pair B - The wrong consensus (Step 2)

Members: Raphael DEMOUGE, Grégoire LEGROS. Analysis and commentary: [reports/td2.md, section 3](../../reports/td2.md#3-step-2---the-wrong-consensus-pair-b).

| File | Content |
|---|---|
| [td2_wrong_consensus.ipynb](td2_wrong_consensus.ipynb) | Main case **C11** (real batch). The notebook covers: the shared wrong values found in the 100 cells; the 2-of-3 and 3-of-5 counts; both faulty queries re-executed; the clause diagnosis; the delta query (6 customers, 446690 cents, nothing added); an independent pandas recomputation; and DEMO-VOTE (synthetic). Run it from this folder (needs `pandas`). |
| [cd_shared_wrong_values.py](cd_shared_wrong_values.py) | Complement from the cross-review by Pair C. It applies the same evidence to **every** shared wrong value (C02, C09, C11), and the quorums use Pair A's method. |
| [shared-wrong-values.md](shared-wrong-values.md) | Output of `cd_shared_wrong_values.py`. For each case it gives: the faulty WHERE as returned by each model, re-executed; the missed customers; and the gap explained to the cent. |
| [review-1.md](review-1.md), [review-2.md](review-2.md) | Cross-reviews by Pair C and Pair A |

## Results

| Case | Reference | Shared wrong value | Models | 2-of-3 panel (A, C, D) | 3-of-5 |
|---|---:|---:|---|---|---|
| C02 | 590320 | 0 | B, C, E | correct, 0 outvoted | **0 wins** |
| C09 | 487980 | 0 | C, D | **0 wins** | abstains |
| C11 | 446690 | 0 | C, E | correct, 0 outvoted | correct, 0 outvoted |

All seven faulty queries select **no row**, and `COALESCE(SUM(...), 0)` turns that empty selection into 0. The SQL causes behind them differ:
- reversed subtraction;
- missing reference year;
- age compared with the correction term;
- equality on a single birthday;
- age at the order date;
- an invented order-date filter.

The only check that detects all three cases is the deterministic reference computation. A cheap guard is to count the matched customers before accepting a 0.
