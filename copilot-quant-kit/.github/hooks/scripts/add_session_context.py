import csv
import sys
from pathlib import Path

from hook_common import print_output, read_event, read_policy, write_audit


def main() -> None:
    """Give a new session the project state in a few lines (SessionStart hook).

    Sends the "Current state" section of the project handoff file and the
    status of the last reconciliation. Both are capped in policy, so the cost
    per session stays small. Sends nothing if the project has neither.
    """
    event = read_event()
    policy = read_policy()
    root = Path(event.get("cwd") or ".")
    lines = []

    handoff = next(
        (root / f for f in policy["handoff_files"] if (root / f).is_file()), None
    )
    if handoff:
        text = handoff.read_text(encoding="utf-8")
        heading = policy["handoff_heading"]
        if heading in text:
            section = text.split(heading, 1)[1].split("\n## ", 1)[0].strip()
            lines.append(
                f"Project state from {handoff.relative_to(root).as_posix()}:\n{section}"
            )

    recon_dir = root / policy["recon_results_dir"]
    runs = (
        sorted(p for p in recon_dir.glob("*/summary.csv")) if recon_dir.is_dir() else []
    )
    if runs:
        with open(runs[-1], encoding="utf-8") as summary:
            status = ", ".join(
                f"{row['name']} {row['status']}" for row in csv.DictReader(summary)
            )
        lines.append(f"Last reconciliation ({runs[-1].parent.name}): {status}")

    write_audit(
        policy, event, {"event": "session_start", "context_chars": sum(map(len, lines))}
    )
    if not lines:
        print_output("SessionStart", {})
        return
    context = "\n\n".join(lines)[: policy["handoff_max_chars"]]
    print_output("SessionStart", {"additionalContext": context})


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001
        print(f"add_session_context error: {error}", file=sys.stderr)
        print("{}")
