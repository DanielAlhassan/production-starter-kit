---
name: python-house-style
description: Daniel's Python house style for the DCF and forecast engines. Use whenever writing, refactoring, or consolidating Python in this repo, especially when adding functions, naming things, or merging code from different authors.
---

# Python house style

The rules are not written here. They live in the repo, in one place, and GitHub Copilot reads the same files. This skill only says where they are and how to use them.

## Single source of truth

| What | File in the repo root |
|---|---|
| Style rules: simplest solution, single source of truth, helpers, debugging, naming, docstrings, comments, constants, type hints | `.github/instructions/python.instructions.md` |
| Banned words, words to avoid, generic names, allowed verbs | `tools/house_style_terms.csv` |
| Project context, plan-first rule, refactor equivalence check, engine hand-off rules | `.github/copilot-instructions.md` |
| Hard check | `tools/check_style.py` |

## Steps

1. Before writing or changing any Python, read `.github/copilot-instructions.md`, `.github/instructions/python.instructions.md`, and `tools/house_style_terms.csv`. Follow them exactly.
2. If those files are not in the repo, stop and tell Daniel. Do not write the rules from memory and do not create a second copy of them. Ask him to add the `copilot-setup` folder to the repo root.
3. For any change that touches more than one function, write the plan first and wait for approval, as `copilot-instructions.md` says.
4. Before finishing, run `python tools/check_style.py <package folder>` and fix every ERROR. List any WARN you left and why.

## Changing a rule

Edit the repo file, not this skill. Word rules go in the CSV. Everything else goes in `python.instructions.md`.
