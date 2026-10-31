import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

POLICY_FILE = Path(__file__).with_name("hook_policy.json")


def read_event() -> dict:
    raw = sys.stdin.read()
    return json.loads(raw) if raw.strip() else {}


def read_policy() -> dict:
    return json.loads(POLICY_FILE.read_text(encoding="utf-8"))


def read_tool_args(event: dict) -> dict:
    args = event.get("toolArgs", event.get("tool_input", {}))
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            return {"raw": args}
    return args if isinstance(args, dict) else {}


def extract_paths(event: dict) -> list[str]:
    # Tools name their path arguments differently and can nest them (multi-file edits),
    # so walk all arguments and also read the file headers of apply_patch text.
    root = Path(event.get("cwd") or ".").resolve()
    path_keys = {
        "path",
        "filepath",
        "file_path",
        "filename",
        "target",
        "paths",
        "files",
        "uri",
    }
    found = []
    stack = [read_tool_args(event)]
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(item)
            continue
        if not isinstance(item, dict):
            continue
        for key, value in item.items():
            if key.lower() in path_keys:
                found.extend(value if isinstance(value, list) else [value])
            elif isinstance(value, (dict, list)):
                stack.append(value)
            elif isinstance(value, str) and "*** " in value:
                for line in value.splitlines():
                    for marker in (
                        "*** Update File: ",
                        "*** Add File: ",
                        "*** Delete File: ",
                    ):
                        if line.startswith(marker):
                            found.append(line[len(marker) :].strip())
    paths = []
    for item in found:
        if not isinstance(item, str) or not item:
            continue
        path = Path(item.removeprefix("file://"))
        path = path if path.is_absolute() else root / path
        try:
            paths.append(path.resolve().relative_to(root).as_posix())
        except ValueError:
            paths.append(path.resolve().as_posix())
    return paths


def print_output(event_name: str, fields: dict) -> None:
    # The Copilot harness reads top-level fields. The Local harness reads hookSpecificOutput.
    # Send both, so the same script works in either session target.
    if not fields:
        print("{}")
        return
    print(
        json.dumps(
            {**fields, "hookSpecificOutput": {"hookEventName": event_name, **fields}}
        )
    )


def write_audit(policy: dict, event: dict, record: dict) -> None:
    audit_dir = Path(event.get("cwd") or ".") / policy["audit_dir"]
    audit_dir.mkdir(exist_ok=True)
    record = {
        "time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session": event.get("sessionId", event.get("session_id", "")),
        **record,
    }
    with open(audit_dir / "agent_actions.jsonl", "a", encoding="utf-8") as log:
        log.write(json.dumps(record) + "\n")


def run_checks(checks: list[dict], cwd: str, path: str = "") -> list[str]:
    # A check is skipped when a when_path_exists file (one path or a list) or its executable is missing.
    # "~" in a command or path means the user folder, for checks that live at user level.
    failures = []
    root = Path(cwd or ".")
    for check in checks:
        required = check.get("when_path_exists", [])
        required = [required] if isinstance(required, str) else required
        if not all((root / Path(r).expanduser()).exists() for r in required):
            continue
        parts = [
            str(Path(part).expanduser()) if part.startswith("~") else part
            for part in shlex.split(check["command"].replace("{path}", path))
        ]
        if parts[0] == "python":
            parts[0] = sys.executable
        try:
            result = subprocess.run(
                parts,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=check.get("timeout_sec", 120),
                check=False,
            )
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            failures.append(
                f"[{check['name']}] stopped after {check.get('timeout_sec', 120)} s"
            )
            continue
        if result.returncode not in check.get("pass_exit_codes", [0]):
            failures.append(
                f"[{check['name']}] exit {result.returncode}\n{result.stdout}{result.stderr}".strip()
            )
    return failures
