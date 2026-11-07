---
name: model-blueprint
description: "Design the sheet layout of a new workbook (financial model, data prep, or reconciliation) before any formulas are written, then build the empty structure on approval. Use when the user starts a new workbook or model, asks how to lay out a workbook, or wants to restructure a workbook that is hard to follow."
---

# Model blueprint

The goal: agree the structure of a workbook before building it. A clear structure makes the workbook easy to check and easy to convert to Python later. The layout follows the CFI and Macabacus financial modeling guidelines and the `workbook-standards` rules.

## Step 1: ask

Ask only what the user has not said:
1. What the workbook is for, and who reads the output.
2. Type: financial model, data prep, or reconciliation.
3. Time periods (annual, quarterly, monthly) and how many.
4. Main inputs and where they come from (file, system, typed in).
5. Main outputs (numbers, tables, charts).

## Step 2: propose the blueprint (do not build yet)

Give a table of the sheets in order:

| Sheet | Purpose | Main rows or columns | Links in from | Links out to |
|---|---|---|---|---|

Use these sheet orders.

**Financial model**
1. `Cover`: name, purpose, owner, version, date, table of contents, units, active scenario, and the summary of checks (one master check: 0 = all pass).
2. `Dashboard`: the main outputs. Links only.
3. `Inputs`: every typed-in number, once, in blue, with units and source.
4. `Drivers`: assumptions by scenario, with one master scenario switch.
5. One sheet per schedule (for example `Revenue`, `Costs`, `Balances`). Each schedule has three parts:
   - Enter: links in from inputs, drivers, and other schedules.
   - Calculate: small steps, one formula per row, copied across.
   - Exit: results that other sheets use.
   Balances that change over time use a corkscrew: opening, plus additions, minus reductions, closing. The next opening links to the last closing.
6. `Statements` or `Outputs`: links only, no calculations.
7. `Checks`: every check with a tolerance input and a PASS or FAIL status.

**Data prep**
1. `Cover` (with checks summary), 2. `Raw_<source>` (data as received, not edited), 3. `Map` (lookup tables with unique keys), 4. `Clean` (one step per column), 5. `Output`, 6. `Checks` (row counts raw to output, duplicate keys, lookup misses).

**Reconciliation**
1. `Cover` (with checks summary), 2. `Inputs` (tolerances, dates), 3. `Source_A` and `Source_B` (as received), 4. `Recon` (key, value A, value B, Difference, Status), 5. `Summary` (matched, unmatched, breaks, master check).

Also give:
- The time columns: the same columns in every schedule, with the first period in the same column on every sheet.
- The color legend (blue, black, green, red) to put on the `Cover`.
- The checks you suggest, each with its tolerance.
- Anything you are not sure about, as questions.

## Step 3: build the structure (only after approval)

- Create the sheets in order, with a title in A1 and a units marker.
- Add the row labels, the period headers, and the color legend.
- Format number cells `#,##0_);(#,##0);"-"_)`; percentages `0.0%`.
- Leave formulas empty unless the user asks for them. If you add formulas, follow `workbook-standards`.
- List every sheet and range you created.

## Step 4: hand over

Give the user the blueprint table as text to keep with the workbook (for example in the `Cover` notes or in the project `docs/` folder). It is the first version of the model documentation.
