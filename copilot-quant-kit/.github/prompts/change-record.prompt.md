---
description: "Write a change record for the current branch: what changed, why, numeric impact."
agent: agent
tools: ["read", "search", "execute"]
---

Write a change record for the work on this branch.

1. Run `git log --oneline main..HEAD` and `git diff --stat main...HEAD`. Read the diff of each changed file in `src/`, `assembly/`, and `settings/`.
2. List settings changes on their own: file, key, old value, new value. A settings change changes model behavior.
3. Read the latest summary in `data/output/recon/`. If there is none, say that reconciliation did not run.
4. Write one row per logical change in the model-documentation change log format: date, commit, change, reason, numeric impact, author. Leave reviewer empty.
5. Use the ASD-STE100 writing skill, STE-flavored mode. No em dashes.
6. If the reason for a change is not clear from the code or commit message, write `[TO CONFIRM: question]`.

Show the result in chat. Do not write a file unless I ask.
