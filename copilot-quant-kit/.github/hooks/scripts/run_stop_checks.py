import json
import sys
from pathlib import Path

from hook_common import read_event, read_policy, run_checks, write_audit


def main() -> None:
    """Run tests and output reconciliation before the agent can finish (agentStop hook).

    Runs only when the agent edited Python files in this session. If a check
    fails, the agent gets another turn with the failure output. After
    max_stop_retries failed attempts, the agent must report the failure to the
    user and stop, so a stuck fix loop does not burn credits.
    """
    event = read_event()
    policy = read_policy()
    root = Path(event.get("cwd") or ".")
    session = event.get("sessionId", event.get("session_id", "default"))
    audit_dir = root / policy["audit_dir"]
    edited_log = audit_dir / f"edited_{session}.txt"
    retry_file = audit_dir / f"stop_retries_{session}.txt"

    if not edited_log.exists():
        print("{}")
        return

    retries = int(retry_file.read_text()) if retry_file.exists() else 0
    if retries > policy["max_stop_retries"]:
        retry_file.unlink()
        print("{}")
        return

    edited = sorted(set(edited_log.read_text(encoding="utf-8").split()))
    failures = run_checks(policy["stop_checks"], str(root))
    write_audit(
        policy,
        event,
        {
            "event": "stop_check",
            "edited": edited,
            "failures": len(failures),
            "attempt": retries + 1,
        },
    )

    if not failures:
        edited_log.unlink()
        retry_file.unlink(missing_ok=True)
        print("{}")
        return

    retry_file.write_text(str(retries + 1))
    report = "\n\n".join(failures)[-policy["max_report_chars"] :]
    if retries == policy["max_stop_retries"]:
        reason = (
            "Checks still fail after several attempts. Do not change more code. "
            "Tell the user which checks fail, the likely cause, and what you tried.\n"
            + report
        )
    else:
        reason = (
            "Checks failed before you finished. Find the cause and fix it. "
            "Do not loosen tests, tolerances, or baselines to make them pass.\n"
            + report
        )
    print(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        print(f"run_stop_checks error: {error}", file=sys.stderr)
        print("{}")
