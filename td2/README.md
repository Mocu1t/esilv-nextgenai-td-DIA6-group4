# TD 2 - The quorum, then the routing rule (18 November 2026)

Assignment: [td1/enonce-td2-en.md](../td1/enonce-td2-en.md) (the final version, pack `2026-11-18-students-5`, was distributed as a PDF). Session report: **[reports/td2.md](../reports/td2.md)**.

No new model call: everything runs on the stored TD 1 traces ([td1/traces-td1.csv](../td1/traces-td1.csv), scored run; the unscored second E run is excluded from the votes).

| Pair | Members | Step | Folder |
|---|---|---|---|
| A | Aurelien PAYEN, Thibault ALLORY | 1. k-of-n vote, 2-of-3 vs 3-of-5 | [A-quorum/](A-quorum/) |
| B | Raphael DEMOUGE, Grégoire LEGROS | 2. Wrong consensus in SQL | [B-consensus/](B-consensus/) |
| C | Mathias COUDER, Carl-Edouard AUDUSSEAU | 3. Routing rule and simulator | [C-routing/](C-routing/) |

Each folder has a `README.md` and two cross-reviews (`review-1.md`, `review-2.md`), one by each of the other pairs.

## Evaluated artefacts

| # | Artefact | Where |
|---|---|---|
| 1 | `skeleton-multi-llm-en.py` with `vote_k_sur_n` completed | [td1/skeleton-multi-llm-en.py](../td1/skeleton-multi-llm-en.py) (the kit stays together; the workshop loads it from there) |
| 2 | 20-question table, 2-of-3 vs 3-of-5, with commentary | [reports/td2.md, section 2](../reports/td2.md#twenty-questions-fixed-2-of-3-panel-versus-3-of-5-quorum), [A-quorum/vote-2of3-vs-3of5.csv](A-quorum/vote-2of3-vs-3of5.csv) |
| 3 | Wrong consensus verified on `boutique.sqlite`, delta query | [reports/td2.md, section 3](../reports/td2.md#3-step-2---the-wrong-consensus-pair-b), [B-consensus/](B-consensus/) |
| 4 | One-page routing rule with TD 1 rates and cells | [C-routing/routing-rule.md](C-routing/routing-rule.md) |
| 5 | Simulator outputs before / after, priority in `choose` | [C-routing/simulator-before.jsonl](C-routing/simulator-before.jsonl), [simulator-after.jsonl](C-routing/simulator-after.jsonl), [simulator-analysis.md](C-routing/simulator-analysis.md) |
| 6 | Prompts, as used | [prompts-en.md](prompts-en.md) (experiment prompt unchanged since TD 1) |

## Replay (from the repository root, no network, no key)

```bash
python td1/atelier-vote.py                                        # 4 synthetic examples
python td1/atelier-vote.py --traces td1/traces-td1.csv --case C09 # one question, fixed 2-of-3 panel
python td2/A-quorum/cd_vote_table.py                              # the 20 decisions, 2-of-3 vs 3-of-5
python td2/B-consensus/cd_shared_wrong_values.py                  # C02, C09, C11: quorums and delta queries
python td2/C-routing/cd_family_rates.py                           # TD 1 rates per family
python td1/atelier-routage.py                                     # supplied policy (before)
python td2/C-routing/atelier-routage.py                           # our rule (after)
```

The notebook [B-consensus/td2_wrong_consensus.ipynb](B-consensus/td2_wrong_consensus.ipynb) runs from its own folder (it needs `pandas`).
