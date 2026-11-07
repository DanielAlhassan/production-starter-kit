import argparse
import os
import re
from pathlib import Path

FILE_MARKER = re.compile(r"^=====\s*FILE:\s*(.+?)\s*=====\s*$", re.MULTILINE)


def main() -> None:
    """Split a Copilot reply into separate files for review.

    Usage (from the repo root): python tools/unpack_files.py <reply.txt> [--out _from_copilot]
    Copy the whole Copilot reply into a text file first. Each block that starts
    with "===== FILE: <path> =====" is written to <out>/<path>. Code fences
    (```) around a block are removed. Files are never written outside <out>,
    so your code does not change: compare each file with the original in
    VS Code, then copy what you accept.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("reply")
    parser.add_argument("--out", default="_from_copilot")
    args = parser.parse_args()

    text = Path(args.reply).read_text(encoding="utf-8")
    markers = list(FILE_MARKER.finditer(text))
    if not markers:
        print(
            "No '===== FILE: <path> =====' lines in the reply. Ask Copilot to use that format."
        )
        return
    out = Path(os.path.realpath(args.out))
    for number, marker in enumerate(markers):
        end = markers[number + 1].start() if number + 1 < len(markers) else len(text)
        lines = text[marker.end() : end].strip("\n").splitlines()
        # The file ends at the first code fence (```) after the marker; text after it is Copilot's prose.
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        fences = [n for n, line in enumerate(lines) if line.strip().startswith("```")]
        lines = lines[: fences[0]] if fences else lines
        relative = marker.group(1).strip().strip("`")
        target = Path(os.path.realpath(out / relative))
        if out not in target.parents:
            print(f"SKIPPED (path outside {args.out}): {relative}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        shown = Path(args.out) / relative
        compare = (
            f'code --diff "{relative}" "{shown}"'
            if Path(relative).is_file()
            else "(new file)"
        )
        print(f"{shown.as_posix()}   {compare}")


if __name__ == "__main__":
    main()
