import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    """Count what the Copilot guardrails did, from the hook audit logs.

    Usage: python summarize_audit.py [repo ...] [--since YYYY-MM-DD]
    Reads <repo>/.copilot-audit/agent_actions.jsonl for each repo (default:
    the current folder) and prints one row per repo plus a total: sessions,
    prompts, tool calls, edits blocked, confirmations asked, Python files
    checked after edits, edit issues caught, finish checks run, and finish
    checks that caught a failure before the agent could say "done".
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("repos", nargs="*", default=["."])
    parser.add_argument("--since", default=None)
    args = parser.parse_args()

    rows = []
    for repo in args.repos:
        log_file = Path(repo) / ".copilot-audit" / "agent_actions.jsonl"
        if not log_file.is_file():
            print(f"No audit log in {repo}")
            continue
        log = pd.read_json(log_file, lines=True)
        log["time_utc"] = pd.to_datetime(log["time_utc"], utc=True)
        if args.since:
            log = log[log["time_utc"] >= pd.Timestamp(args.since, tz="UTC")]
        for column in ("event", "decision", "failures", "session"):
            if column not in log:
                log[column] = None
        tools = log[log["event"] == "tool_call"]
        edits = log[log["event"] == "post_edit_check"]
        stops = log[log["event"] == "stop_check"]
        rows.append(
            {
                "repo": Path(repo).resolve().name,
                "from": log["time_utc"].min().date() if len(log) else None,
                "to": log["time_utc"].max().date() if len(log) else None,
                "sessions": log["session"].nunique(),
                "prompts": int((log["event"] == "prompt").sum()),
                "tool_calls": len(tools),
                "blocked": int((tools["decision"] == "deny").sum()),
                "asked_first": int((tools["decision"] == "ask").sum()),
                "py_files_checked": len(edits),
                "edit_issues_caught": int((edits["failures"].fillna(0) > 0).sum()),
                "finish_checks_run": len(stops),
                "finish_checks_failed": int((stops["failures"].fillna(0) > 0).sum()),
            }
        )

    if not rows:
        return
    table = pd.DataFrame(rows)
    if len(table) > 1:
        total = table.drop(columns=["repo", "from", "to"]).sum()
        table.loc[len(table)] = {
            "repo": "TOTAL",
            "from": table["from"].min(),
            "to": table["to"].max(),
            **total,
        }
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
