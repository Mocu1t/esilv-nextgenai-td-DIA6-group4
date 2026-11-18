# Routing rule - sub-group DIA6 - Group 4 (TD 2, Pair C)

Scope: the revenue questions of TD 1 (SQL written by a model, executed read-only, value checked). Evidence: the scored TD 1 run, last attempt per cell, [model-question-comparison-en.csv](../../td1/model-question-comparison-en.csv); rates computed by [cd_family_rates.py](cd_family_rates.py). Twenty questions support a hypothesis for this batch, not a general error rate, a permanent ranking or a quorum guarantee.

## 1. TD 1 rates per family (correct / evaluated cells)

| Family | Cells | 120b | 20b | north | qwen | dots | All |
|---|---|---|---|---|---|---|---|
| F1 period | C01, C04-C07, C20 | **6/6** | **6/6** | **6/6** | 5/5 + C20 not run | 5/6 (C07) | 28/29 |
| F2 age on a reference date | C02, C08, C09, C11 | **4/4** | 3/4 (C02) | 0/4 | 3/4 (C09) | 0/4 | 10/20 |
| F2b age at the order | C10 | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 | 4/5 |
| F3 product list | C03, C12-C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 20/20 |
| F4 combinations | C15-C19 | 4/5 (C17) | **5/5** | 3/5 | 1/5 | 2/5 | 15/25 |

Model ids: `groq:openai/gpt-oss-120b`, `groq:openai/gpt-oss-20b`, `openrouter:cohere/north-mini-code:free`, `groq:qwen/qwen3.8-27b`, `openrouter:dots-studio/dots-3-note-preview:free`. D/C20 (HTTP 429 twice) is not a model error and is left out of correct/cases.

## 2. First model called and fallback

**Eligible** = 100 % on the evaluated cells of the family. **Cheapest**: all five routes are free (0 $), so the portfolio cannot separate them; the declared tie-break is the price of the paid route of the same model, i.e. what the request costs once the free quota is gone (envelope of `modeles-autorises.json`: 2000 input + 1024 output tokens): gpt-oss-20b 0.000712 $ (Groq 0.10/0.50, five-model summary) < gpt-oss-120b 0.000914 $ (OpenRouter 0.15/0.60, portfolio) < qwen3.8-27b 0.001462 $ (OpenRouter 0.04/1.35, catalogue 2026-10-21). north and dots have no documented price (absent from the portfolio, `:free` only): never "the cheapest", kept as fallbacks. The overall TD 1 rate cannot break the tie (120b and 20b both 19/20).

| Family | First model | Then, if unavailable |
|---|---|---|
| F1 | gpt-oss-20b (6/6) | gpt-oss-120b (6/6), qwen (5/5), north (6/6) |
| F2 | gpt-oss-120b (4/4, the only one) | **no other free model qualifies**: defer to the 120b refill, else the paid route of the same 120b, else abstain |
| F2b | gpt-oss-20b (1/1: one cell, weak evidence) | 120b, qwen, dots (1/1 each) |
| F3 | gpt-oss-20b (4/4) | 120b, qwen, north, dots (4/4 each) |
| F4 | gpt-oss-20b (5/5, the only one) | defer to the 20b refill, else abstain (120b erred on C17) |

**Course of action when the first model is unavailable**: next eligible free model; if none, wait for the refill when the request can wait and the refill comes before the deadline (re-measure availability at wake-up); otherwise the paid route of an eligible model within budget; otherwise **abstain**. Never fall back to a model that erred on the family.

## 3. Check by use (cost of an error)

| Family | Internal dashboard | Figure shown to the customer | Amount paid out |
|---|---|---|---|
| F1, F3 | none | 2-of-3 quorum (distinct families) | deterministic check + human review |
| F2, F2b, F4 | deterministic check | deterministic check | deterministic check + human review |

*Deterministic check* = `script#script` of the portfolio (local, 0 $, retained): the validated reference SQL, 20/20 against the answer key.

**Why.** The check follows the risk of a **silent wrong value**, not the bare rate. On F1/F3 the only TD 1 error (E/C07) is invalid SQL, rejected by the sandbox: no value comes out, so "none" is acceptable for an internal dashboard, as the consistency constraint allows (first model 100 % on the family). On the age families the errors are plausible values **shared between models**, and a quorum accepts them: on C02, 0 wins the 3-of-5 quorum (20b, north, dots); on C09, 0 wins the 2-of-3 panel (north, qwen). Only the deterministic check covers them. On F2 we go beyond the minimum: 120b's 4/4 is contradicted by its only error, A/C17, which is an F2 convention error (`birth_date = date('2026-09-25','-25 years')`); 4/4 only bounds its true rate above about 47 % (one-sided 95 %, 0.05^(1/4)); the family is at 10/20 overall; the check costs nothing.

**Questions where no free model is enough on its own** (for TD 3): F2 for any use beyond the dashboard, F2b and F4 for every use.
