# Sub-group DIA6 - Group 4

- Pack version: `2026-10-18-students-1`
- Database: `data/boutique.sqlite`, SHA-256 `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2`
- Reports: [reports/](reports/)

| Member | TD 1 role | Model / task |
|---|---|---|
| Raphael DEMOUGE | A, operator | Groq `openai/gpt-oss-120b` |
| Carl-Edouard AUDUSSEAU | B, operator | Groq `openai/gpt-oss-20b` |
| Grégoire LEGROS | C, operator | OpenRouter `cohere/north-mini-code:free` |
| Aurelien PAYEN | D, operator | Groq `qwen/qwen3.8-27b` |
| Thibault ALLORY | E, operator | OpenRouter `dots-studio/dots-3-note-preview:free` |
| Mathias COUDER | F, checker | cross-checks references, merges traces, prepares the summaries |

Roles rotate in TD 2 and TD 3.

### Environment

Python 3.10 or later (run with 3.12.14), standard library only (`sqlite3` 3.53.4); Windows PowerShell. API keys only in environment variables, never in the repository: `GROQ_API_KEY` and `OPENROUTER_API_KEY` (see [guide-environnement-etudiant-en.md](guide-environnement-etudiant-en.md); `cd_load-env.ps1` loads them from a `cd_.env` file kept **outside** the clone). Models and parameters are read from [modeles-autorises.json](modeles-autorises.json); the five proposed models were used, none replaced.

### Replay the TD 1 work from a fresh clone (no network, no key)

```powershell
git clone https://github.com/Mocu1t/esilv-nextgenai-td-DIA6-group4
cd esilv-nextgenai-td-DIA6-group4
python check_access.py --no-network          # Python, database hash, CSV fingerprints
python cd_build_references.py --check        # 20 references: SQL on the base = independent CSV computation
python cd_check_traces.py A=traces-A.csv:state-A.jsonl B=traces-B.csv:state-B.jsonl C=traces-C.csv:state-C.jsonl D=traces-D-corrected.csv:state-D-corrected.jsonl E=traces-E.csv:state-E.jsonl E=traces-E-Mathias.csv:state-E-Mathias.jsonl
foreach ($s in "A","B","C","D-corrected","E") { python skeleton-multi-llm-en.py --rates --state "state-$s.jsonl" }
python skeleton-multi-llm-en.py --replay state-E.jsonl --state replay-E.jsonl --out replay-E.csv   # re-runs the stored SQL offline (nature = replay)
python cd_build_comparison.py traces-A.csv traces-B.csv traces-C.csv traces-D-corrected.csv traces-E.csv --extra traces-E-Mathias.csv
```

The last command rebuilds `traces-td1.csv`/`.jsonl`, `model-question-comparison-en.csv` (explanations kept) and `cd_pivot-td1.md`. Run `--rates` and `--replay` on the per-operator state files: `traces-td1.jsonl` also holds the second, unscored E run, and the skeleton would mix the two E runs.

The batch itself (network, keys, quota) was: `python skeleton-multi-llm-en.py --run --models <provider:model> --state state-X.jsonl --out traces-X.csv`, one operator at a time.

### TD 1 status (21 October 2026)

| Deliverable | File |
|---|---|
| References, equal to the answer key, with checker | [reference-td1.csv](reference-td1.csv) |
| Raw traces, every attempt | [traces-td1.csv](traces-td1.csv), [traces-td1.jsonl](traces-td1.jsonl), and the per-operator `traces-*.csv` / `state-*.jsonl` |
| Model x question comparison (100 rows) and pivot | [model-question-comparison-en.csv](model-question-comparison-en.csv), [cd_pivot-td1.md](cd_pivot-td1.md) |
| Five-model summary | [five-model-summary-en.csv](five-model-summary-en.csv) |
| Prompts as used (experiment and coding help) | [prompts-en.md](prompts-en.md) |
| Session report and contributions | [reports/td1.md](reports/td1.md), [contributions-en.csv](contributions-en.csv) |

Completed: 100/100 cells attempted, 99 with a final verdict. Open: `qwen/qwen3.8-27b` x C20 not executed (two HTTP 429, retry limit reached); no index/paid price documented for the two OpenRouter-only free models (N/A with reason). Files prefixed `cd_` were written with coding assistance (see [prompts-en.md](prompts-en.md)).

---

# Lab kit, Trustworthy generative AI, ESILV

> Final. Pack 2026-10-18-students-1. Set your machine up with [Before TD 1](../before-td1-en.html).

