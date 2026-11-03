---
name: progress-log
description: "Keep one progress log per project (docs/progress_log.md) and scope each update from the last one given to the same audience (manager, team). Use at the end of any task to log progress, and when the user asks what to report, what is new since the last update, or to prepare an update or deck."
---

# Progress log

One standard in every project:

| Where | What |
|---|---|
| Git commits | What changed in the code |
| `docs/progress_log.md` | `## Current state` (commit, open items, verified commands, baselines) and `## Log`, one line per item |
| `~/.copilot/updates_given.csv` | Each update given: date, audience, projects, deck. One file for all projects. |

Log line format: `- 2026-11-02 | <area> | <what, one sentence> [done|decision|issue|next]`

Audiences: `manager` (weekly 1:1), `team` (weekly team meeting). Each has its own starting point.

## Script

`scripts/progress.py` in this skill folder. Run it from the project folder.

| Command | Use |
|---|---|
| `python <skill>/scripts/progress.py add <area> "<text>" --tag done` | Add a log line. Creates the file if it is missing. |
| `python <skill>/scripts/progress.py scope manager [--repos A B]` | Show what is new for this audience since its last update: log lines, commits, current state, last reconciliation. First update: 7 days back. |
| `python <skill>/scripts/progress.py record manager [--repos A B] [--deck path]` | Mark the update as given. The next scope starts here. |

## Steps: log progress (end of each task)

1. Write 1 to 3 log lines with `add`. One line per result, decision, issue, or next step. Use the ASD-STE100 writing skill, strict mode. No em dashes.
2. Write facts only: what changed, the check results (PASS or FAIL), the numbers from files. No adjectives.
3. If the open items, verified commands, or baselines changed, update `## Current state` in `docs/progress_log.md`.

## Steps: prepare an update

1. Run `scope <audience>` for the projects the user names.
2. Draft the content from the scope only: done, decisions, issues, next. Do not repeat items from earlier updates; the scope already starts after the last one.
3. Show the draft to the user. Wait for approval.
4. Build the deck with the stakeholder-update skill (3 slides) and the wf-deck skill.
5. Run `record <audience> --deck <path>` only after the user confirms the update was given.
