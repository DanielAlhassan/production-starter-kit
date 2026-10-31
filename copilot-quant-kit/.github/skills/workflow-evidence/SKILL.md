---
name: workflow-evidence
description: "Turn the Copilot hook audit log into numbers: sessions, edits blocked, issues caught after edits, failures caught before finish. Use when the user wants to show how the AI workflow and guardrails work, needs numbers for an update or a demo, or asks what the hooks did."
---

# Workflow evidence

The hooks write every prompt, tool call, block, and check result to `.copilot-audit/agent_actions.jsonl` in each repo. This skill turns the log into a small table.

## Steps

1. Ask the user for the repos and the date range if they are not clear.
2. Run:
   ```
   python <this skill folder>/scripts/summarize_audit.py <repo> [<repo> ...] --since YYYY-MM-DD
   ```
3. Show the table. Then give three lines, each backed by a number in the table:
   - What the guardrails stopped (blocked edits and commands).
   - What the checks caught before the user saw it (edit issues, finish checks that failed and were fixed).
   - The volume of work (sessions, prompts, Python files checked).
4. If the user wants slides, pass the table to the stakeholder-update skill.

## Rules

- Use only numbers from the table. Do not estimate time saved. Ask the user for that number and label it as their estimate.
- Do not show prompt text from the log in slides or emails without the user's approval. Prompts can hold sensitive details.
- No em dashes. Use the ASD-STE100 writing skill, STE-flavored mode.
