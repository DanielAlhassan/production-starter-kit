---
name: workbook-audit
description: "Audit the open workbook against the house Excel rules and report every rule break by severity, then fix the breaks one rule at a time with approval. Use when the user asks to audit, review, check, or clean up a workbook, or asks if a workbook is ready to share."
---

# Workbook audit

The goal: a complete list of rule breaks in the workbook, with cell addresses, so the user can trust it before it goes to someone else. Then fix the breaks with the user's approval.

The rules, ids, severity, and fixes are in `references/excel_rules.yaml`. Use only those rules.

## Step 1: choose the profile

Ask which type of workbook this is, unless the user said it:
- **core**: always applies.
- **data_prep**: lookups and data cleaning.
- **recon**: controls and reconciliations.
- **model**: financial model.

More than one profile can apply.

## Step 2: audit (do not change anything)

Check every sheet, including hidden sheets, against each rule in the chosen profiles. Look at every used cell, not a sample.

- **C01 colors**: compare the font color with the cell type. Skip raw data sheets.
- **C02 partial inputs**: find numbers typed into formulas that are not in `allowed_constants`.
- **C03 inconsistent formulas**: in a row of copied formulas, find a cell whose formula has a different pattern from both neighbors.
- **C04 to C09**: errors, links to other files, merged cells, hidden sheets, volatile functions, whole-column references.
- **Copilot-only rules** (C10 to C12, D04, D05, R01 to R03, M02 to M06): judge from the workbook structure. Say what you looked at.

## Step 3: report

Give one table, high severity first:

| Rule | Severity | Sheet | Cells | What is wrong | Fix |
|---|---|---|---|---|---|

- Group cells for the same break into ranges (for example `Calc!C5:N5`).
- If a rule has more than 10 breaks, give the count and the first 10.
- End with: the total count by severity, the rules that passed, and the rules you could not check, with the reason.

## Step 4: fix (only with approval)

1. Ask which rules to fix. Suggest high severity first.
2. Fix one rule at a time. Before each rule, show the cells and the change (current formula and new formula).
3. After each rule, list every cell you changed. Then audit that rule again and show the result.
4. Do not change values in raw data sheets. Do not delete sheets, rows, or columns.
5. For a partial input (C02): add the new input cell in the inputs area with a label and units, color it blue, and link the formula to it.
6. For an inconsistent formula (C03): ask first. The difference can be an intended override. If it is intended, move it to its own labeled row.

## Notes

- The same checks run outside Excel with `audit_workbook.py` from the GitHub kit. Use it for large workbooks or many files.
- This skill does not change the rulebook. To change a rule, the user edits `excel_rules.yaml` in the GitHub kit and copies it here.
