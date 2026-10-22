# Project instructions

## What this repo is

RRP valuation models. A DCF engine discounts cash flows that come from separate forecast engines (deposits, loans, loss). Code from three authors is being consolidated into one engine. The goal is less code, one vocabulary, and code a person can step through in a debugger without jumping between many small functions.

## How to work

- For any change that touches more than one function, write a plan first and wait for my approval. The plan lists every function you will add, remove, merge, or rename, with its new name and how many places call it. No code in the plan.
- Do not change model logic or outputs during a refactor unless I ask. A refactor that changes a number is a bug.
- Before a refactor, save the current outputs of the affected entry function. After the refactor, compare with `pd.testing.assert_frame_equal`. Report the result.
- Before you say you are done, run `python tools/check_style.py <package folder>` and fix every ERROR. List any WARN you left and why.

## How the engines connect

- Each forecast engine has one public entry function. The DCF engine calls only that function.
- The entry function returns a DataFrame with a fixed set of columns. Those columns are written in the entry function's docstring. If you add, remove, or rename a column, update the docstring and every caller in the same change.
- Use the same column names on both sides of the hand-off. No renaming at the boundary.

## Code style

Follow `.github/instructions/python.instructions.md` for all Python. Word rules live in `tools/house_style_terms.csv`. The short version:

- Simplest solution that works. Professional, readable, easy to debug.
- Single source of truth. Data and parameters go in asset files (Excel, CSV) the code reads, not in constants.
- No helper unless the logic is used in 2 or more places. No wrappers around a single library call.
- Names are verb + domain noun, with no banned words.
- Type hints on every function. Docstrings on entry functions only. Comments only where something is not obvious.
