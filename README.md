# Trustworthy generative AI (ESILV) - Sub-group DIA6 - Group 4

Shared repository for TD 1 to TD 3: comparing models on the same SQL questions, the k-of-n vote and the routing rule, then the cost of a configuration.

| Member | TD 1 role | TD 2 pair |
|---|---|---|
| Raphael DEMOUGE | A, operator `groq:openai/gpt-oss-120b` | B, wrong consensus |
| Carl-Edouard AUDUSSEAU | B, operator `groq:openai/gpt-oss-20b` | C, routing |
| Grégoire LEGROS | C, operator `openrouter:cohere/north-mini-code:free` | B, wrong consensus |
| Aurelien PAYEN | D, operator `groq:qwen/qwen3.8-27b` | A, quorum |
| Thibault ALLORY | E, operator `openrouter:dots-studio/dots-3-note-preview:free` | A, quorum |
| Mathias COUDER | F, checker: references, merge of the traces | C, routing |

## Layout

```text
README.md            this page
td1/                 the lab kit (data, skeleton, workshops, assignments) and the TD 1 results
td2/                 TD 2 work, one folder per pair
  A-quorum/          k-of-n vote, 2-of-3 vs 3-of-5 on the 20 questions
  B-consensus/       wrong consensus, faulty SQL, delta queries
  C-routing/         rates per family, routing rule, adapted simulator
td3/                 TD 3 (11 December 2026)
reports/             td1.md, td2.md, td3.md: the session reports handed in on Moodle
```

The kit stays together in `td1/`: `skeleton-multi-llm-en.py` (with the TD 2 vote), `sandbox_sqlite.py`, `atelier-vote.py` and `data/boutique.sqlite` import or read each other. The TD 2 scripts read the TD 1 results from `td1/`.

| Session | Entry point | Report |
|---|---|---|
| TD 1, 21 October 2026 | [td1/README.md](td1/README.md) | [reports/td1.md](reports/td1.md) |
| TD 2, 18 November 2026 | [td2/README.md](td2/README.md) | [reports/td2.md](reports/td2.md) |
| TD 3, 11 December 2026 | [td3/README.md](td3/README.md) | [reports/td3.md](reports/td3.md) |

## Environment

- **Python:** 3.10 or later (we ran 3.12.14). The standard library is enough; only Pair B's notebook needs `pandas`.
- **Database:** `td1/data/boutique.sqlite`, SHA-256 `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2`. Check it with `python td1/check_access.py --no-network`.
- **API keys:** only in environment variables (`GROQ_API_KEY`, `OPENROUTER_API_KEY`), never in this repository. TD 2 makes no call.
- **Coding assistance:** files prefixed `cd_` were written with it, as declared in [td1/prompts-en.md](td1/prompts-en.md) and [td2/prompts-en.md](td2/prompts-en.md).
