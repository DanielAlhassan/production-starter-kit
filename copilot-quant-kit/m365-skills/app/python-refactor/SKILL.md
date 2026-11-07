---
name: python-refactor
description: "Refactor Python models and notebooks from bundle files (text files with '===== FILE:' markers made by pack_files.py), one complete file at a time, with the house rules from the bundle. Use when the user attaches a bundle, asks to refactor or convert a model, or asks for the next file of a refactor plan."
---

# Python refactor from bundles

The user works in VS Code, but cannot run Copilot there. You write the code here, and the user runs and tests it on their machine. So every answer must be complete, exact, and easy to copy.

## The files you get

- **Bundle** (`<name>_bundle.txt`): one text file with many files.
  - Section RULES: the house rules from the repo. They are the only source of the rules. Follow them exactly. If the RULES section is missing or empty, stop and ask for it. Do not write code from rules you remember.
  - Section CODE: each file starts with `===== FILE: <path> =====`. Paths are from the repo root.
  - Section DATA: row count, columns, and types of each input, and sometimes the first rows. Use only these column names and types. If a column you need is not there, ask.
- **Example bundle** (`example_bundle.txt`): a finished refactor. Copy its structure, names, settings, and tests.
- **Plan** (`<name>_plan.md`): the approved plan, if the work has started. The plan is the source of the task status, not the chat.

## Step 1: plan (no code)

If there is no approved plan, give one:
1. The new files with their paths, and what each one does.
2. For each new file: what moves into it, and from which old file and function or cell.
3. The settings that go to YAML.
4. The order to write the files, with a numbered checkbox for each step.
5. How to prove the outputs did not change: which outputs to compare against the old code, with the tolerance.
6. Your questions.

Then stop. Ask the user to save the plan as `<name>_plan.md` and attach it in the next chats.

## Step 2: one file per answer

When the user asks for a step:
- Write **one complete file**. Never send a part of a file, a diff, or "the rest stays the same".
- Start it with the marker line, inside one code block:

  ````
  ```python
  ===== FILE: src/loss/steps.py =====
  <complete file>
  ```
  ````
  The user's `unpack_files.py` reads this marker. Use the exact repo path.
- Keep the behavior the same as the old code: same inputs, same outputs, same order of rows and columns, unless the plan says otherwise. If you see a bug in the old code, keep it, and report it separately.
- After the code block, give:
  1. The commands to run, from the repo root:
     - `python -m ruff check <file>`
     - `python tools/check_style.py <folder>`
     - `python -m pytest -q`
     - the output comparison from the plan
  2. What the user must check by hand, if anything.
  3. The plan line to tick, for example "Step 3 done".

## When the user pastes an error or a difference

- Fix the cause. Give the complete corrected file again with the marker line.
- If a number differs from the old code, explain why before you change anything. A difference can be a bug in the old code.

## Do not

- Do not invent files, functions, columns, or settings that are not in the bundle or the plan.
- Do not change files outside the step you were asked for.
- Do not shorten a file because it is long. If a file is too long for one answer, say so and propose a split into smaller files first.
