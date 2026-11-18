# TD 2 report - The quorum, then the routing rule

Sub-group DIA6 - Group 4. Session of 18 November 2026, assignment pack `2026-11-18-students-5`.

**Nature of the evidence.** Every vote, wrong-consensus and routing analysis below runs on the **stored TD 1 traces** (`nature = real`, [td1/traces-td1.csv](../td1/traces-td1.csv)): no new model call was made in TD 2. Queries were re-executed read-only on `td1/data/boutique.sqlite`. The following are **synthetic**, kept apart from the measured counts: the four examples of `atelier-vote.py`, the DEMO-VOTE toy table, and all simulator scenarios (`nature = simulation`). The unscored second run of model E ([td1/traces-E-Mathias.csv](../td1/traces-E-Mathias.csv), see [reports/td1.md](td1.md) 3.3) is excluded from every vote: one proposal per model.

## 1. Work attempted and completed

| Step | Pair | Status | Evidence |
|---|---|---|---|
| 1. k-of-n vote | A | **Done**: method completed; 4 synthetic examples; 20 questions under 2-of-3 and 3-of-5 | [td1/skeleton-multi-llm-en.py](../td1/skeleton-multi-llm-en.py) (`vote_k_sur_n`), [td2/A-quorum/](../td2/A-quorum/) |
| 2. Wrong consensus | B | **Done**: C11 diagnosed in SQL with a delta query and an independent recomputation; DEMO-VOTE executed; complement on C02 and C09 | [td2/B-consensus/](../td2/B-consensus/) |
| 3. Routing rule | C | **Done**: exact rates per family, one-page rule, simulator adapted, outputs before/after, analysis of `choose` | [td2/C-routing/](../td2/C-routing/) |
| Cross-review | all | Pair C reviewed A and B (two defects found and fixed, see 6); the other reviews are recorded in each folder | `td2/*/review-*.md` |
| Prompts | - | Experiment prompt unchanged since TD 1; coding-assistance prompts listed | [td2/prompts-en.md](../td2/prompts-en.md) |

Replay everything, no network, no key (from the repository root):

```bash
python td1/atelier-vote.py                           # 4 synthetic examples
python td1/atelier-vote.py --traces td1/traces-td1.csv --case C02
python td2/A-quorum/cd_vote_table.py                 # the 20 decisions, 2-of-3 vs 3-of-5
python td2/B-consensus/cd_shared_wrong_values.py     # C02, C09, C11: quorums, faulty WHERE, delta queries
python td2/C-routing/cd_family_rates.py              # TD 1 rates per family
python td1/atelier-routage.py                        # simulator, supplied policy (before)
python td2/C-routing/atelier-routage.py              # simulator, our rule (after)
```

## 2. Step 1 - The k-of-n vote (Pair A)

`Orchestrateur.vote_k_sur_n` ([td1/skeleton-multi-llm-en.py](../td1/skeleton-multi-llm-en.py), line 603) follows the contract point by point:

1. `n = len(traces_question)`: an error or an unavailable member stays in n; it is skipped for the count (`verdict != "executed"` or `value is None`).
2. `if not (n // 2 < k <= n): raise ValueError`: only a strict majority is accepted (k = 1 of 3 or k = 2 of 5 is refused).
3. A `(provider, model_requested)` already seen raises `ValueError`, checked before the verdict, so a duplicate is refused even if one of its rows is an error.
4. The first value reaching k is returned with its vote count and the agreeing `provider:model` list. With a strict majority, at most one value can reach k.
5. Otherwise `{"consensus": False, "value": None, "votes": <largest count>, "models": []}`: no value is invented. With no vote at all, `votes = 0`.

**Synthetic examples** (`nature = simulation`, `python td1/atelier-vote.py`, panel 120b / north / qwen, k = 2): agreement `[100, 100, 120]` gives 100 (2 votes); disagreement `[100, 110, 120]` abstains (largest 1); unavailable `[100, None, None]` abstains (1 vote, the two errors stay in n = 3); wrong consensus `[0, 0, 100]` returns **0**, against reference 100.

