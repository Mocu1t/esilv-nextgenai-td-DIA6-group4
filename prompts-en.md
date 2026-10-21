# Prompts, as used

Sub-group DIA6 - Group 4, TD 1 (21 October 2026), pack `2026-10-18-students-1`.

## 1. Experiment prompt (identical for the five models)

Taken verbatim from `skeleton-multi-llm-en.py` (`SYSTEM_PROMPT`, `USER_PROMPT_TEMPLATE`, `build_prompt`), **unchanged from the kit**. No variant was used: every trace line of a question carries the same `prompt_sha256` (table below).

### System message

```text
You write SQLite queries for a small e-commerce database. Reply with exactly one SQLite SELECT statement and nothing else: no explanation, no comments, no markdown other than an optional ```sql fence.
```

### User template

`{schema}` is replaced by the content of `schema.sql` (stripped), `{question}` by the question text of `questions-td1.json`.

```text
Schema (SQLite):
{schema}

Conventions (binding):
- product.price is the unit price in euro cents, excluding VAT (an integer). Revenue excluding VAT is SUM(quantity_product * price), an integer number of cents.
- orders holds order lines: one row per (order_id, product_id). All lines of an order share the same customer_id and the same date.
- orders.date and customers.insert_date are UTC timestamps stored as text 'YYYY-MM-DD HH:MM:SS'. customers.birth_date is a date stored as text 'YYYY-MM-DD'. Compare them as text or with SQLite date functions.
- A period "from S to E" is closed on the left and open on the right: date >= S AND date < E.
- A customer's age on a day D is the number of completed years: someone born on B is N years old on D when the N-th anniversary of B is on or before D and the (N+1)-th anniversary is after D. "Exactly 25 years old" means completed age 25 on that day, computed from month and day, never from the year difference alone.
- Unless the question says "at the time of the order", ages are computed on the reference date given in the question.
- The query must return exactly one row and one column named revenue_cents. When no order line matches, return 0 (use COALESCE), not NULL.
- Use only the tables above. One SELECT statement, nothing else.

Question: {question}
```

### `schema.sql` inserted in `{schema}`

```sql
-- Prototype orchestrator, ESILV "Next-Generation AI" (task 1572).
-- Three tables, exactly as specified. Prices are euro cents excluding VAT.
-- orders.date and customers.insert_date: UTC timestamps 'YYYY-MM-DD HH:MM:SS'.
-- customers.birth_date: date 'YYYY-MM-DD'.
CREATE TABLE product (
    product_id TEXT PRIMARY KEY,
    price INTEGER NOT NULL CHECK (price >= 0)
);
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    insert_date TEXT NOT NULL,
    birth_date TEXT NOT NULL
);
CREATE TABLE orders (
    date TEXT NOT NULL,
    order_id TEXT NOT NULL,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    product_id TEXT NOT NULL REFERENCES product(product_id),
    quantity_product INTEGER NOT NULL CHECK (quantity_product > 0),
    PRIMARY KEY (order_id, product_id)
);
```

### Fingerprint per question

`prompt_sha256` = SHA-256 of `system + "
" + user`, recomputed from the unchanged skeleton and compared with every row of `traces-td1.csv` (all models, both E runs, all attempts).

| Question | prompt_sha256 | Same in every trace row |
|---|---|---|
| C01 | `d25f63730bdd4980e31c3e5a449f59f3410bcee3a2cfc132d8f38efab03b1bdd` | yes |
| C02 | `42b91ea47ed6f10aa79e4579ad12fb7a5191e12b1a3fb82b79d253b9d9ae8a62` | yes |
| C03 | `5d8e7c01aa0646ca4a352456f4abb4665fc48e546a82767d6827a905d70d21be` | yes |
| C04 | `c2a73db35adea5cd8622a7c03a9ba03687f12bfcd2e4b40893c93685f34016f4` | yes |
| C05 | `b96a003b2b5ae4511254b974c61e08af86ceed7421a162c48b1590f9e646b70c` | yes |
| C06 | `e10af71902d58af793255a62dee11db30da6f4df4588be141bb0a82b03923258` | yes |
| C07 | `7fef6bd6a1dac0bfc655deb9e35dc04f960b8b8a276b49f6a727a88e1c67c2aa` | yes |
| C08 | `d875514cab7aae73cb92d4378c96e2e5291e14746c05baf6fa28d1449c19e99c` | yes |
| C09 | `8a183ea0b704135aacad9681a454de5f091062bf148a3b9e43cbdec6c7cc8c19` | yes |
| C10 | `bf06c7f2b73ebaad7deca36db05e5d26b7de0e2e97fbf7f829b3471f2b256aca` | yes |
| C11 | `2f368d80930bd7ca3aef95d2966b5d542f1703819851b2503f1837b628fafd88` | yes |
| C12 | `428f3d31cb2a9021446721741fd70f330bb83ca218791305e04bf6732a36bc74` | yes |
| C13 | `8df2423fb78cd6ef6bf4157943bec37c0f05ff124ae276122f3e53ac78f6a88a` | yes |
| C14 | `a0715dbffe3d8f9c9245ace5031860493ab079cd524a1403b9a1a5cce391e167` | yes |
| C15 | `524c019f96e7672f941e11be69dc0f2575dfc5c95719259d6d6f013cada492ad` | yes |
| C16 | `ebc89bbcb01e5890298132161b6ed675899a8d158b7a56619aa3636504d6bca7` | yes |
| C17 | `a99fd1bb3b8d470a035c26906d2c14623694590b52ad8bd3d7d392ca305f4d75` | yes |
| C18 | `2df965d9a03714e645bf78bd50249f8585da3f3d832d14605e72c7777836b985` | yes |
| C19 | `e5396619f946e273f11d2baf48666f84d8a817fde9f7189579c96ce2c2a14119` | yes |
| C20 | `3ff11fcc9b7dce0bdf408c10ec54d9f7d7944f363aa6f85a9c6d4d6df145a0ef` | yes |

