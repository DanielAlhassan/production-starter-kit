---
description: "At the end of a task: add 1 to 3 lines to docs/progress_log.md and update its current state."
agent: agent
tools: ["read", "search", "execute", "edit"]
---

Use the progress-log skill, "log progress" steps, for the work done in this chat.

1. Read what changed: this chat, `git diff --stat`, and the latest summary in `data/output/recon/` if there is one.
2. Show me the 1 to 3 log lines you will add. Wait for my OK.
3. Add them with the script. Update `## Current state` if it changed.
