import subprocess
import sys
from fnmatch import fnmatch

from hook_common import read_policy, run_checks, write_audit


def main() -> None:
    """Check staged changes before a Git commit (Git pre-commit hook).

    Works without Copilot hooks. For each staged Python file, runs the
    commit_file_checks from hook_policy.json (ruff, house style; check only,
    no file changes). If a staged file matches high_risk_paths (model code,
    assembly, settings), also runs the stop_checks: tests, the model run, and
    the output reconciliation. Any failure stops the commit. Staged Excel
    files get commit_xlsx_checks (the workbook audit) as warnings only. Each result goes
    to the audit log. To skip once on purpose: git commit --no-verify.
    """
    policy = read_policy()
    root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()

    failures = []
    for path in staged:
        if path.endswith(".py"):
            failures.extend(run_checks(policy["commit_file_checks"], root, path))
    warnings = []
    for path in staged:
        if path.lower().endswith((".xlsx", ".xlsm")):
            warnings.extend(
                run_checks(policy.get("commit_xlsx_checks", []), root, path)
            )
    high_risk = [
        p
        for p in staged
        if any(fnmatch(p, pattern) for pattern in policy["high_risk_paths"])
    ]
    if high_risk:
        print(
            f"High-risk change ({', '.join(high_risk[:5])}): running tests, model, reconciliation..."
        )
        failures.extend(run_checks(policy["stop_checks"], root))
    protected = [
        p
        for p in staged
        if any(fnmatch(p, pattern) for pattern in policy["protected_paths"])
    ]

    write_audit(
        policy,
        {"cwd": root, "sessionId": "git-commit"},
        {
            "event": "commit_check",
            "staged": len(staged),
            "high_risk": bool(high_risk),
            "failures": len(failures),
            "excel_warnings": len(warnings),
        },
    )
    for path in protected:
        print(
            f"NOTE protected file in this commit: {path}. Commit it only if a person changed it on purpose."
        )
    for warning in warnings:
        print(
            f"WARNING (does not stop the commit):\n{warning[-policy['max_report_chars'] :]}"
        )
    if failures:
        print("\n\n".join(failures)[-policy["max_report_chars"] :])
        sys.exit("\nCommit stopped: fix the failures above, then commit again.")
    print(
        f"Commit checks passed ({len(staged)} files, {'full' if high_risk else 'file-only'} checks)."
    )


if __name__ == "__main__":
    main()
