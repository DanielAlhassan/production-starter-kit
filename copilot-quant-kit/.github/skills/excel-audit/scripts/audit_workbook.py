import argparse
import csv
import re
import sys
from copy import copy
from pathlib import Path

import openpyxl
import yaml
from openpyxl.formula import Tokenizer
from openpyxl.formula.translate import Translator
from openpyxl.styles.colors import Color
from openpyxl.utils import get_column_letter

from excel_common import classify_cell, find_label, read_formula

ERROR_VALUES = {"#REF!", "#N/A", "#DIV/0!", "#VALUE!", "#NAME?", "#NUM!", "#NULL!"}
WHOLE_COLUMN = re.compile(r"(^|!)\$?[A-Z]{1,3}:\$?[A-Z]{1,3}$")
LOOKUPS = {"VLOOKUP", "HLOOKUP", "MATCH", "XLOOKUP", "INDEX", "LOOKUP"}


def main() -> None:
    """Check an Excel workbook against excel_rules.yaml and report every rule it breaks.

    Usage: python audit_workbook.py <workbook.xlsx> [--profile data_prep recon model]
                                    [--rules path] [--out report.csv] [--fix-colors]
    Core rules always apply; --profile adds the rules of each named profile.
    The script checks the rules marked "check: script" and lists the rules
    only Copilot can judge. It never changes the workbook. --fix-colors writes
    a copy (<name>_colors_fixed.xlsx) with font colors set by cell type and no
    other change. Exit code 1 if a high-severity rule is broken.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook")
    parser.add_argument(
        "--profile", nargs="*", default=[], choices=["data_prep", "recon", "model"]
    )
    parser.add_argument(
        "--rules",
        default=str(Path(__file__).resolve().parent.parent / "excel_rules.yaml"),
    )
    parser.add_argument("--out")
    parser.add_argument("--fix-colors", action="store_true")
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.rules).read_text(encoding="utf-8"))
    profiles = {"core", *args.profile}
    rules = {r["id"]: r for r in config["rules"] if profiles & set(r["profiles"])}
    colors = config["colors"]
    allowed = {float(n) for n in config["allowed_constants"]}
    volatile = {f.upper() for f in config["volatile_functions"]}
    path = Path(args.workbook)
    book = openpyxl.load_workbook(path, keep_vba=path.suffix.lower() == ".xlsm")
    values = openpyxl.load_workbook(path, data_only=True)
    findings = []

    def add(rule: str, sheet: str, cell: str, detail: str) -> None:
        if rule in rules:
            findings.append(
                {
                    "rule": rule,
                    "severity": rules[rule]["severity"],
                    "sheet": sheet,
                    "cell": cell,
                    "detail": detail,
                }
            )

    for sheet in book.worksheets:
        name = sheet.title
        raw = any(word in name.lower() for word in config["raw_sheet_words"])
        if sheet.sheet_state != "visible":
            add("C07", name, "", f"sheet is {sheet.sheet_state}")
        for merged in sheet.merged_cells.ranges:
            add("C06", name, str(merged), "merged cells")

        for row in sheet.iter_rows():
            for cell in row:
                kind = classify_cell(cell)
                if kind in ("empty", "text"):
                    continue
                address = cell.coordinate
                cached = values[name][address].value
                if isinstance(cached, str) and cached in ERROR_VALUES:
                    add("C04", name, address, cached)

                if not raw:
                    expected = colors["sheet_link" if kind == "sheet_link" else kind]
                    color = cell.font.color
                    actual = (
                        color.rgb[-6:].upper()
                        if color is not None and color.type == "rgb"
                        else "000000"
                    )
                    if actual not in expected:
                        add(
                            "C01",
                            name,
                            address,
                            f"{kind} has font {actual}, expected {expected[0]}",
                        )
                        if args.fix_colors:
                            font = copy(cell.font)
                            font.color = Color(rgb="FF" + expected[0])
                            cell.font = font
                if (
                    "model" in profiles
                    and kind != "text"
                    and any(s in (cell.number_format or "") for s in "$€£")
                ):
                    add(
                        "M01",
                        name,
                        address,
                        f"currency symbol in format {cell.number_format}",
                    )

                formula = read_formula(cell)
                if not formula:
                    continue
                if kind == "file_link":
                    add("C05", name, address, formula[:80])
                if "#REF!" in formula:
                    add("C04", name, address, "#REF! in formula")

                # Walk the formula tokens: numbers, volatile functions, whole columns, lookup arguments.
                frames = []
                for token in Tokenizer(formula).items:
                    if token.type == "OPERAND":
                        if frames:
                            frames[-1]["last"] += token.value
                        if (
                            token.subtype == "NUMBER"
                            and not raw
                            and float(token.value) not in allowed
                        ):
                            add(
                                "C02",
                                name,
                                address,
                                f"number {token.value} in {formula[:80]}",
                            )
                        if token.subtype == "RANGE" and WHOLE_COLUMN.search(
                            token.value
                        ):
                            add("C09", name, address, token.value)
                    elif token.type == "FUNC" and token.subtype == "OPEN":
                        function = token.value.rstrip("(").upper().replace("_XLFN.", "")
                        if function in volatile:
                            add("C08", name, address, function)
                        frames.append(
                            {"name": function, "args": 1, "last": "", "lookup": False}
                        )
                    elif token.type == "SEP" and token.subtype == "ARG" and frames:
                        frames[-1]["args"] += 1
                        frames[-1]["last"] = ""
                    elif token.type == "FUNC" and token.subtype == "CLOSE" and frames:
                        frame = frames.pop()
                        last = frame["last"].strip().upper()
                        if frame["name"] in ("VLOOKUP", "HLOOKUP"):
                            add("D03", name, address, frame["name"])
                            if frame["args"] < 4 or last in ("TRUE", "1"):
                                add(
                                    "D01",
                                    name,
                                    address,
                                    f"{frame['name']} without exact match",
                                )
                        if frame["name"] == "MATCH" and (
                            frame["args"] < 3 or last not in ("0", "FALSE")
                        ):
                            add("D01", name, address, "MATCH without match type 0")
                        if frame["name"] in ("IFERROR", "IFNA") and frame["lookup"]:
                            add(
                                "D02", name, address, f"{frame['name']} around a lookup"
                            )
                        if frames and (frame["lookup"] or frame["name"] in LOOKUPS):
                            frames[-1]["lookup"] = True

        # One odd formula between two neighbors that agree with each other: a break in the pattern.
        for cell in (c for row in sheet.iter_rows() for c in row if read_formula(c)):
            for before, after in (((0, -1), (0, 1)), ((-1, 0), (1, 0))):
                r1, c1 = cell.row + before[0], cell.column + before[1]
                r2, c2 = cell.row + after[0], cell.column + after[1]
                if min(r1, c1) < 1:
                    continue
                first = read_formula(sheet.cell(row=r1, column=c1))
                last = read_formula(sheet.cell(row=r2, column=c2))
                if not first or not last:
                    continue
                origin = f"{get_column_letter(c1)}{r1}"
                pattern = Translator(first, origin=origin)
                if pattern.translate_formula(
                    f"{get_column_letter(c2)}{r2}"
                ) == last and pattern.translate_formula(
                    cell.coordinate
                ) != read_formula(cell):
                    label = find_label(sheet, cell.row)
                    add(
                        "C03",
                        name,
                        cell.coordinate,
                        f"differs from neighbors{f' (row: {label})' if label else ''}: {read_formula(cell)[:80]}",
                    )

    by_rule = {}
    for finding in findings:
        by_rule.setdefault(finding["rule"], []).append(finding)
    print(f"Workbook: {path.name}   Profiles: {', '.join(sorted(profiles))}")
    print(
        f"Findings: {len(findings)} ({sum(f['severity'] == 'high' for f in findings)} high)\n"
    )
    for rule_id in sorted(
        by_rule, key=lambda r: ("high", "medium", "low").index(rules[r]["severity"])
    ):
        items = by_rule[rule_id]
        print(
            f"[{rule_id}] {rules[rule_id]['severity'].upper()}  {rules[rule_id]['rule']}"
        )
        for item in items[:10]:
            print(f"    {item['sheet']}!{item['cell']}  {item['detail']}")
        if len(items) > 10:
            print(f"    ... and {len(items) - 10} more")
        print(f"    Fix: {rules[rule_id]['fix']}\n")
    manual = [r for r in rules.values() if r["check"] == "copilot"]
    print(
        "Not checked by this script (ask @workbook-audit in Excel): "
        + ", ".join(r["id"] for r in manual)
    )

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(
                target, fieldnames=["rule", "severity", "sheet", "cell", "detail"]
            )
            writer.writeheader()
            writer.writerows(findings)
        print(f"Report: {args.out}")
    if args.fix_colors:
        fixed = path.with_name(f"{path.stem}_colors_fixed{path.suffix}")
        book.save(fixed)
        print(
            f"Colors fixed in a copy: {fixed}. Open it and check charts, pivots, and macros; the original is unchanged."
        )
    sys.exit(1 if any(f["severity"] == "high" for f in findings) else 0)


if __name__ == "__main__":
    main()