### Twenty questions: fixed 2-of-3 panel versus 3-of-5 quorum

Fixed panel = A `groq:openai/gpt-oss-120b`, C `openrouter:cohere/north-mini-code:free`, D `groq:qwen/qwen3.8-27b`, k = 2 of 3. Quorum = the five TD 1 models (adds B `groq:openai/gpt-oss-20b` and E `openrouter:dots-studio/dots-3-note-preview:free`), k = 3 of 5. Proposal = the last attempt of each model; the reference ([td1/reference-td1.csv](../td1/reference-td1.csv)) is read **after** the decision. Produced by [cd_vote_table.py](../td2/A-quorum/cd_vote_table.py) with Pair A's method; identical to Pair A's own table [td2_step1_comparaison.csv](../td2/A-quorum/td2_step1_comparaison.csv); CSV: [vote-2of3-vs-3of5.csv](../td2/A-quorum/vote-2of3-vs-3of5.csv).

| Case | Reference | 2-of-3 (A, C, D) | = ref | 3-of-5 (A to E) | = ref | Changed | A / B / C / D / E (last attempt) |
|---|---:|---|---|---|---|---|---|
| C01 | 792800 | 792800 (3) | yes | 792800 (5) | yes | no | all 792800 |
| C02 | 590320 | 590320 (2) | yes | **0 (3)** | **NO** | **yes** | 590320 / 0 / 0 / 590320 / 0 |
| C03 | 936350 | 936350 (3) | yes | 936350 (5) | yes | no | all 936350 |
| C04 | 2826250 | 2826250 (3) | yes | 2826250 (5) | yes | no | all 2826250 |
| C05 | 38480 | 38480 (3) | yes | 38480 (5) | yes | no | all 38480 |
| C06 | 0 | 0 (3) | yes | 0 (5) | yes | no | all 0 (correct: no order in the period) |
| C07 | 13970 | 13970 (3) | yes | 13970 (4) | yes | no | 13970 x4 / E invalid SQL |
| C08 | 605580 | 605580 (2) | yes | 605580 (3) | yes | no | 605580 / 605580 / 0 / 605580 / 171200 |
| C09 | 487980 | **0 (2)** | **NO** | abstain (max 2) | - | **yes** | 487980 / 487980 / 0 / 0 / 47900 |
| C10 | 558980 | 558980 (2) | yes | 558980 (4) | yes | no | 558980 / 558980 / C invalid SQL / 558980 / 558980 |
| C11 | 446690 | 446690 (2) | yes | 446690 (3) | yes | no | 446690 / 446690 / 0 / 446690 / 0 |
| C12 | 1666490 | 1666490 (3) | yes | 1666490 (5) | yes | no | all 1666490 |
| C13 | 107740 | 107740 (3) | yes | 107740 (5) | yes | no | all 107740 |
| C14 | 0 | 0 (3) | yes | 0 (5) | yes | no | all 0 (correct) |
| C15 | 168680 | 168680 (2) | yes | 168680 (3) | yes | no | 168680 / 168680 / 168680 / 0 / 138920 |
| C16 | 376740 | 376740 (2) | yes | 376740 (3) | yes | no | 376740 / 376740 / 376740 / 367050 / 211260 |
| C17 | 258180 | abstain (max 1) | - | abstain (max 2) | - | no | 80190 / 258180 / 197080 / 248490 / 258180 |
| C18 | 62480 | 62480 (3) | yes | 62480 (4) | yes | no | 62480 x4 / E 39580 |
| C19 | 1990 | abstain (max 1) | - | 1990 (3) | yes | **yes** | 1990 / 1990 / 13930 / 83580 / 1990 |
| C20 | 1106090 | 1106090 (2) | yes | 1106090 (4) | yes | no | 1106090 / 1106090 / 1106090 / D HTTP 429 x2 / 1106090 |

**Totals.** 2-of-3: 17 correct consensus, **1 wrong consensus (C09)**, 2 abstentions (C17, C19). 3-of-5: 17 correct consensus, **1 wrong consensus (C02)**, 2 abstentions (C09, C17).

