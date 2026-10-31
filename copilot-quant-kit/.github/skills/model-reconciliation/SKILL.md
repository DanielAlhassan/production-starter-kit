---
name: model-reconciliation
description: "Compare new model outputs with baseline outputs value by value, with tolerances. Use after any change to model calculation code, after a refactor, when consolidating modules, when the user asks if numbers changed, or before a model change goes to review."
---

# Model reconciliation

The goal: prove that a code change did not move the numbers, or show exactly which numbers moved and by how much.

## Files

- `scripts/compare_outputs.py`: the comparison. Do not write a new one.
- `recon_config_template.csv`: config template. One row per output file pair.
- In the repo: `recon/recon_config.xlsx` (or `.csv`), `recon/baseline/` (approved outputs), `recon/results/` (reports).

## Steps

1. If `recon/recon_config.xlsx` does not exist, show the user `recon_config_template.csv` and propose one row per output. The user sets the keys and tolerances and saves the file as `recon/recon_config.xlsx`. Do not guess tolerances. The stop hook runs this file automatically after each agent turn that edits Python.
2. If `recon/baseline/` is empty, tell the user. The baseline must come from the approved version of the model (for example the last commit on main or the legacy Excel output). A person copies it in. You do not create or change baselines.
3. Run the model to make new outputs in the candidate folder.
4. Run:
   ```
   python .github/skills/model-reconciliation/scripts/compare_outputs.py recon/recon_config.xlsx
   ```
5. Report to the user, for each output: PASS or FAIL, rows only on one side, duplicate keys, dropped columns, number of breaches, and the largest difference.
6. If an output fails:
   - Find the cause in the code change. Explain it in one or two sentences.
   - If the change in numbers is intended (for example a methodology fix), say so and show the size of the change. The user decides if the baseline changes.
   - Do not change tolerances, keys, or the baseline to get a PASS.

## Tolerance guide

A value breaches only when it exceeds both `abs_tol` and `rel_tol`.

| Output type | abs_tol | rel_tol |
|---|---|---|
| Pure refactor, same library versions | 1e-9 | 1e-12 |
| Refactor with a change in operation order | 1e-6 | 1e-9 |
| Excel to Python migration | 1e-4 | 1e-6 |
| Dollar outputs reported in millions | 0.001 | 1e-6 |
