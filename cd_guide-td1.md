# TD 1 — Guide pas à pas du sous-groupe

> Mercredi 21 octobre, 13:30–18:00. Rendu Moodle : **dimanche 25 octobre, 23:59 (Paris)**.
> Sources : [enonce-td1-en.md](enonce-td1-en.md), [consigne-etudiante-en.md](consigne-etudiante-en.md).
> Les fichiers préfixés `cd_` ont été écrits avec une assistance de code (Claude Code) : à relire, comprendre et déclarer dans le rapport.

## Les fichiers à connaître

| Fichier | Rôle |
|---|---|
| [cd_build_references.py](cd_build_references.py) | Étape 1 : calcule les 20 références en SQL **et** en Python sur les CSV, écrit `reference-td1.csv` seulement si les deux concordent |
| [reference-td1.csv](reference-td1.csv) | Les 20 requêtes et valeurs (déjà rempli, 20/20 concordants) |
| [skeleton-multi-llm-en.py](skeleton-multi-llm-en.py) | Étape 2 : appelle les modèles, exécute le SQL en bac à sable, trace |
| [cd_build_comparison.py](cd_build_comparison.py) | Étape 3 : fusionne les traces, produit le CSV de comparaison, le pivot et les décomptes par famille |
| `cd_pivot-td1.md` | Créé par le script ci-dessus : matrice modèles × questions pour la plénière |

Toutes les commandes se lancent depuis `kit-td1`, en PowerShell, avec le Python du venv (`python3` pointe sur le Microsoft Store sous Windows) :

```powershell
cd kit-td1
$py = "..\.venv\Scripts\python.exe"
```

---

## 0. Ouverture (13:30 – 13:45)

- [ ] Chacun a sa sortie `check_access.py` sauvegardée (5/5 OK). **Ne pas relancer le contrôle réseau** : il coûte 3 appels Groq + 2 OpenRouter. Pour l'intégrité locale uniquement : `& $py check_access.py --no-network`.
- [ ] Chaque opérateur note dans les notes de run le **quota restant** de son compte (console Groq / tableau de bord OpenRouter) et les contrôles déjà consommés. Il faut 20 cellules + une marge cible de 5.
- [ ] Attribuer les rôles :

| Membre | Rôle | Modèle (identifiant exact) | Compte |
|---|---|---|---|
| A | opérateur | `groq:openai/gpt-oss-120b` | Groq perso de A |
| B | opérateur | `groq:openai/gpt-oss-20b` | Groq perso de B |
| C | opérateur | `openrouter:cohere/north-mini-code:free` | OpenRouter perso de C |
| D | opérateur | `groq:qwen/qwen3.8-27b` | Groq perso de D |
| E | opérateur | `openrouter:dots-studio/dots-3-note-preview:free` | OpenRouter perso de E (≠ C) |
| F, G, H | vérificateurs | — | contre-vérifient les références, fusionnent les traces, préparent les synthèses |

- [ ] Répartir les 20 questions de référence : 2 ou 3 par membre, chacun avec un binôme qui contre-vérifie.
- [ ] **Signaler à l'encadrant** : [five-model-summary-en.csv](five-model-summary-en.csv) indique `inclusionai/ling-3.0-flash-sante:free` en ligne 3, alors que le modèle C prévu est `cohere/north-mini-code:free`. Demander quelle version fait foi.

---

## 1. Les références (13:45 – 15:00)

