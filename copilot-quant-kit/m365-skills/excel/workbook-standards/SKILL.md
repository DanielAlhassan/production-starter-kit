---
name: workbook-standards
description: "House rules for building and editing Excel workbooks: font colors by cell type, no numbers typed into formulas, consistent formulas, exact-match lookups, checks, and number formats. Use every time you create or change formulas, sheets, or formats in a workbook, and when the user asks how a workbook should be built."
---

# Workbook standards

Follow these rules for every change you make in a workbook. The full rulebook, with rule ids, severity, and fixes, is in `references/excel_rules.yaml`. When this file and the rulebook differ, the rulebook is correct.

## Rules for every change

1. **Font color shows the cell type.**
   - Blue (0000FF): typed-in numbers (inputs).
   - Black: formulas.
   - Green (008000): formulas that use another sheet.
   - Red (FF0000): formulas that use another file.
2. **No numbers typed into formulas.** Do not write `=A1*1.05`. Put 1.05 in a labeled blue input cell and link to it. Counts and unit conversions are allowed: 0, 1, 2, 4, 12, 100, 365, 1000, 1000000.
3. **Each input is entered once.** Every other use links directly to that cell.
4. **One formula along a row.** Write one formula and copy it across. If one period needs different logic, add a separate labeled row.
5. **Lookups are exact match.** Use `XLOOKUP` (or `INDEX`/`MATCH` with 0). If you use `VLOOKUP`, the last argument is `FALSE`.
6. **Do not hide errors.** No `IFERROR` or `IFNA` around a lookup. Add a check column that counts misses.
7. **No volatile functions** (`INDIRECT`, `OFFSET`, `NOW`, `TODAY`, `RAND`). Put the date in an input cell.
8. **No whole-column references** (`A:A`). Use an Excel Table or a fixed range.
9. **No merged cells.** Use Center Across Selection.
10. **Labels have units**, for example "Balance (USD mm)", or the sheet has a units marker in the top left.
11. **Every sheet has a title in A1.**
12. **Raw data sheets do not change.** Sheet names with raw, extract, source, or data_in hold data as received. Clean the data on another sheet or in Power Query.

## Extra rules by workbook type

- **Data prep:** lookup keys are unique; row counts tie from raw to output, with the difference explained.
- **Controls and reconciliations:** tolerances are blue input cells; every comparison has a Difference column and a Status column (PASS or FAIL); a summary shows matched, unmatched, and breaks, with one master check cell (0 = all pass).
- **Financial model:** use the `model-blueprint` skill for the layout. Number format `#,##0_);(#,##0);"-"_)`; no currency symbols in cells.

## When you change a workbook

- Before a large change, say which sheets and cells you will change.
- After the change, list every cell or range you changed.
- Do not delete sheets, rows, or columns without approval.
