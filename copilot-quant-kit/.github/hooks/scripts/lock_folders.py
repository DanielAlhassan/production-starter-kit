import stat
import sys
from pathlib import Path

from hook_common import read_policy


def main() -> None:
    """Set or clear the read-only flag on every file in the protected folders.

    Usage: python lock_folders.py lock|unlock [repo folder]
    The folders come from readonly_folders in hook_policy.json (inputs,
    assets, baselines). With the flag set, an edit by Copilot or by a script
    fails. To change a file on purpose: unlock, change it, lock again. Files
    added later are not locked until the next lock.
    """
    if len(sys.argv) < 2 or sys.argv[1] not in ("lock", "unlock"):
        sys.exit("Usage: python lock_folders.py lock|unlock [repo folder]")
    lock = sys.argv[1] == "lock"
    root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path()
    policy = read_policy()

    for folder in policy["readonly_folders"]:
        files = [p for p in (root / folder).rglob("*") if p.is_file()]
        for path in files:
            mode = path.stat().st_mode
            path.chmod(
                mode & ~stat.S_IWRITE & ~stat.S_IWGRP & ~stat.S_IWOTH
                if lock
                else mode | stat.S_IWRITE
            )
        print(f"{'Locked' if lock else 'Unlocked'} {len(files)} files in {folder}")


if __name__ == "__main__":
    main()
