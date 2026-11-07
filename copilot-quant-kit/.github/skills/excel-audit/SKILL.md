---
name: excel-audit
description: "Check an Excel workbook against the house Excel rules (colors, partial inputs, inconsistent formulas, errors, lookups, number formats) and write a formula map. Use when the user asks to audit, review, or map an .xlsx or .xlsm file, before an Excel model goes to review, or before converting a workbook to Python."
---

# Excel audit

The goal: find every rule break in a workbook with a script, not by reading cells one at a time, and show how the workbook calculates.

## Files

- `excel_rules.yaml`: the rulebook. One source for this skill and for the Copilot in Excel skills. After a change, copy it to OneDrive: `skills/workbook-standards/references/` and `skills/workbook-audit/references/`.
- `scripts/audit_workbook.py`: the checker. Do not write a new one.
- `scripts/map_workbook.py`: the formula map.
- `scripts/excel_common.py`: shared cell and formula functions.

## Steps

1. Ask which profile applies if it is not clear: `data_prep` (lookups, cleaning), `recon` (controls and reconciliations), `model` (financial model). Core rules always apply. More than one profile is allowed.
2. Run the audit:
   `python <skill>/scripts/audit_workbook.py <file> --profile <profiles> --out <file>_audit.csv`
3. Report the findings by severity: high first. Give the rule, the cells, and the fix. Do not list every cell when there are many; give the count and the first cells.
4. List the rules the script cannot check (the last line of the output). Review those by reading the workbook only if the user asks.
5. Fix only with approval, one rule at a time:
   - Colors: `--fix-colors` writes `<name>_colors_fixed.xlsx`. The original does not change.
   - Other rules: give the cell, the current formula, and the new formula. The user makes the change in Excel or approves a script for it.
   - openpyxl can drop charts, pivot tables, and macros when it saves. Always write to a new file and tell the user to check it.
6. For a formula map (also the first step of an Excel-to-Python conversion):
   `python <skill>/scripts/map_workbook.py <file> --out docs/<name>_formula_map.md`

## Exit code

`audit_workbook.py` exits 1 if a high-severity rule is broken. The Git commit check runs it on staged Excel files as a warning only.
