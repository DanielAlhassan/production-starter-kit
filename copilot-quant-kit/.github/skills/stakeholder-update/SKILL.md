---
name: stakeholder-update
description: "Turn finished code or model work into a stakeholder update: a 3-slide deck outline, a status email, or a leadership summary. Use when the user asks for an update, status, summary for a manager, slides about the work, or what to tell stakeholders."
---

# Stakeholder update

The reader is busy and not technical. Show the result, the method in brief, and why it matters.

## Inputs to read first

- The scope from the progress-log skill (`progress.py scope <audience>`): what is new since the last update to this audience. Do not repeat items from earlier updates.
- The change records and the latest summary in `data/output/recon/`.
- Ask the user for the audience (manager or team) if it is not clear.

## Deck: 3 slides maximum

1. **Summary.** One headline sentence with the result. Three bullets maximum.
2. **What was done and how.** Steps in plain words. One simple diagram or table if it helps. No code.
3. **Why it matters.** Impact in time saved, risk reduced, controls added, or decisions made possible. Use numbers only when they come from a file. Name the source in the speaker notes.

Build the deck with the wf-deck skill: write the 3 slides as a deck YAML file and run its renderer. Do not build slides any other way.

## Email

Subject line with the result. Then: what is done, what is next, what you need from the reader (if anything), and the risks. Under 150 words.

## Rules

- Write with the ASD-STE100 writing skill in STE-flavored mode. No em dashes.
- No number without a source file. If a number is an estimate, say "about" and say how it was estimated.
- Do not claim a control or a test that did not run. If reconciliation failed or did not run, say so.
