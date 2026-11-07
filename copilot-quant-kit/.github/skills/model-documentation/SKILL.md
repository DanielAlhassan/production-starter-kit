---
name: model-documentation
description: "Write or update model documentation, methodology notes, implementation notes, control descriptions, or a model change record for MRM review. Use when the user asks to document a model, a module, a control, or a change, or when a model change is ready for review."
---

# Model documentation

Documentation must let a validator rerun and challenge the model without asking the developer.

## Steps

1. Read the code first: `assembly/driver.py` and `assembly/switchboard.py` (package), `run.py` and the step files in `src/`, the controls, the YAML files in `settings/`, and the files in `assets/` (including the data dictionary). Do not describe what the code does not do.
2. Copy `template.md` to `docs/<model>.md`, or update the existing file. Keep the section order.
3. Fill each section from the code and config. Where a fact is not in the code (owner, business purpose, approvals), write `[TO CONFIRM: question]`. Do not invent it.
4. Write in STE-flavored mode with the ASD-STE100 writing skill. Use strict mode for the run steps and the controls tables.
5. Every number in the document comes from a file. Name the file. Do not type numbers from memory.
6. For a change record, fill section 9 only and include the reconciliation result.
7. At the end, list every `[TO CONFIRM]` item for the user.

## Quality checks before you finish

- A reader can run the model from section 5 alone.
- Every control in the code is in section 6, and every control in section 6 is in the code.
- Every assumption in section 7 has a reason and an impact.
