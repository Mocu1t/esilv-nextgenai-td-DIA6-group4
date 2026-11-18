# Prompts, as used - TD 2

Sub-group DIA6 - Group 4, TD 2 (18 November 2026).

**Experiment prompt**: unchanged. TD 2 makes no new model call; the vote and the routing rule work on the stored TD 1 traces, whose fingerprints are listed in section 1 of [../td1/prompts-en.md](../td1/prompts-en.md).

**Coding-assistance prompts.** Assistant: Claude Code (model Claude Opus 5.5), in VS Code, session of Mathias COUDER (Pair C) on 18 November 2026; prompts reproduced verbatim, in French as typed, numbering continued from TD 1 ([../td1/prompts-en.md](../td1/prompts-en.md), section 2).

- **Routing (Pair C), prompts 19 to 25.** Written or modified with the assistant: `C-routing/cd_family_rates.py`, `C-routing/atelier-routage.py` (adapted `RESOURCES` and `choose`), `C-routing/routing-rule.md`, `C-routing/simulator-analysis.md` and the simulator outputs `simulator-before.jsonl` / `simulator-after.jsonl`. The routing choices (tie-break on the price of the paid route of the same model; deterministic check on F2 even for the internal dashboard) were proposed by the assistant with their justification, then discussed and decided by the pair (prompts 21 and 22).
- **Cross-review and assembly, prompts 26 and 27.** With the assistant: the one-line indentation fix in `td1/skeleton-multi-llm-en.py` (logic of Pair A unchanged); `A-quorum/cd_vote_table.py` and `vote-2of3-vs-3of5.csv`; `B-consensus/cd_shared_wrong_values.py` and `shared-wrong-values.md`; the three paths of Pair B's notebook; the repository layout (`git mv`, paths updated); the README files, the reviews by Pair C (`A-quorum/review-1.md`, `B-consensus/review-1.md`) and the checklists of the other reviews; `reports/td2.md`.
- **Pairs A and B:** add here any AI prompt you used, verbatim.

**19.**

```text
Faisons ensemble le TD2. J'ai mis les consignes actualisées dans le pdf : "TD 2 - The quorum, then the routing rule" guide moi pas à pas
```

**20.**

```text
[answer to the assistant's question "Which pair are you in for TD 2?": Pair C (routing)]
```

**21.**

```text
what do you think is the best for both ? and how to justify it ?
```

**22.**

```text
parfait, alors alons y comme ca. réponds en francais dans cette conversation
```

**23.**

```text
peux tu exécuter ces commandes git ?
```

**24.**

```text
ajoute les prompts de cette séance dans prompts-en.md
```

**25.**

```text
oui, committe et push
```

**26.**

```text
j'ai pull le travail des autres, finalise le travail et les livrables pour ce td. J'ai ajouté une image "structure.png" qui montre la structure que devrait respecter le dossier. 
Adapte pour que tout soit près.
Puis résumes les points clés à retenir
```

**27.**

```text
[answers to the assistant's questions on the pair members and on pushing: Pair A = Aurelien PAYEN + Thibault ALLORY; Pair B = Raphael DEMOUGE + Grégoire LEGROS; Pair C = Mathias COUDER + Carl-Edouard AUDUSSEAU; "Oui, commit + push"]
```
