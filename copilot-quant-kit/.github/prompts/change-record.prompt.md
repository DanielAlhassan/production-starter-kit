---
description: "Write a change record for the current branch: what changed, why, numeric impact."
agent: agent
tools: ["read", "search", "execute"]
---

Write a change record for the work on this branch.

1. Run `git log --oneline main..HEAD` and `git diff --stat main...HEAD`. Read the diff of each changed calculation file.
2. Read the latest summary in `recon/results/`. If there is none, say that reconciliation did not run.
3. Write one row per logical change in the model-documentation template, section 9 format: date, commit, change, reason, numeric impact, author. Leave reviewer empty.
4. Use the ASD-STE100 writing skill, STE-flavored mode. No em dashes.
5. If the reason for a change is not clear from the code or commit message, write `[TO CONFIRM: question]`.

Show the result in chat. Do not write a file unless I ask.
