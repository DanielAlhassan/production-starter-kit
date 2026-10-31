# <Model name>: model documentation

| Item | Value |
|---|---|
| Model | |
| Package (if any) | |
| Owner | |
| Version (Git commit) | |
| Last updated | |
| Upstream models | |
| Downstream models | |

## 1. Purpose and scope

What the module calculates, for which use, and what it does not cover.

## 2. Inputs

Files in `data/input/`.

| Input | Source | Owner | Frequency | Key columns | Input controls |
|---|---|---|---|---|---|

## 3. Methodology

The calculation in plain words, then the formulas. One subsection per calc step, in run order.

## 4. Assets and settings

Methodology files in `assets/` and run values in `settings/`. Mark each row as asset or setting.

| Item | Asset or setting | File and key | Value | Reason | Who approves a change |
|---|---|---|---|---|---|

## 5. Implementation and run steps

1. Folder layout: `data/`, `assets/`, `settings/`, `src/` (`run.py` and step files), `assembly/` (`driver.py`, `switchboard.py`) for a package.
2. Run order: what `run()` calls, in order. For a package, how the switchboard selects enabled models.
3. Environment: Python version and packages.
4. Command to run (for example `python -m assembly.driver`).
5. Outputs in `data/output/` and the run record.

## 6. Controls

| Control | Type (input / implementation / output) | What it checks | Threshold | Action on FAIL |
|---|---|---|---|---|

## 7. Assumptions and limitations

| Assumption or limitation | Reason | Impact | Mitigation |
|---|---|---|---|

## 8. Testing and reconciliation

Unit tests (what they cover), reconciliation against the baseline (pairs, tolerances, last result), and sensitivity checks.

## 9. Change log

| Date | Commit | Change | Reason | Numeric impact (reconciliation result) | Author | Reviewer |
|---|---|---|---|---|---|---|
