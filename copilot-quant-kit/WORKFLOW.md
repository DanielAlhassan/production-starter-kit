# My Copilot workflow: one page

One chat per phase. Start a new chat (Ctrl+N) when the phase changes.

## 1. Start

| Situation | Command |
|---|---|
| New model repo, or a new model in the package | `/scaffold-model` |
| New task, ideas not clear yet | Brain dump agent (or Microsoft Copilot, no credit cost) |
| Big repo, need an inventory first | Ask for the `Explore` subagent: "Use Explore to list ... Return only the findings." |

## 2. Plan

| Situation | Command |
|---|---|
| Change touches more than one function | Plan agent, Opus. Approve the plan before code. |
| Point Copilot at the code | `#codebase`, or `#file` for one file. Do not paste code or transcripts. |

## 3. Build

| Situation | Command |
|---|---|
| Run an approved spec | `model-builder` agent |
| New workbook or model in Excel | `@model-blueprint` |
| Side question in the middle of a task | `/fork` |
| Chat has 20 to 30 turns | `/compact focus on <decisions to keep>` |

## 4. Check

| Situation | Command |
|---|---|
| Did the numbers move? | `/reconcile` |
| Review my change or a teammate's model | `/review-model src/<model>` (or the **Review this change** button after model-builder) |
| Names and types do not match across models | `/data-dictionary data/output` |
| Is this workbook ready to share? (VS Code) | `excel-audit` skill: `audit_workbook.py <file> --profile ...` |
| Is this workbook ready to share? (Excel) | `@workbook-audit` |
| Convert a workbook to Python: step 1 | `map_workbook.py <file> --out docs/<name>_formula_map.md` |

## 5. Record and share

| Situation | Command |
|---|---|
| End of a task: log progress | `/log-progress` |
| Change log entry for MRM | `/change-record` |
| Model documentation | "Use the model-documentation skill for src/<model>" |
| Numbers on what the guardrails did | `/workflow-evidence 2026-11-01` |
| Weekly update (manager 1:1, team meeting) | `/prepare-update manager` or `/prepare-update team` |

## 6. End of a phase

1. Update the `## Current state` section in `docs/progress_log.md`: current commit, open items, verified commands, file owners, baselines. The next session starts with it.
2. Close the chat. Start the next phase in a new chat.

## Weekly

| Command | Why |
|---|---|
| `/chronicle:cost-tips` | Find expensive habits |
| `/troubleshoot` | A hook, skill, or prompt does not load |

Type `/` in chat to see every command with its description.
