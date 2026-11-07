from openpyxl.cell.cell import Cell
from openpyxl.formula import Tokenizer
from openpyxl.worksheet.worksheet import Worksheet


def read_formula(cell: Cell) -> str:
    value = cell.value
    text = value.text if hasattr(value, "text") else value
    return text if isinstance(text, str) and text.startswith("=") else ""


def classify_cell(cell: Cell) -> str:
    # input = typed-in number; sheet_link / file_link = formula that uses another sheet / file.
    formula = read_formula(cell)
    if formula:
        if "[" in formula:
            return "file_link"
        ranges = [
            t.value
            for t in Tokenizer(formula).items
            if t.type == "OPERAND" and t.subtype == "RANGE"
        ]
        return "sheet_link" if any("!" in r for r in ranges) else "formula"
    if isinstance(cell.value, (int, float)) and not isinstance(cell.value, bool):
        return "input"
    return "text" if cell.value is not None else "empty"


def find_label(sheet: Worksheet, row: int) -> str:
    for column in range(1, 6):
        value = sheet.cell(row=row, column=column).value
        if isinstance(value, str) and not value.startswith("="):
            return value.strip()
    return ""
