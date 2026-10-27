---
description: Plan a refactor across modules before any code is written
agent: agent
---

Plan a refactor of: ${input:scope:modules or folders to refactor}

Goal: ${input:goal:what the refactor should achieve}

Do not write or edit code. Produce the plan, then stop and wait for my approval.

1. Read every module in scope and every module that calls into it.
2. Run `python tools/check_style.py` on the scope and summarize the current errors by type.
3. Inventory table, one row per function: name, file, line count, number of call sites, verdict. Verdict is one of: keep, inline into `<caller>`, merge with `<function>`, rename to `<new name>`, delete.
4. Engine hand-off: for each forecast engine, name its one entry function, its inputs, and the exact output columns the DCF engine reads. Flag any column renamed between the two sides.
5. Target layout: the function list after the refactor, grouped by file. Check every new name against the banned words in `.github/instructions/python.instructions.md`. Show the call depth from each entry function.
6. Numbers: function count before and after, helper count before and after.
7. Equivalence check: which entry functions you will run before and after, and how you will compare outputs.
8. Risks: anything where behavior could change.
