---
description: "Review a model (yours or a teammate's) before it joins the package."
agent: model-reviewer
argument-hint: "model folder, for example src/deposits"
---

Review the model in ${input:model:model folder, for example src/deposits}.

1. Start at its `run.py`. Find the files it reads in `data/input/`, `assets/`, and `settings/`, and the files it writes to `data/output/`.
2. Check how the switchboard dispatches it and if it is enabled in `settings/`.
3. Check its outputs against the data dictionary in `assets/` and against what downstream models read (search for usages of its output columns).
4. Run its tests. If `settings/recon.yaml` has a pair for this model, run the reconciliation.
5. Give the review in the standard table format. End with the three changes that matter most before integration.