Les valeurs sont déjà calculées. Le travail de cette étape consiste à **les comprendre, les contre-vérifier et savoir les expliquer** (c'est nécessaire pour le niveau 2 de R1).

1. Relancer la vérification (elle n'écrit rien) :
   ```powershell
   & $py cd_build_references.py --check
   ```
   On attend 20 lignes `[OK ]`.
2. Chaque membre ouvre ses 2 ou 3 requêtes dans [reference-td1.csv](reference-td1.csv) et sait expliquer chaque filtre. Le binôme les contre-vérifie par une autre méthode, par exemple en recomptant à la main les lignes concernées avec `sqlite3 data/boutique.sqlite`.
3. Montrer les 20 valeurs à l'encadrant. Il indique les questions dont la valeur diffère du corrigé, sans donner la valeur. Corriger **avant** de lancer ces questions.

| | | | | |
|---|---|---|---|---|
| C01 792800 | C02 590320 | C03 936350 | C04 2826250 | C05 38480 |
| C06 0 | C07 13970 | C08 605580 | C09 487980 | C10 558980 |
| C11 446690 | C12 1666490 | C13 107740 | C14 0 | C15 168680 |
| C16 376740 | C17 258180 | C18 62480 | C19 1990 | C20 1106090 |

### Les quatre conventions à savoir expliquer

- **Période** : intervalle fermé à gauche, ouvert à droite, `o.date >= 'S' AND o.date < 'E'`. Certaines commandes tombent pile à minuit (`2026-03-01 00:00:00`, `2026-05-15 00:00:00`, `2026-06-01 00:00:00`). Une borne `<=` ou un `BETWEEN` change donc le résultat de C01, C05, C07 et C20.
- **Âge révolu** : `année(D) − année(naissance) − (MM-JJ(D) < MM-JJ(naissance))`. Les clients C001, C002 et C003 sont nés les 25, 24 et 26/09/2001, d'où les valeurs différentes de C02 (25/09), C08 (24/09) et C09 (26/09). Pour C11 (01/12), C006 (né le 30/11/2001) a 25 ans, mais pas C014 (né le 08/12/2001). Un modèle qui fait seulement « 2026 − 2001 » se trompe.
- **Âge au moment de la commande** (C10, C18) : l'âge se calcule à `substr(o.date, 1, 10)` pour chaque ligne. Un même client peut donc compter pour certaines lignes et pas pour d'autres.
- **Montant** : `SUM(quantity_product * price)` en centimes HT, avec `COALESCE(..., 0)`. C06 (aucune commande en 2025) et C14 (aucune commande après le 20/09/2026) doivent renvoyer `0` et non `NULL`.

### Vérification indépendante

Le script calcule chaque valeur deux fois :
- en **SQL**, sur la base ouverte en lecture seule ;
- en **Python pur**, sur les CSV, avec une autre méthode d'âge : on teste si `25e anniversaire ≤ D < 26e anniversaire`, avec `date.replace(year=...)`.

Aucune valeur ne vient d'un LLM.

⚠️ **Ne plus modifier `reference-td1.csv` une fois les appels lancés.** Le squelette refuse de reprendre une expérience dont la référence a changé ; il faudrait alors de nouveaux fichiers `--state` et `--out`.

**Livrable** : `reference-td1.csv`, égal au corrigé.

---

## 2. Les cinq modèles (15:00 – 15:35)

**Règle d'or** : un seul opérateur lance des appels à la fois, puis il passe la main. Le squelette applique déjà les règles du lot : 3 s entre deux requêtes, temperature 0, sortie plafonnée, timeout de 45 s, au plus une reprise par cellule.

1. Chaque opérateur définit **sa** clé dans **sa** session PowerShell, sans jamais l'écrire dans un fichier :
   ```powershell
   $env:GROQ_API_KEY = "gsk_..."            # A, B, D
   $env:OPENROUTER_API_KEY = "sk-or-v1-..." # C, E
   ```
2. Faire d'abord un test sur 2 questions, puis lancer le reste avec **les mêmes** fichiers `--state` et `--out` (les cellules déjà vérifiées sont sautées) :
   ```powershell
   # A
   & $py skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --cases C01,C03 --state state-A.jsonl --out traces-A.csv
   & $py skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --state state-A.jsonl --out traces-A.csv
   ```
   Les autres opérateurs font de même avec leur modèle et leur lettre :

   | Membre | `--models` | Fichiers |
   |---|---|---|
   | B | `groq:openai/gpt-oss-20b` | `state-B.jsonl` / `traces-B.csv` |
   | C | `openrouter:cohere/north-mini-code:free` | `state-C.jsonl` / `traces-C.csv` |
   | D | `groq:qwen/qwen3.8-27b` | `state-D.jsonl` / `traces-D.csv` |
   | E | `openrouter:dots-studio/dots-3-note-preview:free` | `state-E.jsonl` / `traces-E.csv` |

3. Dans les notes de run, chaque opérateur sépare trois compteurs : **appels initiaux**, **contrôles d'accès** et **reprises**. Il relève aussi son quota après le lot.
4. En cas de problème :
   - **Un modèle ne répond plus** : le remplacer par un autre modèle gratuit (Groq Free, ou OpenRouter `:free`). Noter l'identifiant exact, les paramètres et la date dans `modeles-autorises.json` et dans le rapport.
   - **Le quota est épuisé** : redistribuer les questions restantes à un membre qui a encore de la capacité, ou demander à l'encadrant le lot de secours identifié. Une nouvelle clé n'ajoute pas de capacité.
   - **Le réseau tombe** : l'encadrant fournit `traces-reelles.jsonl`, et on lance `& $py skeleton-multi-llm-en.py --replay traces-reelles.jsonl`. Les lignes obtenues ont `nature = replay` et ne doivent jamais être mélangées avec les lignes réelles.
5. Garder **tous** les fichiers `state-*.jsonl` et `traces-*.csv`, sans jamais les supprimer.

---

## 3. Lire les traces et faire les synthèses (15:35 – 16:00, puis 16:15 – 17:00)

1. Un vérificateur (F, G ou H) fusionne les traces :
   ```powershell
   & $py cd_build_comparison.py traces-A.csv traces-B.csv traces-C.csv traces-D.csv traces-E.csv
   ```
   Le script produit :
   - `traces-td1.csv` : toutes les tentatives, sous un seul en-tête ;
   - `model-question-comparison-en.csv` : 100 lignes, avec la dernière tentative de chaque cellule et `not_executed` pour une cellule jamais lancée ;
   - `cd_pivot-td1.md` : la matrice à projeter en plénière ;
   - dans le terminal, les décomptes par famille.

   S'il affiche `WARNING ... different prompt fingerprints`, le prompt a été modifié en cours de route : il faut trouver pourquoi.
2. **Compléter chaque `TODO` de la colonne `explanation`** avec une cause tirée de la trace (colonnes `sql`, `error`, `http_status`, `verdict_detail`), et non une impression. Quatre causes sont à distinguer :

   | Cause | Où la voir dans la trace |
   |---|---|
   | Convention cassée | `incorrect` : le SQL utilise `<=` ou `BETWEEN`, calcule l'âge par la seule différence d'années, oublie `COALESCE`, oublie une jointure ou un filtre produit… |
   | SQL invalide ou rejeté | `sql_invalid` ou `sql_rejected` : texte au lieu de SQL, plusieurs requêtes, table inconnue |
   | Sortie tronquée | réponse coupée, `tokens_completion` proche du plafond (1024) |
   | Accès refusé | `access_error`, HTTP 400 à 404 ou 429 : ce n'est **pas** une mauvaise réponse |

3. Remplir [five-model-summary-en.csv](five-model-summary-en.csv), une ligne par modèle :
   - **index public** (avec source et date), **prix entrée/sortie** d'une route payante du *même* modèle (avec source et date), **accès utilisé**, à reprendre de [portefeuille-modeles-en.md](portefeuille-modeles-en.md) ou de son CSV ; mettre `N/A` avec la raison s'il n'existe pas de route payante documentée ;
   - `period_results`, `age_results`, `product_results`, `combined_results` : recopier les décomptes « correct/évalués » du terminal. Indiquer à part les accès en échec et les cellules non faites, et préciser qu'une question combinée compte dans plusieurs familles ;
   - `trace_files` et `limits` : par exemple « 20 questions, un seul tirage, temperature 0 : hypothèse de routage, pas un classement ».
4. Préparer l'explication d'**une trace au choix de l'encadrant** : son empreinte de prompt (`prompt_sha256`, identique pour tous les modèles sur une même question), une mesure manquante (colonne vide = non mesurée) et une reprise s'il y en a eu une.

---

## 4. Plénière (17:00 – 17:30)

- Projeter `cd_pivot-td1.md`.
- Repérer les questions que la plupart des modèles ratent, ainsi que la convention en cause : elles reviennent au TD 2.
- Expliquer chaque écart avec les autres sous-groupes par les traces. Il peut venir des références, des paramètres d'appel, des accès ou de la variabilité des modèles.

## 5. Notation et préparation du TD 2 (17:30 – 18:00)

- [ ] L'encadrant note R1, R2 et R3 à la table.
- [ ] Désigner qui lit `atelier-vote.py` et la règle de routage attendue pour le TD 2.
- [ ] 17:45 : quiz individuel sur Moodle.

---

## 6. Rendu (avant le dimanche 25/10, 23:59)

Dépôt Git **public** du sous-groupe, le même pour les TD 1 à 3.

- [ ] Copier `kit-td1/.gitignore` à la racine du dépôt si la racine n'est pas `kit-td1`. Vérifier qu'**aucune clé** n'est commitée.
- [ ] Committer :
  - `reference-td1.csv`, `traces-td1.csv`, tous les `traces-*.csv` et `state-*.jsonl` ;
  - `model-question-comparison-en.csv`, `five-model-summary-en.csv` ;
  - le code, y compris les `cd_*.py` et les prompts (`SYSTEM_PROMPT` et `USER_PROMPT_TEMPLATE` du squelette, inchangés et identiques pour tous les modèles).
- [ ] Écrire `reports/td1.md` avec :
  - le travail tenté et terminé ;
  - les réussites et les échecs, avec des liens vers les CSV et les traces ;
  - les causes observées et les hypothèses ;
  - les limites ;
  - **la contribution de chaque membre** ;
  - l'**assistance de code déclarée** (fichiers `cd_*`) ;
  - tout modèle remplacé (identifiant et date) ;
  - les exemples rejoués ou simulés, identifiés comme tels ;
  - la suite pour le TD 2.
- [ ] Ouvrir le dépôt dans une fenêtre privée pour vérifier qu'il est lisible sans connexion.
- [ ] Sur Moodle : l'URL complète du dépôt, le **hash complet du commit** (`git rev-parse HEAD`) et le lien vers `reports/td1.md` à ce commit.

## Ce qui est valorisé (à garder en tête)

1. Une référence égale au corrigé, obtenue avec les conventions du protocole.
2. Des traces qui renvoient à des appels réels, une ligne par appel, sans mélanger réel, rejeu et simulation.
3. Une cause par échec, lue dans la trace.
4. Une fiche portefeuille qui prépare la décision : quel modèle suffit pour quelle famille de questions, et à quel prix.
