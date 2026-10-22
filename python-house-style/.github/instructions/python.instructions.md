---
applyTo: "**/*.py"
---

# Python house style

This is professional code that other people will debug, review, and hand to Model Risk. Write the simplest code that solves the problem. When in doubt, write less.

## 1. Simplest solution first

- Before writing code, ask: what is the simplest way to get this result? Prefer one clear pandas expression over a custom function, and plain functions over classes.
- Do not add classes, dataclasses for config, abstract base classes, registries, factories, custom decorators, or logging frameworks unless I ask.
- Do not add defensive checks for things that cannot happen. Check inputs once, at the engine boundary.

## 2. Single source of truth

- Every fact lives in one place. A rate, a mapping, a column list, or a scenario name is defined once and read from there.
- Data is not code. Mappings, lookup tables, scenario lists, rates, and parameters go in an asset file (Excel or CSV) that the code reads, not in constants at the top of a module.
- Constants: only for a value that is fixed by definition and used in 2 or more places. A constant used once is inlined where it is used.
- Before adding a value, search the repo and the asset files for it. If it exists, read it from there.

## 3. Helpers

- Create a function only when the same logic is used in 2 or more places. Single-use logic stays inline.
- A long function may be split only into named business steps: steps you would name when walking someone through the model (project runoff, discount cash flows, build the scenario table). Never split into utility pieces. Mark a single-use business step with `# house-style: step` on its `def` line.
- Never wrap a single library call in its own function. Call the library directly.
- Before writing a new function, search the repo for one that already does it. Reuse or extend it.
- When consolidating, merge duplicates into one function and delete the copies. The function count should go down.
- Leading underscore: rare. Default is no underscore.

Bad:

```python
SCENARIO_NAMES = {"base": "Base", "adv": "Adverse", "sev": "Severe"}

def _frame(path):
    return pd.read_excel(path)

def _normalize_text(value: str) -> str:
    return value.strip().lower()

deposits = _frame(config.deposit_file)
deposits["scenario"] = deposits["scenario"].map(_normalize_text).map(SCENARIO_NAMES)
```

Good: the mapping lives in the model's input workbook, the helpers are gone.

```python
deposits = pd.read_excel(config.deposit_file)
scenario_names = pd.read_excel(config.input_workbook, sheet_name="Scenarios")
deposits["scenario"] = deposits["scenario"].str.strip().str.lower()
deposits = deposits.merge(scenario_names, on="scenario", how="left")
```

## 4. Easy to debug

The test: I can put one breakpoint in the entry function, step down, and see every value without opening five files.

- Name intermediate results. Assign each meaningful step to a variable with a domain name (`runoff_balances`, `discounted_flows`) so it can be inspected. No calls nested more than two deep on one line.
- Keep the call depth shallow: entry function, then business steps, then library calls. At most two levels of our own functions below the entry function.
- No nested functions, no closures, no lambdas assigned to names. A short inline lambda as a sort key is fine.
- No hidden state. Do not change global variables. Do not use `inplace=True`; assign the result.
- No silent failures. No bare `except`, no `except: pass`. When raising, name the scenario, file, or column in the message.
- List arguments explicitly. No `**kwargs` passed between our own functions.

## 5. Naming

- Pattern: verb + domain noun, usually 2 to 4 words. `standardize_scenario_names`, `project_deposit_runoff`, `discount_cash_flows`.
- Pick the verb that says what actually happens. One-word function names (`_frame`, `_row`) are not allowed.
- Banned words, words to avoid, generic names, and allowed verbs are listed in [tools/house_style_terms.csv](../../tools/house_style_terms.csv). That file is the single source of truth for word rules. Banned words apply in any form, in names, comments, and docstrings. Do not swap in a synonym with the same meaning (for example `verify` for validate); use the replacement in the file.
- Domain nouns: scenario, horizon, runoff, cap_rate, discount_rate, cash_flow, deposits, loans, loss. One concept, one word, everywhere.

## 6. Docstrings and comments

- Only entry functions get a docstring: the functions other modules call. Internal functions get none.
- An entry function docstring says what the function does in one plain sentence, then what goes in and what comes out. For an engine entry function, list the output columns. Enough that a reviewer understands it without reading the body, short enough to read in a few seconds. Usually 3 to 8 lines.
- Write docstrings in plain, direct sentences. No filler ("This function is responsible for..."), no repeating the type hints in words.
- Comments only where the code does something that is not obvious: a business rule, a workaround, a reason a value is what it is. Say why, not what. No comments that restate the line below.

Example of an entry function docstring:

```python
def project_deposit_runoff(deposits: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """Project deposit balances over the horizon using each product's runoff rate.

    deposits: one row per product with balance and runoff_rate.
    Returns one row per product and period with columns
    product, period, balance, runoff_amount.
    """
```

## 7. Type hints

Type hints on every argument and the return type, on every function.

## 8. Before finishing

Run `python tools/check_style.py <package folder>` and fix every ERROR. List any WARN you left and why.
