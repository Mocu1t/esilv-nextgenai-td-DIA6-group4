# TD 1 report - Comparing models on the same questions

Sub-group DIA6 - Group 4. Session of 21 October 2026, pack `2026-10-18-students-1`.
All trace rows are `nature = real`: no replayed or simulated row enters the results below.

## 1. Work attempted and completed

| Step | Status | Evidence |
|---|---|---|
| Opening check | Done before the session: `check_access.py` 5/5 OK | kept locally (not committed: `ready-for-td1.txt` is in `.gitignore`) |
| 1. Twenty references | **Done, 20/20 equal to the answer key on the first attempt** | [reference-td1.csv](../reference-td1.csv) |
| 2. Five models, 100 cells | **Done: 100/100 cells attempted, 99 with a final verdict** | [traces-td1.csv](../traces-td1.csv), [traces-td1.jsonl](../traces-td1.jsonl), per-operator `traces-*.csv` / `state-*.jsonl` |
| 3. Traces read, two summaries | **Done: 100 comparison rows, every failure explained from its SQL/error** | [model-question-comparison-en.csv](../model-question-comparison-en.csv), [five-model-summary-en.csv](../five-model-summary-en.csv), pivot [cd_pivot-td1.md](../cd_pivot-td1.md) |
| Prompts as used | Done, kit prompt unchanged | [prompts-en.md](../prompts-en.md) |

**References.** Each SQL query was computed on `data/boutique.sqlite` opened read-only and independently recomputed in plain Python on the three CSV files, with a different age method (25th anniversary <= reference date < 26th anniversary) ([cd_build_references.py](../cd_build_references.py)). The two agreed 20/20, then each query was checked by one member (`checked_by` column) and the twenty values were compared with the instructor's answer key: no difference. No value comes from a model.

**Calls.** 126 HTTP attempts: 120 initial calls (60 Groq, 60 OpenRouter, of which 20 belong to a second, unscored E run, see 3.3) and 6 retries. HTTP status: 119 x 200, 6 x 429, 1 timeout. Every row of a question carries the same prompt fingerprint across models, runs and attempts ([prompts-en.md](../prompts-en.md), table of fingerprints). All rows were checked by [cd_check_traces.py](../cd_check_traces.py): expected model, reference, nature, attempts <= 2, CSV equal to JSONL, no API key.

## 2. Results

Final verdict = last attempt of each cell ([model-question-comparison-en.csv](../model-question-comparison-en.csv)).

| Operator | Model (access) | Correct | Other final verdicts |
|---|---|---:|---|
| A | `openai/gpt-oss-120b` (Groq Free) | 19/20 | C17 incorrect |
| B | `openai/gpt-oss-20b` (Groq Free) | 19/20 | C02 incorrect |
| D | `qwen/qwen3.8-27b` (Groq Free) | 14/20 | 5 incorrect, C20 not executed (2 x HTTP 429) |
| C | `cohere/north-mini-code:free` (OpenRouter) | 13/20 | 6 incorrect, C10 invalid SQL |
| E | `dots-studio/dots-3-note-preview:free` (OpenRouter) | 12/20 | 7 incorrect, C07 invalid SQL |

Total: 77 correct, 20 incorrect, 2 invalid SQL, 1 not executed.

By family (official question types; a combined question counts in every family it touches; details in [five-model-summary-en.csv](../five-model-summary-en.csv)):

| Model | period | age | product | combined (C15-C19) |
|---|---|---|---|---|
| gpt-oss-120b | 9/10 | 9/10 | 6/7 | 4/5 |
| gpt-oss-20b | 10/10 | 9/10 | 7/7 | 5/5 |
| qwen3.8-27b | 6/9 + 1 not executed | 5/10 | 4/7 | 1/5 |
| north-mini-code | 8/10 | 3/10 | 5/7 | 3/5 |
| dots-3-note-preview | 7/10 | 3/10 | 6/7 | 2/5 |

Questions with a single filter of type `period` (C01, C04-C07, C20) or `product list` (C03, C12-C14): every model is correct, except E on C07 (invalid alias) and D on C20 (not executed).

## 3. Failures and their causes (observed in the traces)

### 3.1 The age convention causes almost every error

**21 of the 22 executed failures are on questions involving age.** Patterns read in the SQL (one cause per row in the comparison CSV):

- year difference only, or "half" of the rule (year difference = 25 AND birthday passed), which drops customers with a 26-year difference whose birthday has not yet come, e.g. C005 (born 2000-09-26) and C007 (born 2000-11-30) - E/C15, E/C18;
- "exactly 25" read as "25th birthday on the reference day" - A/C17, E/C09, E/C11;
- reversed or incomplete arithmetic (birth_year - 2026 = 25; reference year missing) - C/C02, C/C08, C/C09, C/C11;
- hard-coded birth years with inverted day bound, dropping C001 (born 2001-09-25, aged 25) and adding C004 (born 2000-09-25, aged 26) - D/C16, D/C17; verified: this gives exactly the observed 367050;
- wrong birth-date window: born in the year before the reference date (aged 0) - B/C02; born within the last 26 years (aged 0 to 25) - C/C19; birthday test built on 'MM-YYYY' instead of 'MM-DD' - C/C17;
- conditions that can never hold or always hold - D/C15 (MM-DD both <= and > '09-25'), D/C19 (a year compared with a full date), E/C08 (AND/OR precedence);
- approximate age in days (years x 365 + months x 31) - E/C16; age at the order date when a reference date is given - D/C09; an invented extra filter on the order date - E/C02;
- invalid SQL on an age question - C/C10 (CAST without AS).

