---
name: python-house-style
description: Daniel's Python house style for the DCF and forecast engines. Use whenever writing, refactoring, or consolidating Python in this repo, especially when adding functions, naming things, or merging code from different authors.
---

# Python house style

This code was written by three people and is being consolidated. The goal is less code, one vocabulary, and names a person would say out loud in a model walkthrough. Code should not read as AI-written.

## 1. Helpers

- Create a function only when the same logic is used in **2 or more places**. Single-use logic stays inline.
- Splitting a long function is allowed only into **named business steps**: steps you would name when walking someone through the model (project runoff, discount cash flows, build the scenario table). Never split into utility pieces.
- Never wrap a single library call in its own function. Call the library directly.
- Before writing a new function, search the repo for one that already does it. Reuse or extend it instead of adding a near-duplicate.
- When consolidating, merge duplicates into one function and delete the copies. Net function count should go down, not up.
- Leading underscore: rare. Use it only for internal plumbing in a module that nothing outside should call. Default is no underscore.

### Example

Bad: two functions, one used once, one a thin wrapper.

```python
def _read_excel(path: Path, sheet: str) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet)

def _read_parameters(path: Path) -> pd.DataFrame:
    df = _read_excel(path, "Parameters")
    df.columns = df.columns.str.strip().str.lower()
    return df.dropna(how="all")

params = _read_parameters(config.parameter_file)
```

Good: inline at the one place it is used.

```python
params = pd.read_excel(config.parameter_file, sheet_name="Parameters")
params.columns = params.columns.str.strip().str.lower()
params = params.dropna(how="all")
```

If the same three lines are needed in a second place, then make one function: `read_parameter_sheet(path: Path) -> pd.DataFrame`.

## 2. Naming

- Pattern: **verb + domain noun**, usually 2 to 4 words. Descriptive, not long. `standardize_scenario_names`, `project_deposit_runoff`, `discount_cash_flows`.
- Preferred verbs: `get`, `read`, `write`, `compute`, `project`, `discount`, `check`, `map`, `build`, `prepare`, `process`, `sanitize`, `standardize`, `rename`.
- Pick the verb that says what actually happens. If columns are renamed, say `rename_..._columns`. If values are made consistent, say `standardize_...`.

### Banned words (any form: function, variable, argument, class, comment, docstring)

| Banned | Use instead | Example |
|---|---|---|
| validate, validated, validation | check | `check_cap_rate_bounds` |
| resolve, resolved, resolver | get, map, pick | `get_scenario_path`, `map_scenario_to_sheet` |
| normalize, normalized | standardize, rename | `standardize_scenario_names` |
| ensure | check, add | `add_missing_horizon_columns` |
| handle, handler | name the actual action | `fill_missing_rates`, `process_loan_file` |

### Avoid

- `load`: use `read_` for files, `get_` for lookups.
- Generic names: `utils`, `helpers`, `manager`, `data`, `info`, `obj`, `tmp`, `_impl`, `_internal`.

### Domain nouns

Use the team's terms, not invented ones: `scenario`, `horizon`, `runoff`, `cap_rate`, `discount_rate`, `cash_flow`, `deposits`, `loans`, `loss`. Add to this list rather than inventing synonyms. One concept, one word, everywhere.

## 3. Type hints and docstrings

- Type hints on every function signature, including the return type.
- Public functions: short docstring. One-line summary, then `Args` / `Returns` only where not obvious from names and hints. Aim for 6 lines or fewer.
- Private helpers: no docstring. A one-line comment only if the logic is not obvious.

## 4. Before finishing

Run the check script on the files you changed and fix everything it flags:

```
python tools/check_style.py path/to/changed_files.py
```

Do not rename around the banned list with synonyms that mean the same thing (e.g. `verify` for validate). Use the replacement verbs above.
