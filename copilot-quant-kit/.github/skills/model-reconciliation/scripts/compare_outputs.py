import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def read_table(path: Path, sheet: object = None) -> pd.DataFrame:
    if path.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
        return pd.read_excel(
            path, sheet_name=sheet if isinstance(sheet, str) and sheet else 0
        )
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def compare_pair(pair: dict) -> tuple[dict, pd.DataFrame]:
    summary = {"name": pair["name"], "status": "FAIL", "note": ""}
    base_path, cand_path = Path(pair["baseline"]), Path(pair["candidate"])
    missing = [str(p) for p in (base_path, cand_path) if not p.exists()]
    if missing:
        summary["note"] = f"file not found: {', '.join(missing)}"
        return summary, pd.DataFrame()

    base = read_table(base_path, pair.get("sheet"))
    cand = read_table(cand_path, pair.get("sheet"))
    keys = list(pair["keys"])
    abs_tol = float(pair["abs_tol"])
    rel_tol = float(pair["rel_tol"])

    absent_keys = [k for k in keys if k not in base.columns or k not in cand.columns]
    if absent_keys:
        summary["note"] = f"key columns missing: {', '.join(absent_keys)}"
        return summary, pd.DataFrame()

    dropped = sorted(set(base.columns) - set(cand.columns))
    added = sorted(set(cand.columns) - set(base.columns))
    value_cols = [c for c in base.columns if c in cand.columns and c not in keys]
    merged = base.merge(
        cand, on=keys, how="outer", suffixes=("__base", "__cand"), indicator=True
    )
    both = merged[merged["_merge"] == "both"]

    breaches = []
    for col in value_cols:
        b, c = both[f"{col}__base"], both[f"{col}__cand"]
        one_missing = b.isna() ^ c.isna()
        if pd.api.types.is_numeric_dtype(b) and pd.api.types.is_numeric_dtype(c):
            abs_diff = (c - b).abs()
            # Relative difference is infinite when the baseline is zero and the value moved.
            rel_diff = (abs_diff / b.abs()).where(
                b != 0, np.where(abs_diff > 0, np.inf, 0.0)
            )
            out = one_missing | ((abs_diff > abs_tol) & (rel_diff > rel_tol))
        else:
            abs_diff = rel_diff = pd.Series(np.nan, index=b.index)
            out = one_missing | (
                (b.astype(str) != c.astype(str)) & b.notna() & c.notna()
            )
        if out.any():
            rows = both.loc[out, keys].copy()
            rows["column"] = col
            rows["baseline"] = b[out]
            rows["candidate"] = c[out]
            rows["abs_diff"] = abs_diff[out]
            rows["rel_diff"] = rel_diff[out]
            breaches.append(rows)

    detail = pd.concat(breaches, ignore_index=True) if breaches else pd.DataFrame()
    summary.update(
        {
            "rows_baseline": len(base),
            "rows_candidate": len(cand),
            "only_in_baseline": int((merged["_merge"] == "left_only").sum()),
            "only_in_candidate": int((merged["_merge"] == "right_only").sum()),
            "duplicate_keys": int(
                base.duplicated(keys).sum() + cand.duplicated(keys).sum()
            ),
            "values_compared": len(both) * len(value_cols),
            "breaches": len(detail),
            "max_abs_diff": float(detail["abs_diff"].max())
            if len(detail) and detail["abs_diff"].notna().any()
            else 0.0,
            "columns_dropped": ";".join(map(str, dropped)),
            "columns_added": ";".join(map(str, added)),
        }
    )
    failed = (
        summary["breaches"]
        or summary["only_in_baseline"]
        or summary["only_in_candidate"]
    )
    failed = failed or summary["duplicate_keys"] or dropped
    summary["status"] = "FAIL" if failed else "PASS"
    if len(detail):
        detail.insert(0, "name", pair["name"])
    return summary, detail


def main() -> None:
    """Compare candidate model outputs with baseline outputs, value by value.

    Usage: python compare_outputs.py settings/recon.yaml
    Each entry in `pairs` names one output: name, baseline, candidate, keys,
    abs_tol, rel_tol, and an optional sheet. A value breaches only when it
    exceeds both abs_tol and rel_tol. Writes summary.csv and breaches.csv to
    <results_dir>/<timestamp>/, prints the summary, and exits with 1 if any
    pair fails. Paths are relative to the repo root.
    """
    config = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
    results = [compare_pair(pair) for pair in config["pairs"]]
    summary = pd.DataFrame([r[0] for r in results])
    details = [r[1] for r in results if len(r[1])]
    detail = pd.concat(details, ignore_index=True) if details else pd.DataFrame()

    out_dir = Path(config["results_dir"]) / datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_dir / "summary.csv", index=False)
    detail.to_csv(out_dir / "breaches.csv", index=False)

    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(
            summary.drop(columns=["columns_added"], errors="ignore").to_string(
                index=False
            )
        )
        if len(detail):
            print(
                f"\nFirst breaches (all {len(detail)} in {out_dir / 'breaches.csv'}):"
            )
            print(detail.head(15).to_string(index=False))
    print(f"\nResults: {out_dir}")
    sys.exit(1 if (summary["status"] == "FAIL").any() else 0)


if __name__ == "__main__":
    main()