**Questions where the decision changes:**

- **C02, correct to wrong.** 2-of-3: A and D both return 590320 (correct); C's 0 is outvoted. 3-of-5: B (gpt-oss-20b), C and E (dots) all return **0** (verdict `incorrect` for each). 0 reaches k = 3 and wins against the reference 590320. The two models added to the panel make the wrong value the majority.
- **C09, wrong to abstention.** 2-of-3: C and D both return **0** (`incorrect`) against A's correct 487980, so 0 reaches k = 2 and wins. 3-of-5: B joins A on 487980 (2 votes); 0 still has 2 votes (C, D); E proposes a third value, 47900 (`incorrect`). No value reaches 3, so the quorum abstains, which is safe but gives no answer.
- **C19, abstention to correct.** 2-of-3: A 1990, C 13930 and D 83580 are three different values, so the largest count is 1 and the panel abstains. 3-of-5: B and E both join A on 1990, giving 3 votes and a correct consensus.

**Same decision, different margin:** C07 (E: invalid SQL, `no such column: oi.quantity_product`, stays in n = 5 without a vote: 4/5); C10 (C: invalid SQL, `CAST` without `AS`: 2/3 and 4/5); C20 (D: two HTTP 429, `not_executed`: 2/3 and 4/5). These three cases show that an unavailable member stays in n: with one more missing vote, C20 under 2-of-3 would abstain. C17 abstains under both, but B and E agree on the reference 258180 under 3-of-5 (2 votes, below k = 3). Other margins: C08, C11, C15, C16 drop from unanimity to 2 of 3 and 3 of 5 because of a dissenting wrong value. C18 goes to 4/5 because of E's 39580.

**Finding.** Moving from 3 to 5 voters does **not** reduce the number of wrong consensus on this batch (1 each). It only moves the wrong consensus: from C09, where C and D are wrong together, to C02, where B, C and E are wrong together. On age questions the errors are **correlated** and fall on the same value, 0. A larger quorum helps when the errors are scattered (C19), not when they share a cause.

## 3. Step 2 - The wrong consensus (Pair B)

### Main case C11 (real batch, own TD 1 traces)

Notebook: [td2/B-consensus/td2_wrong_consensus.ipynb](../td2/B-consensus/td2_wrong_consensus.ipynb) (executed, outputs kept).

- **Question C11**: revenue excluding VAT of the customers who are exactly 25 on the reference date 2026-12-01, over all their orders.
- **Agreeing models**: C `cohere/north-mini-code:free` ([traces-C.csv](../td1/traces-C.csv)) and E `dots-studio/dots-3-note-preview:free` (scored run [traces-E.csv](../td1/traces-E.csv)). Both return **0**, with verdict `incorrect`. Independent reference: **446690** cents.
- **Quorums**: fixed 2-of-3 panel (A, C, D; k = 2) returns 446690 with 2 votes (A, D): the wrong value is **outvoted**, because Dots is not in the panel. 3-of-5 (k = 3) returns 446690 with 3 votes (A, B, D): 0 gets only 2 votes and is **outvoted**.

**Faulty SQL, as returned by the models** (both re-executed on `boutique.sqlite`: 0):

```sql
-- C, cohere/north-mini-code:free
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (CAST(SUBSTR('2026-12-01', 1, 4) AS INTEGER) - CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER)) =
  CASE WHEN SUBSTR(c.birth_date, 6, 2) > SUBSTR('2026-12-01', 6, 2) THEN 1
       WHEN SUBSTR(c.birth_date, 6, 2) = SUBSTR('2026-12-01', 6, 2)
            AND SUBSTR(c.birth_date, 9, 2) > SUBSTR('2026-12-01', 9, 2) THEN 1
       ELSE 0 END
  AND ((SUBSTR(c.birth_date, 6, 2) < SUBSTR('2026-12-01', 6, 2)) OR
       (SUBSTR(c.birth_date, 6, 2) = SUBSTR('2026-12-01', 6, 2)
        AND SUBSTR(c.birth_date, 9, 2) <= SUBSTR('2026-12-01', 9, 2)));
-- (the model's comments are removed here; the verbatim query is in the notebook and in shared-wrong-values.md)

-- E, dots-studio/dots-3-note-preview:free
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (c.birth_date IS NOT NULL) AND
      (strftime('%Y-%m-%d', c.birth_date, '25 years') = '2026-12-01');
```

