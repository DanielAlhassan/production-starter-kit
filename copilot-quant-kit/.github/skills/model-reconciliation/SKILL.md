---
name: model-reconciliation
description: "Compare new model outputs with approved baseline outputs value by value, with tolerances. Use after any change to model code in src/ or assembly/, after a refactor, when consolidating models, when the user asks if numbers changed, or before a change goes to review."
---

# Model reconciliation

The goal: prove that a code change did not move the numbers, or show exactly which numbers moved and by how much.

## Files

- `scripts/compare_outputs.py`: the comparison. Do not write a new one.
- `recon_template.yaml`: template for `settings/recon.yaml`.
- In the repo:
  - `settings/recon.yaml`: output pairs, keys, tolerances, results folder.
  - `data/output/baseline/`: approved outputs. A person puts them there.
  - `data/output/`: new outputs from the current run.
  - `data/output/recon/`: comparison reports.

## Steps

1. If `settings/recon.yaml` does not exist, show the user `recon_template.yaml` and propose one entry per output. The user sets the keys and tolerances. Do not guess tolerances.
2. If `data/output/baseline/` is empty, tell the user. The baseline comes from the approved version of the model (the last approved commit or the legacy Excel output). You do not create or change baselines. Hooks block this.
3. Run the model so `data/output/` has new outputs:
   - Package: `python -m assembly.driver`
   - Single model: call `run()` from `src/run.py` the way the repo does it.
4. Run:
   ```
   python .github/skills/model-reconciliation/scripts/compare_outputs.py settings/recon.yaml
   ```
5. Report for each output: PASS or FAIL, rows only on one side, duplicate keys, dropped columns, number of breaches, and the largest difference.
6. If an output fails:
   - Find the cause in the code change. Explain it in one or two sentences.
   - If the change in numbers is intended (for example a methodology fix), say so and show its size. The user decides if the baseline changes.
   - Do not change tolerances, keys, or the baseline to get a PASS.

The stop hook runs the driver and this comparison after each agent turn that edits Python, when `assembly/driver.py` and `settings/recon.yaml` exist.

## Tolerance guide

A value breaches only when it exceeds both `abs_tol` and `rel_tol`.

| Change type | abs_tol | rel_tol |
|---|---|---|
| Pure refactor, same library versions | 1e-9 | 1e-12 |
| Refactor with a change in operation order | 1e-6 | 1e-9 |
| Excel to Python migration | 1e-4 | 1e-6 |
| Dollar outputs reported in millions | 0.001 | 1e-6 |
