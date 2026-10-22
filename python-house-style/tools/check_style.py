"""Check Python files against the house style.

Usage: python tools/check_style.py [file_or_folder ...]
Banned words, avoided words, generic names and naming verbs come from
tools/house_style_terms.csv, the single source of truth for the word rules.
Exits with code 1 when any ERROR is found. WARN lines need a look, not always a fix.
"""

from __future__ import annotations

import ast
import csv
import io
import re
import sys
import tokenize
from collections import Counter
from pathlib import Path

Issue = tuple[Path, int, str, str]


def split_name(name: str) -> str:
    # snake_case and camelCase both become lowercase words separated by spaces
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    return " ".join(part.lower() for part in re.split(r"[_\s]+", spaced) if part)


def find_flagged_words(text: str, terms: dict[str, dict[str, str]]) -> list[tuple[str, str]]:
    found = []
    for word in re.findall(r"[A-Za-z]+", text):
        lowered = word.lower()
        for term, use_instead in terms.get("banned", {}).items():
            # a banned term also catches its other forms (noun, past tense, -or)
            if lowered.startswith(term.rstrip("e")):
                found.append(("ERROR", f"banned word '{word}', use {use_instead}"))
        for term, use_instead in terms.get("avoid", {}).items():
            if re.fullmatch(rf"{term}(s|ed|er|ing)?", lowered):
                found.append(("WARN", f"avoid '{word}', use {use_instead}"))
    return found


def check_file(  # house-style: step
    path: Path,
    terms: dict[str, dict[str, str]],
    issues: list[Issue],
    definitions: dict[str, list[tuple[Path, int, bool, bool]]],
    references: Counter[str],
) -> None:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    lines = source.splitlines()
    generic_names = terms.get("generic", {})
    file_references: Counter[str] = Counter()

    if path.stem in generic_names:
        issues.append((path, 1, "ERROR", f"generic module name '{path.stem}', name it after what it does"))

    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            for severity, message in find_flagged_words(token.string, terms):
                issues.append((path, token.start[0], severity, f"comment: {message}"))

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            file_references[node.id] += 1
        elif isinstance(node, ast.Attribute):
            file_references[node.attr] += 1
    references.update(file_references)

    for statement in tree.body:
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
            continue
        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
        for target in targets:
            if not (isinstance(target, ast.Name) and target.id.isupper()):
                continue
            if file_references[target.id] <= 1:
                issues.append((path, statement.lineno, "WARN", f"constant '{target.id}' is used once or never, inline it"))
            value = statement.value
            if isinstance(value, (ast.List, ast.Tuple, ast.Set)) and len(value.elts) > 5 or isinstance(value, ast.Dict) and len(value.keys) > 5:
                issues.append((path, statement.lineno, "WARN", f"'{target.id}' is a lookup table in code, move it to an asset file (Excel or CSV) the code reads"))

    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node, clean=False)
            if docstring:
                for severity, message in find_flagged_words(docstring, terms):
                    issues.append((path, node.body[0].lineno, severity, f"docstring: {message}"))

        named = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            named.append(node.name)
        elif isinstance(node, ast.arg):
            named.append(node.arg)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            named.append(node.id)
        for name in named:
            for severity, message in find_flagged_words(split_name(name), terms):
                issues.append((path, node.lineno, severity, f"name '{name}': {message}"))
            if name.strip("_").lower() in generic_names:
                issues.append((path, node.lineno, "WARN", f"generic name '{name}', say what it holds"))

        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Lambda):
            issues.append((path, node.lineno, "ERROR", "lambda assigned to a name, inline it or write a def"))

        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                issues.append((path, node.lineno, "ERROR", "bare except hides the real error, name the exception"))
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                issues.append((path, node.lineno, "ERROR", "except: pass swallows the error, raise or log with context"))

        if isinstance(node, ast.Call):
            for keyword in node.keywords:
                if keyword.arg == "inplace":
                    issues.append((path, node.lineno, "WARN", "inplace=True changes data out of sight, assign the result"))

        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        name = node.name
        is_dunder = name.startswith("__") and name.endswith("__")
        # a function called inside its own file is internal; one that is not is an entry function
        is_internal = file_references[name] > 0 and name != "main"
        docstring = ast.get_docstring(node)

        for child in ast.walk(node):
            if child is not node and isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                issues.append((path, child.lineno, "ERROR", f"nested function '{child.name}' inside '{name}', move it to module level or inline it"))

        for argument in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
            if argument.annotation is None and argument.arg not in {"self", "cls"}:
                issues.append((path, node.lineno, "ERROR", f"'{name}': argument '{argument.arg}' has no type hint"))
        if node.returns is None:
            issues.append((path, node.lineno, "ERROR", f"'{name}': no return type hint"))
        if node.args.kwarg is not None:
            issues.append((path, node.lineno, "WARN", f"'{name}': **{node.args.kwarg.arg} hides what is passed, list the arguments"))

        if not is_dunder and name != "main":
            words = split_name(name).split()
            if len(words) < 2:
                issues.append((path, node.lineno, "ERROR", f"one-word name '{name}', use verb + domain noun"))
            elif words[0] not in terms.get("verb", {}) and not find_flagged_words(words[0], terms):
                issues.append((path, node.lineno, "WARN", f"'{name}' does not start with a verb from the terms file"))
        if name.startswith("_") and not is_dunder:
            issues.append((path, node.lineno, "WARN", f"leading underscore on '{name}' is rare, drop it unless this is internal plumbing"))

        if not is_dunder and not name.startswith("test"):
            if is_internal and docstring:
                issues.append((path, node.lineno, "WARN", f"internal function '{name}' gets no docstring, only entry functions do"))
            if not is_internal and docstring is None:
                issues.append((path, node.lineno, "WARN", f"entry function '{name}' needs a docstring: what it does, inputs, outputs"))
            if docstring and len(docstring.splitlines()) > 12:
                issues.append((path, node.lineno, "WARN", f"docstring on '{name}' is over 12 lines, tighten it"))

        body = node.body[1:] if docstring else node.body
        if not node.decorator_list and len(body) == 1 and isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.Call):
            issues.append((path, node.lineno, "ERROR", f"'{name}' only wraps one call, call it directly where it is used"))

        if not is_dunder and name != "main" and not name.startswith("test"):
            is_step = "house-style: step" in lines[node.lineno - 1]
            definitions.setdefault(name, []).append((path, node.lineno, is_step, name.startswith("_")))