**Diagnosis.** The required window is "born from 2000-12-02 to 2001-12-01 inclusive" (6 customers). The two models make **two different errors**:
- **C (cohere)** computes the correction for "birthday not reached yet" (0 or 1), but compares the year difference **to that correction** instead of subtracting the correction and comparing the result to 25. The number 25 never appears in the query. Combined with "birthday reached", the condition keeps only customers born in 2026, and there are none (birth dates run from 1958 to 2006).
- **E (dots)** tests that the 25th birthday falls **on** 2026-12-01, i.e. born exactly on 2001-12-01. That is "turning 25 that day", not "being 25 that day", and no customer matches.

Both selections are empty, and `COALESCE(SUM(...), 0)` turns an empty selection into **0**. So 0 is the value that any query selecting nothing produces. Agreement on 0 is weak evidence: two independent bugs give the same plausible value.

**Delta query, executed** on `boutique.sqlite`: it selects the rows that pass the reference condition AND NOT the faulty condition, grouped by customer. The result is the same for C and E:

```sql
SELECT c.customer_id, c.birth_date, SUM(o.quantity_product * p.price) AS revenue_cents
FROM orders o
JOIN product p   ON p.product_id = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE (CAST(substr('2026-12-01', 1, 4) AS INTEGER) - CAST(substr(c.birth_date, 1, 4) AS INTEGER)
       - (substr('2026-12-01', 6, 5) < substr(c.birth_date, 6, 5))) = 25
  AND NOT COALESCE((<faulty WHERE of C or E>), 0)
GROUP BY c.customer_id, c.birth_date ORDER BY c.customer_id;
```

| customer_id | birth_date | missed revenue (cents) |
|---|---|---:|
| C001 | 2001-09-25 | 135000 |
| C002 | 2001-09-24 | 25920 |
| C003 | 2001-09-26 | 47900 |
| C006 | 2001-11-30 | 77450 |
| C008 | 2001-05-15 | 99090 |
| C009 | 2001-03-10 | 61330 |
| **total** | | **446690** |

The reverse direction (rows counted by the faulty query but not by the reference) is empty. The gap 446690 - 0 is therefore explained **to the cent**. The boundary trap is C007 (born 2000-11-30): already 26 on 2026-12-01, and correctly excluded by the reference.

**Independent check.** The notebook recomputes the value in pandas without reusing the SQL: it parses the dates, applies the completed-age rule, and cross-checks with the window ]2000-12-01, 2001-12-01]. Result: 446690 = reference. The reference itself was validated in TD 1 by a second, CSV-based method and by the instructor's answer key ([reports/td1.md](td1.md)).

### Where the shared wrong value wins a quorum: C02 and C09 (real batch)

Running the same diagnosis on the whole batch ([cd_shared_wrong_values.py](../td2/B-consensus/cd_shared_wrong_values.py), output in [shared-wrong-values.md](../td2/B-consensus/shared-wrong-values.md)) finds three shared wrong values, all **0** and all on F2 (age on a reference date):

| Case | Reference | Models on 0 | 2-of-3 (A, C, D) | 3-of-5 | Faulty WHERE (each re-executed: 0) | Delta query |
|---|---:|---|---|---|---|---|
| C02 | 590320 | B, C, E | 590320, correct | **0 wins** | B: born in ]2025-09-25, 2026-09-25] (age 0); C: `birth_year - 2026 = 25` (reversed subtraction, born in 2051); E: born exactly 2001-09-25 **and** an invented filter "ordered on 2026-09-25" | 6 customers, 590320, nothing added |
| C09 | 487980 | C, D | **0 wins** | abstains | C: `birth_year - correction = 25` (the reference year 2026 is missing, so born in year 25 or 26); D: age at the **order date** instead of the reference date, and `m-d >= birth m-d AND m-d < (birth + 26 years) m-d` can never hold | 6 customers, 487980, nothing added |
| C11 | 446690 | C, E | 446690, correct | 446690, correct | see above | 6 customers, 446690, nothing added |