Most missed questions: C02, C09 and C17 (3 models each), all age questions.

The only failure outside age questions: E/C07, invalid SQL (`no such column: oi.quantity_product`, undefined alias).

### 3.2 Access and network incidents (not wrong answers)

- **A/C07**: attempt 1 timeout after 45 s (no HTTP status, no value), attempt 2 correct. A network failure, then a valid retry.
- **D, C16 to C20**: HTTP 429 "Rate limit reached for model qwen/qwen3.8-27b" (Groq per-minute limit) from 13:15 UTC; 5 retries; C16, C17, C19 then answered (incorrectly), C18 correctly; **C20 received two 429 and stays `not_executed`**: the protocol allows two attempts per cell, so it is counted neither as correct nor as a model error.
- Missing measurements stay empty in the traces: no tokens on the timeout and 429 rows (their latency is recorded, 45.2 s for the timeout), `cost_native` empty on every Groq row (Groq returns no native cost).

### 3.3 Process incidents

- **Double run of model E.** Model E was run twice, on two accounts (Thibault's, scored: [traces-E.csv](../traces-E.csv); Mathias's, unscored: [traces-E-Mathias.csv](../traces-E-Mathias.csv)), and the two runs overlapped in time (13:46-13:50 UTC). This broke the one-request-at-a-time rule and used 20 OpenRouter calls beyond the budget. Both runs are kept as real raw evidence; only the operator's run is scored. They disagree on **7 of 20 questions** (C07, C08, C10, C11, C15, C16, C17) with the same model, prompt and temperature 0: temperature 0 does not make this free route reproducible.
- **D's first run used an invalid API key**; its files were not kept, so the corresponding access errors are not in the traces. D restarted as a separate experiment (`state-D-corrected.jsonl`).
- **Line endings**: Git (`core.autocrlf=true`) converted LF to CRLF inside the SQL fields of the CSV files on checkout; content unchanged, checked against the JSONL. `.gitattributes` now keeps the trace files byte for byte.
- **Summary template**: `five-model-summary-en.csv` listed `inclusionai/ling-3.0-flash-sante:free` for the third model; the model actually run, `cohere/north-mini-code:free`, was written instead.

## 4. Portfolio and routing hypothesis

From [five-model-summary-en.csv](../five-model-summary-en.csv) (sources and dates in the file):

- gpt-oss-120b: index 11.6 (kit portfolio, 2026-09-28); paid route OpenRouter $0.15 / $0.60 per million tokens.
- gpt-oss-20b: index 10 (estimate, Artificial Analysis) / 9 (kit portfolio); paid route Groq $0.10 / $0.50.
- qwen3.8-27b: index 33.7 (kit portfolio); paid route OpenRouter $0.04 / $1.35 (catalogue read 2026-10-21).
- north-mini-code and dots-3-note-preview: absent from the portfolio, only `:free` routes listed: index and price N/A.

**Hypothesis for this batch (not a ranking):** for single `period` or `product list` questions, any of the five free models was enough here; for questions involving age, only the two gpt-oss models were reliable (9/10 each), and the model with the highest public index (qwen3.8-27b, 33.7) got only 5/10 on age questions. The public index did not predict accuracy on this task.

## 5. Limitations

One pass per model, twenty questions and one database: a single error changes a rate by 5 points. Free routes with rate limits (429) and a non-reproducible model at temperature 0 (E). Public indices come from heterogeneous sources (kit portfolio vs Artificial Analysis estimate). Paid prices are those of other routes of the same model, not of the access actually used.

## 6. Contributions

Details per item in [contributions-en.csv](../contributions-en.csv).

| Member | Role | Contribution |
|---|---|---|
| Raphael DEMOUGE | A | Run of gpt-oss-120b (traces-A); comparison rows and summary row for model A; checked references C18-C20 |
| Carl-Edouard AUDUSSEAU | B | Run of gpt-oss-20b (traces-B); comparison rows and summary row for model B; checked references C01-C04 |
| Grégoire LEGROS | C | Run of north-mini-code (traces-C); checked references C08-C10 |
| Aurelien PAYEN | D | Run of qwen3.8-27b (traces-D-corrected); checked references C05-C07 |
| Thibault ALLORY | E | Run of dots-3-note-preview (traces-E, scored); checked references C11-C13 |
| Mathias COUDER | F | Repository; reference queries and independent check; checked references C14-C17; consolidation and verification of all traces; merge into traces-td1; comparison rows and summary rows for C, D, E; prompts, README, this report; second E run |

**Coding assistance, declared.** Mathias used Claude Code (Claude Opus 5.5). Files prefixed `cd_` and the documents listed in [prompts-en.md](../prompts-en.md) were written with it; its prompts are reproduced there verbatim. The sub-group reviewed the code and can explain it; references were validated against the answer key, never taken from a model.

## 7. Next steps (TD 2)

- Vote k-of-n on the saved traces, without new calls (`vote_k_sur_n` in the skeleton, `atelier-vote.py`).
- **Observed wrong consensus**: on C02, three models (gpt-oss-20b, north-mini-code, dots-3-note-preview) return the same wrong value 0 against 590320; a 3-of-5 majority would accept it. Also C09 and C11 (two models each on 0). These are the cases to discuss in TD 2.
- Routing rule: separate age questions from period/product questions; consider computing the completed age deterministically rather than leaving it to the model.
- Rotate the roles; one operator at a time if any new call is ever allocated.
