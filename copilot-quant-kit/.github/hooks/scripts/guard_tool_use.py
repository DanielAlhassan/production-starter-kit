import json
import re
import sys
from fnmatch import fnmatch

from hook_common import (
    extract_paths,
    read_event,
    read_policy,
    read_tool_args,
    write_audit,
)


def main() -> None:
    """Decide if the agent can run a tool call (preToolUse hook).

    Denies edits to protected paths and risky shell commands, asks before
    commands that change the repo, and writes every call to the audit log.
    Prints "{}" when it has no decision, so normal approvals still apply.
    """
    event = read_event()
    policy = read_policy()
    tool = str(event.get("toolName", event.get("tool_name", ""))).lower()
    paths = extract_paths(event)
    command = str(read_tool_args(event).get("command", ""))
    is_edit = any(word in tool for word in policy["edit_tool_words"])
    is_shell = any(word in tool for word in policy["shell_tool_words"])

    decision = {}
    protected = [
        p
        for p in paths
        if any(fnmatch(p, pattern) for pattern in policy["protected_paths"])
    ]
    if is_edit and protected:
        decision = {
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Protected path: {', '.join(protected)}. "
            "Inputs, baselines, Excel files, and guardrail files are changed only by a person. "
            "Write output to a new file or ask the user.",
        }
    elif is_shell and any(
        re.search(p, command, re.IGNORECASE) for p in policy["blocked_commands"]
    ):
        decision = {
            "permissionDecision": "deny",
            "permissionDecisionReason": "Blocked command (push, hard reset, recursive delete, or network call). "
            "Tell the user the command and why you need it. The user runs it.",
        }
    elif is_shell and any(
        re.search(p, command, re.IGNORECASE) for p in policy["confirm_commands"]
    ):
        decision = {
            "permissionDecision": "ask",
            "permissionDecisionReason": "This command changes the environment or Git history. Confirm first.",
        }

    write_audit(
        policy,
        event,
        {
            "event": "tool_call",
            "tool": tool,
            "paths": paths,
            "command": command[:300],
            "decision": decision.get("permissionDecision", "default"),
        },
    )
    print(json.dumps(decision))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        # A crash here would deny every tool call (preToolUse fails closed), so fall back to normal approvals.
        print(f"guard_tool_use error: {error}", file=sys.stderr)
        print("{}")