def main() -> int:
    """Check every file or folder given on the command line."""
    # terms file: {kind: {term: use_instead}}, kinds are banned, avoid, generic, verb
    terms: dict[str, dict[str, str]] = {}
    with Path(__file__).with_name("house_style_terms.csv").open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            terms.setdefault(row["kind"], {})[row["term"].lower()] = row["use_instead"]
    targets = [Path(arg) for arg in sys.argv[1:]] or [Path(".")]
    files = sorted({
        file
        for target in targets
        for file in (target.rglob("*.py") if target.is_dir() else [target])
        if not {".venv", "venv", "site-packages", "__pycache__", ".git", "build", "dist"}.intersection(file.parts)
    })

    issues: list[Issue] = []
    definitions: dict[str, list[tuple[Path, int, bool, bool]]] = {}
    references: Counter[str] = Counter()
    for file in files:
        try:
            check_file(file, terms, issues, definitions, references)
        except SyntaxError as error:
            issues.append((file, error.lineno or 1, "ERROR", f"syntax error: {error.msg}"))

    for name, places in definitions.items():
        if len(places) > 1:
            where = ", ".join(f"{path}:{line}" for path, line, _, _ in places)
            for path, line, _, _ in places:
                issues.append((path, line, "WARN", f"'{name}' is defined in {len(places)} places ({where}), merge into one"))
        uses = references[name]
        for path, line, is_step, is_private in places:
            if is_step:
                continue
            if is_private and uses <= 1:
                issues.append((path, line, "ERROR", f"helper '{name}' is used {uses} time(s), inline it"))
            elif uses == 1:
                issues.append((path, line, "WARN", f"'{name}' is used once in the checked files, inline it or mark the def line '# house-style: step'"))

    for path, line, severity, message in sorted(issues, key=lambda issue: (str(issue[0]), issue[1])):
        print(f"{path}:{line}: {severity} {message}")
    error_count = sum(issue[2] == "ERROR" for issue in issues)
    print(f"\n{len(files)} file(s) checked: {error_count} error(s), {len(issues) - error_count} warning(s)")
    return 1 if error_count else 0


if __name__ == "__main__":
    sys.exit(main())
