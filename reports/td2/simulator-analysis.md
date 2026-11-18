# Routing simulator - before and after adaptation (TD 2, Pair C)

All rows are `nature = simulation`: synthetic availability, no provider call. Raw outputs: [simulator-before.jsonl](simulator-before.jsonl) (supplied `atelier-routage.py`) and [simulator-after.jsonl](simulator-after.jsonl) (adapted to [routing-rule.md](routing-rule.md)). Replay: `python atelier-routage.py` (after); `git show 6fcdc5f:atelier-routage.py` gives the supplied version.

## Before: supplied resources and policy

| Scenario | Decision | Resource | Cash | Reason |
|---|---|---|---|---|
| simple (difficulty 1) | run | small-free | 0 | eligible included capacity |
| complex (difficulty 3) | run | senior-subscription | 0 | eligible included capacity |
| deferrable (subscription exhausted, reset 60 min) | defer | senior-subscription | 0 | recheck availability at wake-up (60 min) |
| urgent (cannot wait, deadline 5) | run | senior-api | 0.30 | available route within the authorised budget |
| budget exhausted (budget 0) | abstain | - | 0 | no eligible resource within deadline and budget |
| high impact | run | senior-subscription | 0 | eligible included capacity (checks: source verification and human review) |
| unknown capability (difficulty 4) | abstain | - | 0 | no eligible resource within deadline and budget |

## What we changed

- **RESOURCES**: the five TD 1 models with their real access route, plus the paid OpenRouter route of gpt-oss-120b (0.000914 $ per request, fixed envelope). The capability level is replaced by **`families`**: the families where the model was 100 % in TD 1, with the cells (e.g. `"F2": "4/4 (C02, C08, C09, C11)"`). Portfolio subscriptions (Claude, Codex, Google) are left out: no TD 1 evidence on these questions, so the rule cannot declare them eligible.
- **choose**: same priority order as the supplied policy (free or included capacity, then deferral, then paid route within budget, then abstention). Eligibility = TD 1 evidence on the requested family; tie-break between free routes = price of the paid route of the same model; `checks` follows the table of the rule (family x use); every `reason` quotes the justifying TD 1 cells; an unknown family abstains.

## After: our rule

| Scenario (template id) | Request | Decision | Resource | Cash | Check |
|---|---|---|---|---|---|
| simple (R1) | F1, dashboard | run | groq:openai/gpt-oss-20b, 6/6 (C01, C04-C07, C20) | 0 | none |
| provider unavailable (R2) | F1, 20b down, cannot wait | run | groq:openai/gpt-oss-120b, 6/6 (same cells) | 0 | none |
| complex | F4, customer | run | groq:openai/gpt-oss-20b, 5/5 (C15-C19) | 0 | deterministic check |
| deferrable (R3) | F2, 120b free exhausted, refill 1 min | defer | groq:openai/gpt-oss-120b, 4/4 (C02, C08, C09, C11) | 0 | deterministic check |
| urgent | F2, 120b exhausted, cannot wait | run | openrouter:openai/gpt-oss-120b, same model | 0.000914 | deterministic check |
| budget exhausted (R4) | F2, exhausted, budget 0 | abstain | - | 0 | (eligible: the two 120b routes only) |
| high impact (R5) | F3, payout | run | groq:openai/gpt-oss-20b, 4/4 (C03, C12-C14) | 0 | deterministic check + human review |
| unknown capability | F5, not measured in TD 1 | abstain | - | 0 | no TD 1 evidence |

The one-minute refill models what operator D met in TD 1 (Groq HTTP 429, per model and per minute). "budget exhausted" abstains rather than calling 20b or qwen, which each erred once on F2 (C02, C09).

## Priority in the supplied `choose`: available included capacity before deferral

**Reading of the branches.** `choose` returns at the first non-empty branch. Branch 1 builds `included` = eligible resources that are `available` and have `cash == 0`: it contains the free routes (`allocation == 0`) **and** the subscription (`allocation > 0`). Branch 2 (`waiting` + `defer`) is only evaluated when branch 1 is empty. An exhausted free resource has `available == False`, so it is not in `included`; if the subscription is available, branch 1 returns `run` on it, and the deferral is never considered, even when the free refill comes before `deadline_minutes`. Verified by running the supplied version: free exhausted with a 30-minute refill and subscription available gives `run senior-subscription` ("eligible included capacity"); with the subscription also exhausted, the same request gives `defer small-free` (wake in 30). Inside branch 1, `min` on `allocation` prefers the free route whenever it is available.

**Why this order.** The subscription is already paid: its marginal cost, like the free route's, is 0 cash. Waiting would save nothing, would add latency up to the deadline, and carries a risk: reaching the reset time does not prove the capacity is back (the docstring asks to re-measure at wake-up). Same cost, answer now, no uncertainty: running on the included capacity dominates.

**When to reverse it.** When the included allocation is scarce and has an **opportunity cost**: the subscription quota (0.04 in the scenario) is finite until its own reset; spending it on a request that can wait may leave a later urgent or high-impact request, which cannot wait, with only the paid API (0.30) or an abstention. Operationally: when the remaining subscription allocation falls below what the urgent traffic expected before its reset, and the free refill reliably arrives before the deadline, deferrable requests should wait for the free route and the subscription should be reserved for requests that cannot. The reversal also applies if using the subscription has a marginal cost (overage beyond the allocation) or if, for the family requested, the free model has better evidence than the subscription model.
