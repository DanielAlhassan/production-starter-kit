# Copilot house style setup

Copy everything in this folder into the root of the repo. Folders that start with a dot are hidden in Finder; press Cmd+Shift+. to show them.

| File | When it runs | What it does |
|---|---|---|
| `.github/copilot-instructions.md` | Every Copilot Chat and agent request in this repo | Project context, plan-first rule, engine hand-off rules |
| `.github/instructions/python.instructions.md` | Every request that involves a .py file | Full house style |
| `tools/house_style_terms.csv` | Read by the checker and linked from the instructions | Single source of truth for banned words, generic names, verbs |
| `tools/check_style.py` | Copilot runs it before finishing; the git hook runs it on every commit | Hard check that does not depend on the model |
| `.pre-commit-config.yaml` | Every `git commit` | Blocks a commit with any ERROR |
| `.vscode/tasks.json` | Terminal > Run Task > house style check | Puts every issue in the Problems panel |
| `.github/prompts/plan-refactor.prompt.md` | Type `/plan-refactor` in Copilot Chat | Inventory and plan, no code |
| `.github/skills/python-house-style/SKILL.md` | When Claude or a Copilot agent picks up the skill | Points to the files above, holds no rules of its own |
| `.github/prompts/flatten-helpers.prompt.md` | Type `/flatten-helpers` with a file open | Inline helpers in one file, outputs unchanged |

## One-time steps

1. Change `src` to your package folder in `.pre-commit-config.yaml` and `.vscode/tasks.json`.
2. `pip install pre-commit` then `pre-commit install`.
3. In VS Code settings, confirm "Use Instruction Files" for Copilot Chat is on (it is on by default).
4. Run `python tools/check_style.py src` once to see where the code stands today.

To change a word rule, edit the CSV. Nothing else needs to change.
