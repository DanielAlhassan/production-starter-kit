import argparse
import csv
import re
import subprocess
from datetime import date, timedelta
from pathlib import Path

LOG_FILE = Path("docs/progress_log.md")
UPDATES_FILE = Path.home() / ".copilot" / "updates_given.csv"
UPDATE_COLUMNS = ["date", "audience", "covered_to", "repos", "deck"]
LOG_TEMPLATE = """# Progress log

One file per project, same name in every project. Add lines with:
python ~/.copilot/skills/progress-log/scripts/progress.py add <area> "<what>" --tag done|decision|issue|next

## Current state

- Commit:
- Open items:
- Verified commands:
- Baselines:

## Log

"""


def main() -> None:
    """Keep one progress log per project and scope each update from the last one.

    Usage (run in a project folder unless --repos is given):
      progress.py add <area> "<text>" [--tag done|decision|issue|next]
          Add a dated line to docs/progress_log.md. Creates the file if needed.
      progress.py scope <audience> [--repos A B ...] [--since YYYY-MM-DD]
          Print what is new for this audience since its last update: log lines,
          Git commits, current state, last reconciliation. With no earlier
          update, starts 7 days back.
      progress.py record <audience> [--repos A B ...] [--deck path]
          Write that an update was given today. The next scope starts here.
    Updates for all projects go to ~/.copilot/updates_given.csv, so each
    audience (manager, team) has its own starting point.
    """
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add")
    add.add_argument("area")
    add.add_argument("text")
    add.add_argument(
        "--tag", default="done", choices=["done", "decision", "issue", "next"]
    )
    scope = commands.add_parser("scope")
    scope.add_argument("audience")
    scope.add_argument("--repos", nargs="+", default=["."])
    scope.add_argument("--since")
    record = commands.add_parser("record")
    record.add_argument("audience")
    record.add_argument("--repos", nargs="+", default=["."])
    record.add_argument("--deck", default="")
    args = parser.parse_args()
    today = date.today().isoformat()

    if args.command == "add":
        LOG_FILE.parent.mkdir(exist_ok=True)
        if not LOG_FILE.is_file():
            LOG_FILE.write_text(LOG_TEMPLATE, encoding="utf-8")
        line = f"- {today} | {args.area} | {args.text.strip()} [{args.tag}]\n"
        text = LOG_FILE.read_text(encoding="utf-8")
        LOG_FILE.write_text(
            text if text.endswith("\n") else text + "\n", encoding="utf-8"
        )
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(line)
        print(f"Added to {LOG_FILE}: {line.strip()}")
        return

    if args.command == "record":
        new_file = not UPDATES_FILE.is_file()
        UPDATES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(UPDATES_FILE, "a", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=UPDATE_COLUMNS)
            if new_file:
                writer.writeheader()
            writer.writerow(
                {
                    "date": today,
                    "audience": args.audience.lower(),
                    "covered_to": today,
                    "repos": ";".join(Path(r).resolve().name for r in args.repos),
                    "deck": args.deck,
                }
            )
        print(f"Recorded update for '{args.audience}' on {today} in {UPDATES_FILE}")
        return

    updates = []
    if UPDATES_FILE.is_file():
        with open(UPDATES_FILE, encoding="utf-8", newline="") as source:
            updates = list(csv.DictReader(source))
    past = [u for u in updates if u["audience"] == args.audience.lower()]
    since = args.since or (
        past[-1]["covered_to"]
        if past
        else (date.today() - timedelta(days=7)).isoformat()
    )
    print(f"# Scope for '{args.audience}' since {since}")
    print(
        f"Last update to this audience: {past[-1]['date'] if past else 'none recorded'}\n"
    )
    for repo in args.repos:
        root = Path(repo).resolve()
        print(f"## Project: {root.name}\n")
        log_path = root / LOG_FILE
        text = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
        if "## Current state" in text:
            state = text.split("## Current state", 1)[1].split("\n## ", 1)[0].strip()
            print(f"### Current state\n{state}\n")
        entries = [
            line
            for line in text.splitlines()
            if re.match(r"- \d{4}-\d{2}-\d{2} \|", line) and line[2:12] > since
        ]
        print("### Log since last update")
        print("\n".join(entries) if entries else "(no log lines)")
        commits = subprocess.run(
            [
                "git",
                "log",
                f"--since={since} 23:59",
                "--date=short",
                "--pretty=format:- %ad %h %s",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        print(f"\n### Commits since last update\n{commits or '(no commits)'}")
        recon_runs = sorted((root / "data" / "output" / "recon").glob("*/summary.csv"))
        if recon_runs:
            with open(recon_runs[-1], encoding="utf-8") as summary:
                status = ", ".join(
                    f"{row['name']} {row['status']}" for row in csv.DictReader(summary)
                )
            print(f"\n### Last reconciliation ({recon_runs[-1].parent.name})\n{status}")
        print()


if __name__ == "__main__":
    main()
