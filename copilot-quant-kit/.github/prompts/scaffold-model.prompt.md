---
description: "Create the standard model layout, or add a new model to a package (src/<model>, switchboard, settings)."
agent: model-builder
argument-hint: "model name, and 'package' if the repo has several models"
---

Set up the model ${input:model:model name}.

Follow the layout in the model-structure instructions exactly.

**If the repo has no `src/` yet:**
1. Create `data/input/`, `data/output/`, `data/output/baseline/`, `data/output/recon/`, `assets/`, `settings/`, `src/`, `tests/`. Add a `.gitkeep` to each empty folder.
2. Create `settings/run.yaml` with the run values the user gives (dates, scenarios, regions, paths). Ask for them. Do not invent values.
3. Create `src/run.py` with one callable `run()`: read `settings/run.yaml`, read inputs, call the steps, run the controls, write outputs. Leave step calls as a list the user fills in.
4. If the user said this is a package, use `src/<model>/run.py` instead and also create step 5.
5. Package only: create `assembly/driver.py` (reads `settings/run.yaml`, calls the switchboard, writes the run record) and `assembly/switchboard.py` (maps each model name to its `run()`, dispatches the models enabled in `settings/models.yaml`). Create `settings/models.yaml` with this model enabled.

**If the repo is a package and `assembly/` exists:**
1. Create `src/<model>/run.py` with one callable `run()`, following the other models in `src/`.
2. Add the model to `assembly/switchboard.py` and to `settings/models.yaml`, disabled until the user enables it.
3. Do not change `assembly/driver.py`.

Then list what you created and what the user must add: input files in `data/input/`, methodology files in `assets/`, settings values, and a recon entry in `settings/recon.yaml`.
