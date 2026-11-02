# Additions for .github/copilot-instructions.md

Paste the block below into your existing `.github/copilot-instructions.md`. Do not replace the file. Keep the whole file short: Copilot sends it with every request, so every line costs credits.

```markdown
## How to work in this repo

- Plan first for any change that touches more than one function. Wait for approval.
- Make small changes. After each change, read the hook messages and fix what they report.
- Never change model numbers silently. After a change to calculation code, run the model-reconciliation skill and report PASS or FAIL per output.
- Layout: `data/input`, `data/output`, `assets` (stable methodology files), `settings` (YAML), `src/run.py` with one `run()`, and `assembly/driver.py` plus `assembly/switchboard.py` for a package. Follow the model-structure instructions.
- Do not edit `data/input/`, `assets/`, `data/output/baseline/`, Excel files, or `.github/hooks/`. Hooks block this. Ask the user.
- A change to files in `src/`, `assembly/`, or `settings/` is high risk. Before you say done, run the tests and `/reconcile`, then tell the user to run `/review-model` in a new chat. Do not review your own change.
- Files in `data/input/`, `assets/`, and `data/output/baseline/` are read-only. If an edit fails there, stop and tell the user. Do not change file permissions.
- Say what you checked and what you did not check. Do not say "done" if a check failed or did not run.

## Writing

- For any prose (documentation, docstrings, comments, README, change records, emails, slide text), use the ASD-STE100 writing skill. Do not wait for the user to ask.
- No em dashes.
```
