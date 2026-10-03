"""Extract motion features from the PADS dataset into one small CSV.

Run this locally on the downloaded dataset, then share the CSV:
    python extract_motion_features.py <path/to/pads_dataset> [--tasks Relaxed StretchHold] [--limit 20]

Reads  movement/timeseries/<id>_<Task>_<Left|Right>Wrist.txt  (comma-separated, no header assumed;
columns: Accelerometer X,Y,Z [g], Gyroscope X,Y,Z [rad/s]; 100 Hz, per the dataset description)
and    patients/patient_<id>.json  (condition, age, gender).
Writes ml/data/processed/motion_features.csv (one row per subject x task x wrist).
Uses the same feature code as the live API (backend/app/features/motion_features.py).
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.features.motion_features import extract_features  # noqa: E402

SAMPLE_RATE = 100.0
NAME = re.compile(r"^(\d+)_(.+)_(Left|Right)Wrist\.txt$")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--tasks", nargs="+", default=["Relaxed", "StretchHold"])
    ap.add_argument("--limit", type=int, default=None, help="only the first N subjects (quick test)")
    args = ap.parse_args()

    ts_dir = args.root / "movement" / "timeseries"
    files = sorted(ts_dir.glob("*.txt"))
    if not files:
        sys.exit(f"No .txt files found in {ts_dir}")
    found = sorted({m.group(2) for f in files if (m := NAME.match(f.name))})
    print("Tasks found in the data:", ", ".join(found))
    if not set(args.tasks) & set(found):
        sys.exit(f"None of --tasks {args.tasks} exist. Choose from the list above.")

    patients = {}
    for p in (args.root / "patients").glob("patient_*.json"):
        d = json.loads(p.read_text())
        patients[d["id"].zfill(3)] = d
    print("Condition counts:", pd.Series([d.get("condition") for d in patients.values()]).value_counts().to_dict())

    subjects = sorted({NAME.match(f.name).group(1) for f in files if NAME.match(f.name)})
    if args.limit:
        subjects = subjects[: args.limit]
    wanted = set(subjects)

    rows, failed = [], 0
    for f in files:
        m = NAME.match(f.name)
        if not m or m.group(1) not in wanted or m.group(2) not in args.tasks:
            continue
        sid, task, wrist = m.groups()
        try:
            raw = pd.read_csv(f, header=None).apply(pd.to_numeric, errors="coerce").dropna().to_numpy()
            if raw.shape[1] != 6:
                raise ValueError(f"expected 6 columns, found {raw.shape[1]}")
            t = np.arange(len(raw)) / SAMPLE_RATE
            feats = extract_features(raw[:, :3], raw[:, 3:], t)
        except Exception as err:  # keep going; report at the end
            failed += 1
            print(f"  skipped {f.name}: {err}")
            continue
        info = patients.get(sid.zfill(3), {})
        rows.append({"subject": sid, "task": task, "wrist": wrist, "condition": info.get("condition"),
                     "age": info.get("age"), "gender": info.get("gender"), **feats})

    out = Path(__file__).resolve().parents[1] / "data" / "processed" / "motion_features.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out, index=False)
    print(f"\nWrote {len(df)} rows ({df.subject.nunique() if len(df) else 0} subjects) to {out}; {failed} files skipped.")


if __name__ == "__main__":
    main()
