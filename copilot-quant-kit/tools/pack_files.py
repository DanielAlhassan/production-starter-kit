import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from openpyxl import load_workbook


def collect_files(
    entries: list[str], types: list[str], skip: set[str]
) -> tuple[list[Path], list[str]]:
    found, missing = [], []
    for entry in entries:
        path = Path(entry)
        if path.is_file():
            found.append(path)
        elif path.is_dir():
            found += sorted(
                p
                for p in path.rglob("*")
                if p.is_file() and p.suffix.lower() in types and not skip & set(p.parts)
            )
        else:
            missing.append(entry)
    return found, missing


def main() -> None:
    """Pack the code, settings, data samples, and house rules for one task into one text file for M365 Copilot.

    Usage (from the repo root): python tools/pack_files.py bundles/<name>.yaml
    The spec lists the task, the code (files or folders), and the data (files or
    folders). bundles/bundle_settings.yaml gives the rules files, data mode, size
    limit, and output folder for every bundle; a spec can change any of them.
    Each file in the bundle starts with "===== FILE: <path> =====", the same
    marker Copilot uses in its reply, so tools/unpack_files.py can split it.
    Notebooks are added as cells without outputs. Data files are added as row
    count, columns, types, and (data_mode: sample) the first rows.
    Writes <out_folder>/<name>_bundle.txt. The repo files do not change.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    settings = yaml.safe_load(
        (spec_path.parent / "bundle_settings.yaml").read_text(encoding="utf-8")
    )
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    settings.update({k: v for k, v in spec.items() if k in settings})
    skip = set(settings["skip_folders"])
    text_types = [t.lower() for t in settings["text_types"]]
    data_types = [t.lower() for t in settings["data_types"]]

    rules, missing_rules = collect_files(settings["rules"], text_types, skip)
    code, missing_code = collect_files(spec.get("code", []), text_types, skip)
    data, missing_data = collect_files(spec.get("data", []), data_types, skip)
    missing = missing_rules + missing_code + missing_data

    sections = []
    for title, files in (("RULES", rules), ("CODE", code)):
        sections.append(f"===== SECTION: {title} =====\n")
        for path in files:
            text = path.read_text(encoding="utf-8", errors="replace")
            if path.suffix.lower() == ".ipynb":
                cells = json.loads(text)["cells"]
                text = "\n\n".join(
                    f"# --- {cell['cell_type']} cell {number} ---\n"
                    + "".join(cell["source"])
                    for number, cell in enumerate(cells, start=1)
                )
            sections.append(f"===== FILE: {path.as_posix()} =====\n{text.rstrip()}\n")

    sections.append("===== SECTION: DATA =====\n")
    rows = int(settings["data_rows"])
    for path in data:
        suffix = path.suffix.lower()
        if suffix in (".xlsx", ".xlsm", ".xls"):
            book = load_workbook(path, read_only=True) if suffix != ".xls" else None
            frames = pd.read_excel(path, sheet_name=None, nrows=1000)
            counts = {s: (book[s].max_row or 1) - 1 for s in frames} if book else {}
        elif suffix == ".parquet":
            frame = pd.read_parquet(path)
            frames, counts = {"": frame.head(1000)}, {"": len(frame)}
        else:
            frames = {"": pd.read_csv(path, nrows=1000, low_memory=False)}
            with open(path, encoding="utf-8", errors="replace") as source:
                counts = {"": sum(1 for _ in source) - 1}
        for sheet, frame in frames.items():
            label = f"{path.as_posix()} [sheet: {sheet}]" if sheet else path.as_posix()
            columns = "\n".join(
                f"| {name} | {dtype} |"
                for name, dtype in frame.dtypes.astype(str).items()
            )
            block = f"===== DATA: {label} =====\nRows: {counts.get(sheet, 'unknown')}   Columns: {frame.shape[1]}\n\n| Column | Type |\n|---|---|\n{columns}\n"
            if settings["data_mode"] == "sample":
                block += f"\nFirst {min(rows, len(frame))} rows (CSV):\n{frame.head(rows).to_csv(index=False)}"
            sections.append(block)

    tree = "\n".join(
        f"- {p.as_posix()} ({p.stat().st_size:,} bytes)" for p in rules + code + data
    )
    header = (
        f"# Bundle: {spec['name']}\n\nMade {datetime.now().astimezone():%Y-%m-%d} from repo folder {Path.cwd().name}.\n\n"
        f"## Task\n\n{spec.get('task', '(no task given)').strip()}\n\n"
        "## How to read this bundle\n\n"
        "- Section RULES: the house rules. Follow them exactly.\n"
        "- Section CODE: each file starts with a line '===== FILE: <path> ====='.\n"
        f"- Section DATA: row count, columns, and types of each input{' and the first rows' if settings['data_mode'] == 'sample' else ''}.\n"
        "- Answer with complete files, each starting with '===== FILE: <path> =====', inside a code block.\n\n"
        f"## Files in this bundle\n\n{tree}\n"
    )
    if missing:
        header += (
            "\n## Not found (not in this bundle)\n\n"
            + "\n".join(f"- {m}" for m in missing)
            + "\n"
        )
    text = header + "\n" + "\n".join(sections)

    out = Path(settings["out_folder"]) / f"{spec['name']}_bundle.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(
        f"Bundle: {out}   {len(rules)} rules, {len(code)} code, {len(data)} data files   {len(text):,} characters"
    )
    for entry in missing:
        print(f"WARNING not found: {entry}")
    if missing_rules:
        print(
            "WARNING house rules missing: Copilot will not see them. Check 'rules' in bundle_settings.yaml."
        )
    if len(text) > settings["max_chars"]:
        print(
            f"WARNING bundle is over {settings['max_chars']:,} characters. Split the spec, or set data_mode: schema."
        )


if __name__ == "__main__":
    main()