C09 is the **wrong consensus of the fixed panel**: two of the three panel families fail on the same question with different SQL, and k = 2 accepts 0. C02 is the **wrong consensus of the 3-of-5 quorum**. In all 7 faulty queries, the selection is empty (each delta covers the gap and adds no row). The error does not show in the value: 0 is also the correct answer to C06 and C14.

### DEMO-VOTE (synthetic, constructed teaching material)

This is a one-row toy table: a sale on 2026-01-01 of 100 cents, with the period [2026-01-01, 2026-01-02). It is executed in the notebook, section 8. The variant `sale_date > '2026-01-01'` returns **0**, because the strict bound excludes the sale made on the opening day. The variant `>= '2026-01-01'` returns **100**. With proposals `[0, 0, 100]` and k = 2 of 3, the quorum returns 0 against the reference 100. Two proposals sharing the same boundary error outvote the correct one.

### Consequence for the panel and the checking

- A quorum measures **agreement, not correctness**. On this batch, both quorums accept exactly one wrong value, and the panel composition alone decides which question is hit. Picking "the right panel" after seeing the results would be overfitting: a 2-of-3 panel of {C, E, any} returns 0 on C11.
- **Independent check that detects the error.** The deterministic reference computation (`script#script` in the portfolio: the validated SQL, 20/20 against the answer key) detects all three cases. It is the check our routing rule requires on the age families (section 4).
- **Cheap guard for TD 3:** any 0 produced by `COALESCE` on an empty selection should trigger a count of matched customers or rows (here 0 against 6) before the value is accepted. A different panel or an escalation is a candidate check, not a guarantee.

## 4. Step 3 - The routing rule (Pair C)

Full rule (one page): [td2/C-routing/routing-rule.md](../td2/C-routing/routing-rule.md). The rates come from the scored TD 1 table ([td1/model-question-comparison-en.csv](../td1/model-question-comparison-en.csv)) and are computed by [cd_family_rates.py](../td2/C-routing/cd_family_rates.py).

| Family | Cells | 120b | 20b | north | qwen | dots | All |
|---|---|---|---|---|---|---|---|
| F1 period | C01, C04-C07, C20 | **6/6** | **6/6** | **6/6** | 5/5 + C20 not run | 5/6 (C07) | 28/29 |
| F2 age on a reference date | C02, C08, C09, C11 | **4/4** | 3/4 (C02) | 0/4 | 3/4 (C09) | 0/4 | 10/20 |
| F2b age at the order | C10 | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 | 4/5 |
| F3 product list | C03, C12-C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 20/20 |
| F4 combinations | C15-C19 | 4/5 (C17) | **5/5** | 3/5 | 1/5 | 2/5 | 15/25 |

| Family | First model (eligible = 100 % on the family) | If unavailable | Dashboard | Customer | Payout |
|---|---|---|---|---|---|
| F1 | gpt-oss-20b (6/6) | 120b, qwen, north | none | 2-of-3 quorum | deterministic check + review |
| F2 | gpt-oss-120b (4/4, the only one) | wait for the 120b refill, else paid 120b route, else abstain | deterministic check | deterministic check | deterministic check + review |
| F2b | gpt-oss-20b (1/1, weak evidence) | 120b, qwen, dots | deterministic check | deterministic check | deterministic check + review |
| F3 | gpt-oss-20b (4/4) | 120b, qwen, north, dots | none | 2-of-3 quorum | deterministic check + review |
| F4 | gpt-oss-20b (5/5, the only one) | wait for the 20b refill, else abstain | deterministic check | deterministic check | deterministic check + review |

"Cheapest": all five routes are free, so the tie is broken on the price of the paid route of the same model, for the envelope of 2000 input and 1024 output tokens:

