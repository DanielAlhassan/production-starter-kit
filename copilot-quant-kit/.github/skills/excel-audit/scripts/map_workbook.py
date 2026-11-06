import argparse
import re
from pathlib import Path

import openpyxl
from openpyxl.formula.translate import Translator
from openpyxl.utils import get_column_letter

from excel_common import classify_cell, find_label, read_formula

SHEET_REF = re.compile(r"(?<![#\w.])(?:'([^']+)'|([A-Za-z0-9_\.]+))!")


def main() -> None:
    """Write a formula map of an Excel workbook: what each row calculates and where data flows.

    Usage: python map_workbook.py <workbook.xlsx> [--out map.md]
    For each sheet, repeated formulas along a row are shown once as a range
    (for example C5:N5 =B5*(1+$C$2)), with the row label and the cell type.
    The map ends with the links between sheets. Output is Markdown, to the
    screen or to --out. The workbook is not changed.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook")
    parser.add_argument("--out")
    args = parser.parse_args()

    book = openpyxl.load_workbook(args.workbook)
    lines = [f"# Formula map: {Path(args.workbook).name}", ""]
    links = {}

    for sheet in book.worksheets:
        counts = {"input": 0, "formula": 0, "sheet_link": 0, "file_link": 0}
        blocks = []
        for row in sheet.iter_rows():
            run = None
            for cell in row:
                kind = classify_cell(cell)
                if kind in counts:
                    counts[kind] += 1
                formula = read_formula(cell)
                for match in SHEET_REF.finditer(formula):
                    target = match.group(1) or match.group(2)
                    if target != sheet.title:
                        links[(target, sheet.title)] = (
                            links.get((target, sheet.title), 0) + 1
                        )
                if not formula:
                    if run:
                        blocks.append(run)
                    run = None
                    continue
                # Extend the run if this cell is the run's first formula copied across.
                if (
                    run
                    and run["end"] == cell.column - 1
                    and Translator(
                        run["formula"], origin=run["origin"]
                    ).translate_formula(cell.coordinate)
                    == formula
                ):
                    run["end"] = cell.column
                    continue
                if run:
                    blocks.append(run)
                run = {
                    "row": cell.row,
                    "start": cell.column,
                    "end": cell.column,
                    "formula": formula,
                    "origin": cell.coordinate,
                    "kind": kind,
                }
            if run:
                blocks.append(run)

        state = "" if sheet.sheet_state == "visible" else f" ({sheet.sheet_state})"
        lines += [
            f"## {sheet.title}{state}",
            "",
            f"Inputs: {counts['input']}  Formulas: {counts['formula']}  Links to other sheets: {counts['sheet_link']}  Links to other files: {counts['file_link']}",
            "",
        ]
        if blocks:
            lines += [
                "| Row | Label | Cells | Type | Formula |",
                "|---|---|---|---|---|",
            ]
            for block in blocks:
                cells = (
                    block["origin"]
                    if block["start"] == block["end"]
                    else f"{block['origin']}:{get_column_letter(block['end'])}{block['row']}"
                )
                formula = block["formula"].replace("|", "\\|")
                lines.append(
                    f"| {block['row']} | {find_label(sheet, block['row'])} | {cells} | {block['kind']} | `{formula}` |"
                )
            lines.append("")

    lines += ["## Links between sheets", ""]
    if links:
        lines += ["| From | To | Formulas |", "|---|---|---|"]
        lines += [
            f"| {source} | {target} | {count} |"
            for (source, target), count in sorted(links.items())
        ]
    else:
        lines.append("(no links between sheets)")
    text = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Formula map: {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
