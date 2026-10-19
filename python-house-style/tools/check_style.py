"""Check Python files against the team house style.

Flags: banned or discouraged words in names, comments and docstrings;
single-use underscore helpers; thin wrappers around one call; missing
type hints; docstrings on helpers; public functions without docstrings.

Usage: python check_style.py [file_or_folder ...]   (default: current folder)
Exits with status 1 if anything is flagged.
"""
import ast
import io
import re
import sys
import tokenize
from collections import Counter
from pathlib import Path

BANNED = re.compile(r"validat|resolv|normali[sz]|ensur|handl", re.I)
DISCOURAGED = re.compile(r"load|util|helper|impl|internal", re.I)
BANNED_IN_TEXT = re.compile(r"\b(?:validat|resolv|normali[sz]|ensur|handl)\w*", re.I)
SKIP_FOLDERS = {"venv", "__pycache__", "build", "dist"}


def split_name(name: str) -> list[str]:
    words = []
    for part in name.split("_"):
        words += re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", part)
    return [w.lower() for w in words]


def check_name(node: ast.AST, name: str, kind: str, add) -> None:
    words = split_name(name)
    if any(BANNED.search(w) for w in words):
        add(node, f"{kind} '{name}' uses a banned word")
    elif any(DISCOURAGED.match(w) for w in words):
        add(node, f"{kind} '{name}' uses a discouraged word")


def check_function(fn: ast.FunctionDef, refs: Counter, add) -> None:
    name = fn.name
    check_name(fn, name, "function", add)
    all_args = fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs
    for arg in all_args:
        check_name(arg, arg.arg, "argument", add)
    if name.startswith("__") and name.endswith("__"):
        return

    hinted = [a for a in all_args if a.arg not in ("self", "cls")]
    hinted += [a for a in (fn.args.vararg, fn.args.kwarg) if a is not None]
    missing = [a.arg for a in hinted if a.annotation is None]
    if missing:
        add(fn, f"'{name}' is missing type hints for: {', '.join(missing)}")
    if fn.returns is None:
        add(fn, f"'{name}' is missing a return type hint")

    doc = ast.get_docstring(fn)
    if name.startswith("_"):
        if doc:
            add(fn, f"helper '{name}' has a docstring; use a one-line comment if needed")
        if refs[name] < 2:
            add(fn, f"helper '{name}' is used {refs[name]} time(s); inline it")
    elif not doc:
        add(fn, f"public function '{name}' has no docstring")

    body = fn.body[1:] if doc else fn.body
    if (len(body) == 1 and isinstance(body[0], (ast.Return, ast.Expr))
            and isinstance(body[0].value, ast.Call)):
        add(fn, f"'{name}' only wraps a single call; call it directly")


def check_tree(path: Path, tree: ast.Module, refs: Counter) -> list[tuple]:
    issues = []
    seen_variables = set()

    def add(node, message):
        issues.append((str(path), node.lineno, message))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            check_function(node, refs, add)
        elif isinstance(node, ast.ClassDef):
            check_name(node, node.name, "class", add)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id not in seen_variables:
                seen_variables.add(node.id)
                check_name(node, node.id, "variable", add)
    return issues


def check_comments(path: Path, source: str) -> list[tuple]:
    issues = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            is_block_string = (tok.type == tokenize.STRING
                               and tok.string.lstrip("rbuRBUfF")[:3] in ('"""', "'''"))
            if tok.type == tokenize.COMMENT or is_block_string:
                for match in BANNED_IN_TEXT.finditer(tok.string):
                    issues.append((str(path), tok.start[0],
                                   f"banned word '{match.group()}' in comment or docstring"))
    except tokenize.TokenError:
        pass
    return issues


def find_python_files(args: list[str]) -> list[Path]:
    files = []
    for root in [Path(a) for a in args] or [Path(".")]:
        if root.is_file():
            files.append(root)
            continue
        for p in root.rglob("*.py"):
            if not any(part.startswith(".") or part in SKIP_FOLDERS for part in p.parts):
                files.append(p)
    return files


def main(args: list[str]) -> int:
    parsed = {}
    for path in find_python_files(args):
        source = path.read_text(encoding="utf-8")
        try:
            parsed[path] = (source, ast.parse(source))
        except SyntaxError as err:
            print(f"{path}:{err.lineno}: could not parse")

    # count every reference to a name across all files, to spot single-use helpers
    refs = Counter()
    for _, tree in parsed.values():
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                refs[node.id] += 1
            elif isinstance(node, ast.Attribute):
                refs[node.attr] += 1

    issues = []
    for path, (source, tree) in parsed.items():
        issues += check_tree(path, tree, refs)
        issues += check_comments(path, source)

    for file, line, message in sorted(issues):
        print(f"{file}:{line}: {message}")
    print(f"{len(issues)} issue(s) in {len(parsed)} file(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
