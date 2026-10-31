import hashlib
import json
import sys
from pathlib import Path

from hook_common import (
    extract_paths,
    read_event,
    read_policy,
    run_checks,
    write_audit,
)


def main() -> None:
    """Format and lint each Python file the agent just changed (postToolUse hook).

    Runs the post_edit_checks from hook_policy.json on every edited .py file,
    records the file for the stop checks, and sends any remaining problems
    back to the agent so it fixes them in the same turn.
    """
    event = read_event()
    policy = read_policy()
    tool = str(event.get("toolName", event.get("tool_name", ""))).lower()
    root = Path(event.get("cwd") or ".")
    if not any(word in tool for word in policy["edit_tool_words"]):
        print("{}")
        return

    py_files = [
        p for p in extract_paths(event) if p.endswith(".py") and (root / p).is_file()
    ]
    if not py_files:
        print("{}")
        return

    session = event.get("sessionId", event.get("session_id", "default"))
    edited_log = root / policy["audit_dir"] / f"edited_{session}.txt"
    edited_log.parent.mkdir(exist_ok=True)
    with open(edited_log, "a", encoding="utf-8") as log:
        log.writelines(f"{p}\n" for p in py_files)

    notes = []
    for path in py_files:
        before = hashlib.sha256((root / path).read_bytes()).hexdigest()
        failures = run_checks(policy["post_edit_checks"], str(root), path)
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != before:
            notes.append(
                f"{path} was reformatted by ruff. Read it again before the next edit."
            )
        notes.extend(failures)
        write_audit(
            policy,
            event,
            {"event": "post_edit_check", "path": path, "failures": len(failures)},
        )

    if not notes:
        print("{}")
        return
    report = "\n\n".join(notes)[: policy["max_report_chars"]]
    print(
        json.dumps(
            {
                "additionalContext": f"Post-edit checks:\n{report}\nFix every error before you continue."
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        print(f"check_python_edit error: {error}", file=sys.stderr)
        print("{}")