| Model | Paid route | Price per request |
|---|---|---:|
| 20b | Groq | 0.000712 $ |
| 120b | OpenRouter | 0.000914 $ |
| qwen | OpenRouter | 0.001462 $ |

north and dots have no documented price.

The check follows the risk of a **silent wrong value**. On F1 and F3, the only error (E/C07) is invalid SQL, rejected by the sandbox. On the age families, the errors are plausible shared values that quorums accepted (section 3). On F2 we also require a check for the dashboard: 120b's 4/4 is contradicted by its only error A/C17, an F2-convention error, and 4/4 only bounds the true rate above about 47 % (one-sided 95 %).

### Simulator: before and after adaptation

Outputs: [simulator-before.jsonl](../td2/C-routing/simulator-before.jsonl) (supplied policy, kept runnable as [td1/atelier-routage.py](../td1/atelier-routage.py)) and [simulator-after.jsonl](../td2/C-routing/simulator-after.jsonl) ([td2/C-routing/atelier-routage.py](../td2/C-routing/atelier-routage.py)). Detailed reading: [simulator-analysis.md](../td2/C-routing/simulator-analysis.md).

| Scenario | Before (fictitious resources) | After (our rule; each reason quotes the TD 1 cells) |
|---|---|---|
| simple | run small-free | run gpt-oss-20b, F1 6/6, no check |
| provider unavailable | - | 20b down, cannot wait: run gpt-oss-120b, F1 6/6 |
| complex | run senior-subscription | F4 customer: run gpt-oss-20b 5/5 + deterministic check |
| deferrable | defer senior-subscription (60 min) | F2, 120b free exhausted, refill 1 min: defer 120b |
| urgent | run senior-api, 0.30 | F2, cannot wait: run the paid OpenRouter 120b route, 0.000914 $ |
| budget exhausted | abstain | F2, budget 0: abstain (only the two 120b routes are eligible) |
| high impact | run senior-subscription + checks | F3 payout: run 20b + deterministic check + human review |
| unknown capability | abstain | F5 not measured in TD 1: abstain |

### Priority in the supplied `choose`: available included capacity before deferral

`choose` returns at the first non-empty branch:

1. **Branch 1** builds `included` = eligible resources that are `available` with `cash == 0`. It contains the free routes (`allocation == 0`) **and** the subscription (`allocation > 0`).
2. **Branch 2** (`defer`) is evaluated only when branch 1 is empty.

An exhausted free route has `available == False`, so it is not in `included`. If the subscription is available, branch 1 returns `run` on it, and deferral is never considered, even when the free refill comes before `deadline_minutes`. We checked this on the supplied code:

| Free route | Subscription | Decision |
|---|---|---|
| exhausted, refill 30 min | available | `run senior-subscription` |
| exhausted, refill 30 min | exhausted | `defer small-free` |

**Why this order:** the subscription is already paid, so its marginal cost is 0, like the free route's. Waiting saves nothing and adds latency. It is also uncertain: reaching the reset time does not prove the capacity is back.

**When to reverse it:** when the subscription allocation is **scarce and has an opportunity cost**. Spending it on a request that can wait may leave a later urgent or high-impact request with only the paid API (0.30) or an abstention. Operationally, reverse the priority when:
- the remaining allocation falls below the urgent traffic expected before its reset, and
- the free refill reliably arrives before the deadline.

Also reverse it if the subscription has a marginal cost (overage beyond the allocation), or if the free model has better TD 1 evidence on the family than the subscription model.

## 5. Observed causes and hypotheses

- **Age is where models fail, and where they fail together.** All three shared wrong values are F2 questions, all equal to 0, and each comes from an empty selection. The causes differ:
  - reversed subtraction;
  - missing reference year;
  - comparison with the correction term;
  - equality on a single birthday;
  - age at the order date;
  - an invented order-date filter.

  Hypothesis for this batch: `COALESCE(SUM(...), 0)`, required by the prompt, turns every empty selection into a value that looks plausible.
