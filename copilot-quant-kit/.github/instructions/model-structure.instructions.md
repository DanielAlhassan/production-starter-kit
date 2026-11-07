---
applyTo: "**/*.py,**/*.yaml,**/*.yml"
description: "Model repo layout: data, assets, settings, src with run.py, assembly with driver and switchboard."
---

# Model structure

Use this layout. Do not invent a new layout or add top-level folders without asking.

```
data/
  input/            Source data for a run. Read only.
  output/           Model outputs. Written only by the model run.
    baseline/       Approved outputs for reconciliation. Changed only by a person.
    recon/          Reconciliation results.
assets/             Stable files that are part of the methodology (spreadsheets, mappings, curves, data dictionary). Read only.
settings/           YAML files: run settings, paths, toggles, enabled models, tolerances.
src/                Model code.
  run.py            One callable: run(). The only entry point of the model.
  <step>.py         One file per step of the model. run() calls them in order.
tests/              Tests for the step files and controls.
assembly/           Only when the repo is a package of several models.
  driver.py         Entry point of the package. Reads settings, calls the switchboard, writes the run record.
  switchboard.py    Reads the enabled models from settings and dispatches each one to its run().
```

In a package, each model has its own folder: `src/<model>/run.py` with its own `run()`. The switchboard is the only place that knows the list of models.

## Assets vs settings

- **assets/**: things that are part of the methodology and do not change between runs. A change to an asset is a methodology change.
- **settings/**: things that control a run and can change between runs: dates, scenarios, paths, which models are enabled, tolerances.
- If you are not sure where a value goes, ask. Never put the value in code.

## Rules

1. No numbers, paths, or mappings in code. They come from `settings/` or `assets/`.
2. `run()` reads settings, calls the steps in order, and writes outputs to `data/output/`. Step files do not read settings files or write files. They take DataFrames and settings values as arguments and return DataFrames.
3. Do not change files in `data/input/`, `assets/`, or `data/output/baseline/`. Hooks block this.
4. A change to a file in `settings/` changes model behavior. Tell the user each settings change and why.
5. Column, scenario, and region names come from the data dictionary in `assets/`. Rename columns only where data is read, with a mapping from `assets/` or `settings/`.
6. Each model has input, implementation, and output controls. Each control returns a DataFrame with columns `control`, `status` (PASS or FAIL), `detail`. A FAIL stops the run with a clear message.
   - Input: row counts, required columns, data types, nulls, allowed values, date coverage, totals against source.
   - Implementation: totals tie between steps, sign checks, no duplicate keys after merges.
   - Output: shape (scenarios x regions x quarters), totals tie to inputs, no NaN or inf.
7. The driver writes a run record to `data/output/`: run time, user, Git commit, settings files used, a hash of each input file, enabled models, and all control results.
8. The output of one model can be the input of the next. Do not change an output column, type, or key without a change to the data dictionary and a note to the user that downstream models are affected.
9. To add a model to a package: create `src/<model>/run.py`, add it to the switchboard and to the enabled models in `settings/`. Do not change the driver.
10. After a change to model code, run the model, then run the model-reconciliation skill. A numeric change is never silent.
