# Additions for .github/copilot-instructions.md

Paste the block below into your existing `.github/copilot-instructions.md`. Do not replace the file. Keep the whole file short: Copilot sends it with every request, so every line costs credits.

```markdown
## How to work in this repo

- Plan first for any change that touches more than one function. Wait for approval.
- Make small changes. After each change, read the hook messages and fix what they report.
- Never change model numbers silently. After a change to calculation code, run the model-reconciliation skill and report PASS or FAIL per output.
- Do not edit inputs, baselines, Excel files, or `.github/hooks/`. Hooks block this. Ask the user.
- Say what you checked and what you did not check. Do not say "done" if a check failed or did not run.

## Writing

- For any prose (documentation, docstrings, comments, README, change records, emails, slide text), use the ASD-STE100 writing skill. Do not wait for the user to ask.
- No em dashes.
```