- **A bigger quorum is not a better quorum when errors are correlated** (C02 against C09). Diversity of families does not prevent it: B and A belong to the same family (gpt-oss) and disagree on C02, while C and E, from different families, agree on 0.
- **Simple period and product questions** (F1, F3) are answered correctly by every model, except for one invalid SQL. Routing them to the cheapest model, without a check for the internal dashboard, is consistent with TD 1.

## 6. Successes, failures and incidents

- **Defect found in cross-review (Pair A):** the pushed `skeleton-multi-llm-en.py` did not compile. The `def vote_k_sur_n` line was indented 4 spaces too deep (`IndentationError`), so `atelier-vote.py` could not load it. The fix is that one line, with the logic unchanged. After the fix, our replay with the method gives exactly the decisions of Pair A's table.
- **Pair A's table is in French** ([td2_step1_comparaison.csv](../td2/A-quorum/td2_step1_comparaison.csv)): kept as delivered. The English table above is regenerated from the method.
- **Pair B's notebook chooses the Dots row by its order in the CSV** (`iloc[0]`). This happens to give the scored run (traces-E.csv, 0). The rule we apply is explicit: the unscored second E run is excluded (on C11 that run returned the correct 446690, another sign that Dots is not reproducible at temperature 0).
- **Repository layout** aligned with the instructor's structure:
  - kit and TD 1 under `td1/`, with paths updated and all scripts re-run;
  - TD 2 by pair under `td2/`;
  - reports under `reports/`.

  Moves were made with `git mv`, so file history is kept.
- **Not done:** no new network experiment (not required); the quorums were not re-run on the second E run.

## 7. Limitations

- **Small sample.** There are 20 questions and one pass per model, so one cell moves a rate by 5 to 25 points depending on the family (F2b has a single cell). The rates are a hypothesis for this batch, not an error rate, a ranking or a quorum guarantee.
- **Fictitious simulator inputs.** The availabilities and refill times of the simulator are scenarios. The one-minute refill imitates the Groq HTTP 429 seen in TD 1. The prices are those of the paid routes of the same models, not of the free access actually used.
- **Unproven check.** The deterministic check is the validated reference SQL. It covers these 20 questions, but a new question needs its own reference, and that is the cost to price in TD 3.

## 8. Contributions

| Member | Pair | Contribution |
|---|---|---|
| Aurelien PAYEN | A (vote) | `vote_k_sur_n` in the skeleton; synthetic examples; 20-question 2-of-3 / 3-of-5 table (`td2_step1_comparaison.csv`) |
| Thibault ALLORY | A (vote) | `vote_k_sur_n` and 20-question comparison with Aurelien |
| Raphael DEMOUGE | B (consensus) | Notebook `td2_wrong_consensus.ipynb`: shared wrong values, C11 diagnosis, delta query, independent pandas check, DEMO-VOTE |
| Grégoire LEGROS | B (consensus) | C11 diagnosis, delta query and independent check, with Raphael |
| Mathias COUDER | C (routing) | Rates per family, routing rule, adapted simulator and priority analysis; cross-review of A and B (compile fix, independent replay of the vote table, C02/C09 complement); repository layout; this report |
| Carl-Edouard AUDUSSEAU | C (routing) | Routing rule and simulator adaptation, with Mathias |

**Coding assistance, declared.** Mathias used Claude Code (Claude Opus 5.5). The files prefixed `cd_`, the Pair C documents and this report were written with it; its prompts are listed in [td2/prompts-en.md](../td2/prompts-en.md). The sub-group reviewed the code and queries and can explain them. No reference value comes from a model.

## 9. Next steps (TD 3)

- **Questions where no free model is enough on its own:**
  - F2 for any use beyond the dashboard (best: 120b 4/4, yet 10/20 overall);
  - F2b, which has a single cell;
  - F4, where only 20b is 5/5.

  These set the price of checking in TD 3: deterministic check (0 $, but one reference SQL per question), a paid route, or a human review.
- Add the "empty selection" guard: count the matched rows before accepting a 0.
- Quantify each configuration (single model, 2-of-3, 3-of-5, rule plus check) on the 20 decisions above, with the cost method of [methode-cout-en](../td1/methode-cout-en.md).