Kit of 14 October 2026 for the three sessions of 21 October, 18 November and
11 December. The database and the twenty questions are the same for every
sub-group. Read the environment guide first. Preparation was due by 18 October; the environment is checked when TD 1 opens at 13:30. Each assignment gives the schedule of its afternoon.

## Before the first session

| File | Role |
|---|---|
| [guide-environnement-etudiant-en](guide-environnement-etudiant-en.html) | Install Python, create the two free accounts and the keys, then run `check_access.py`. |
| `check_access.py` | Checks your Python version, the hash of the database and the access to every authorised model; one OK or KO per line. |
| `modeles-autorises.json` | The authorised models: exact identifiers, call parameters and batch limits, read by `check_access.py` and by the skeleton. |
| `.gitignore` | Keeps environment files, keys, virtual environments and caches out of your public repository. Keep it at the root of the repository. |

## The three assignments

| File | Role |
|---|---|
| [enonce-td1-en](enonce-td1-en.html) | TD 1: compare the authorised models on the same twenty questions. |
| [enonce-td2-en](enonce-td2-en.html) | TD 2: the k-of-n vote, then the routing rule of your sub-group. |
| [enonce-td3-en](enonce-td3-en.html) | TD 3: quantify each configuration, choose one for a named use case, present it. |
| [consigne-etudiante-en](consigne-etudiante-en.html) | The protocol: task, schema, conventions, accounts, call rules, models, calls planned, offline fallback, hand-in, the twenty questions. |

## The case

| File | Role |
|---|---|
| `data/boutique.sqlite` | The database, identical for every sub-group. Never modify it. |
| `data/product.csv`, `data/customers.csv`, `data/orders.csv` | The same data as CSV files, for a spreadsheet or a check by hand. |
| `data/manifest.json` | SHA-256 hashes of the database and of the CSV files, row counts, integrity checks. |
| `schema.sql` | The three tables, sent to the models in the prompt. |
| [questions-td1-en](questions-td1-en.html) | The twenty questions, without answers. |
| `questions-td1.json` | The same questions, read by the skeleton. |
| `reference-td1.csv` | Template of step 1 of TD 1: your reference query and its value for each question. |

## The code

| File | Role |
|---|---|
| `skeleton-multi-llm-en.py` | The orchestrator skeleton: prompt, clients, sandboxed execution, verdict, trace table, rates. The k-of-n vote is yours to write in TD 2. |
| `sandbox_sqlite.py` | Read-only SQLite sandbox, used by the skeleton for every query a model returns. |
| `atelier-vote.py` | Runs your vote on four synthetic examples, then on the stored traces of one question. No network. |
| `atelier-routage.py` | Reads the decisions of a routing rule on seven scenarios with synthetic resources, then you adapt it to your own rule. No network. |

## Reading a portfolio and a cost

| File | Role |
|---|---|
| [portefeuille-modeles-en](portefeuille-modeles-en.html) | Sixty model and access pairs in five capability groups, with public index, prices and access routes. |
| `portefeuille-modeles-2026-09-28.csv` | The same table as a CSV file, for a spreadsheet. |
| [methode-cout-en](methode-cout-en.html) | The step-by-step method: read the tokens of a trace, choose a dated price, compute one call, one configuration, then an annual bill. |

## TD 1 summaries

| File | Role |
|---|---|
| `model-question-comparison-en.csv` | One final result per model/question, verdict, explanation and raw-trace pointer; display its pivot matrix. |
| `five-model-summary-en.csv` | Five models, documented index and prices, access and results by family. |
| [comparison-example-en](comparison-example-en.html) | Column definitions and a fictional presentation example, unrelated to lab answers. |

## Inventory

| File | Role |
|---|---|
| `manifest.json` | SHA-256 hash of every file of this kit. |

## Start

```bash
cd kit-td1
python3 check_access.py                       # Python, database hash, one probe per authorised model
python3 skeleton-multi-llm-en.py --demo       # the whole chain on three simulated models, no key, no network
python3 atelier-routage.py                    # the seven routing scenarios, no network
```

Then step 1 of [enonce-td1-en](enonce-td1-en.html): fill in `reference-td1.csv`. Step 2 uses the allocation and `--models` / `--cases` commands in the assignment. The base batch is 100 cells (60 Groq, 40 OpenRouter); controls and retries are separate, with at most one retry per cell. Each operator checks their own allowance. Keep the CSV and JSONL attempts.

The assessment sheet, the hand-in page and the hand-in templates are one folder above this runnable kit. [Before TD 1](../before-td1-en.html) gives the preparation steps to follow before the first session.
