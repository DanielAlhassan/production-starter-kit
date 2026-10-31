---
applyTo: "**/*.py"
description: "Structure and controls for model code (DCF engine, forecast modules, controls)."
---

# Model code structure

Use this layout for every model module. Do not invent a new layout.

```
config/                  Excel parameter files. All numbers the model uses come from here.
data_dictionary.xlsx     Column names, data types, units, and allowed values (scenarios, regions).
src/<module>/
  read_inputs.py         Read source files. Run input controls.
  calc_<step>.py         Pure calculation steps. Input is a DataFrame, output is a DataFrame.
  write_outputs.py       Run output controls. Write files.
run_<module>.py          Entry point. Reads config, calls steps in order, writes the run record.
tests/                   One test file per calc file.
recon/                   recon_config.xlsx, baseline/ outputs, results/.
```

## Rules

1. No numbers in code. Rates, horizons, tolerances, mappings, and file paths go in `config/`. The code reads them.
2. Column names, scenario names, and region names come from `data_dictionary.xlsx`. Do not rename a column inside a calc step. Rename only in `read_inputs.py`, with a mapping read from config.
3. Calc steps do not read or write files and do not use global state. Same input gives the same output.
4. Every module has three control types. Each control returns a DataFrame with columns `control`, `status` (PASS or FAIL), `detail`.
   - Input controls: row counts, required columns, data types, nulls, allowed values, date coverage, totals against source.
   - Implementation controls: sums that must tie between steps, sign checks, no duplicated keys after merges.
   - Output controls: shape (scenarios x regions x 40 quarters), totals tie to inputs, no NaN or inf.
5. A FAIL in any control stops the run with a clear message. Do not continue on bad data.
6. `run_<module>.py` writes a run record: run time, user, Git commit, config file names, a hash of each input file, and all control results.
7. The output of one module is the input of the next. Do not change an output column, type, or key without a change to `data_dictionary.xlsx` and a note to the user that downstream modules are affected.
8. After a change to calculation code, run the output reconciliation (model-reconciliation skill). Report the result. A numeric change is never silent.