Call parameters (from `modeles-autorises.json`): temperature 0; output cap 1024 tokens (1000 for `qwen/qwen3.8-27b`); `reasoning_effort` low (gpt-oss) or none (qwen) on Groq; `reasoning.enabled=false` and `provider.max_price=0` on OpenRouter; 45 s timeout; at most one retry per cell.

## 2. Coding-assistance prompts

Assistant: Claude Code (model Claude Opus 5.5), in VS Code, session of Mathias COUDER on 21 October 2026. Prompts reproduced verbatim, in French as typed; pasted material is summarised in brackets. Files written or modified by the assistant carry the `cd_` prefix (`cd_build_references.py`, `cd_build_comparison.py`, `cd_check_traces.py`, `cd_load-env.ps1`, `cd_guide-td1.md`, `cd_pivot-td1.md`), except names imposed by the assignment or by Git: `prompts-en.md`, `reports/td1.md`, `contributions-en.csv`, the group section of `README.md`, `.gitattributes`, the `checked_by` column of `reference-td1.csv`, and the rows of `model-question-comparison-en.csv` and `five-model-summary-en.csv` described in `reports/td1.md`. No reference value was taken from a model: the assistant wrote the SQL and an independent CSV computation, and both were checked against the instructor's answer key.

Other members: add here any AI prompt you used for your part, verbatim.

**1.**

```text
en te basant sur enonce-td1-en.md et consigne-etudiante-en.md, aide moi à préparer le td1.
```

**2.**

```text
propose moi un fichier md qui me guide moi et mon groupe pas à pas dans le td1, grace à ce que tu as préparé. Aussi pour tous les fichiers que tu as toi même créé ou que tu vas créer, ajoute cd_ comme prefix devant le nom du fichier pour que je me repère facilement
```

**3.**

```text
où sont les consignes pour la création du github ?
```

**4.**

```text
guide moi pour la création du repository
```

**5.**

```text
Etape 2 : To https://github.com/Mocu1t/esilv-nextgenai-td-DIA6-group4
 ! [remote rejected] main -> main (push declined due to email privacy restrictions)
error: failed to push some refs to 'https://github.com/Mocu1t/esilv-nextgenai-td-DIA6-group4'
```

**6.**

```text
[pasted output of `git commit --amend --reset-author`: 47 files changed]
c'est bon ?
```

**7.**

```text
peux tu me créer un .env pour ne pas reperdre mes clés api ?
```

**8.**

```text
OK. Je suis en TD. Peux tu me guider ?
```

**9.**

```text
[pasted rows C14 to C17 of reference-td1.csv]
Peux tu m'expliquer ces 4 requetes
```

**10.**

```text
"Noter qui a vérifié quoi. C'est exigé par submission-en.md. Ajoutez une colonne checked_by à la fin de reference-td1.csv. Le squelette ne lit que case_id et revenue_cents : la colonne en plus ne gêne pas."
ajoute la colonne, je la complète avec les noms
```

**11.**

```text
Voici les valeurs de references du prof :
[pasted table of the twenty instructor values, C01 to C20]
Peux tu vérifier que c'est bien les mêmes que les notres ?
```

**12.**

```text
en haut du readme ajoute une partie pour noter les 6 membres de mon groupe
```

**13.**

```text
faisons l'étape 2 pour le modèle E
```

**14.**

```text
traces-D original a été fait avec une key api non valide, donc ce n'est meme pas vraiment une vraie tentative.
Peux tu vérifier le contenu de chaque traces et chaque state, et vérifier que ce qu'ils contiennent est bien ce qui est attendu
```

**15.**

```text
j'ai pull les modifs des autres membres, peux tu check a nouveau ?
```

**16.**

```text
ok, j'ai remis les 2 fichiers issus de notre travail sur le modele E. Peux tu résoudre les 3 pbs de ton côté ? le modèle utilisé fait foi, et tu peux fusionner les explications
```

**17.**

```text
j'ai push. Que nous reste t il a faire pour finir le td1 ? y a t il des livrables a faire encore
```

**18.**

```text
Oui, finissons les différents livrables. Pour les contributions, c'est ce que j'avais noté dans references-td1 : chaque autre membre s'est occupé d'un modèle, et je me suis occupé de la mise en commun et de la fusion des différents travaux
```
