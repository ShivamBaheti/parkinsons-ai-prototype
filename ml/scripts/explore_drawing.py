"""Profile the UCI spiral-drawing dataset (id 395). Usage: python explore_drawing.py <dataset_dir>"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

COLS = ["x", "y", "z", "pressure", "grip_angle", "t", "test"]
GROUPS = {"hw_control": "hw_dataset/control", "hw_parkinson": "hw_dataset/parkinson",
          "new_parkinson": "new_dataset/parkinson"}


def load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", header=None, names=COLS)


def main(root: Path) -> None:
    rows = []
    for group, rel in GROUPS.items():
        for f in sorted((root / rel).glob("*.txt")):
            df = load(f)
            for test, d in df.groupby("test"):
                dt = np.diff(d["t"].to_numpy())
                rows.append(dict(group=group, file=f.name, test=int(test), n=len(d),
                                 dur=(d.t.iloc[-1] - d.t.iloc[0]), dt_med=np.median(dt) if len(dt) else np.nan,
                                 dt_nonmono=int((dt < 0).sum()), x_min=d.x.min(), x_max=d.x.max(),
                                 y_min=d.y.min(), y_max=d.y.max(), p_max=d.pressure.max(),
                                 p_zero=float((d.pressure == 0).mean())))
    s = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print("files per group:\n", s.groupby("group").file.nunique(), "\n")
    print("tests present per group (files having each test):\n",
          s.pivot_table(index="group", columns="test", values="file", aggfunc="nunique"), "\n")
    print("points per test (median / min / max):\n",
          s.groupby(["group", "test"]).n.agg(["median", "min", "max"]), "\n")
    print("duration (raw timestamp units) per test, median:\n",
          s.groupby(["group", "test"]).dur.median().unstack(), "\n")
    print("median sample interval (raw units):", s.dt_med.median(), " non-monotonic steps:", s.dt_nonmono.sum())
    print("x range:", s.x_min.min(), s.x_max.max(), " y range:", s.y_min.min(), s.y_max.max())
    print("share of samples with zero pressure, by group:\n", s.groupby("group").p_zero.mean())
    s.to_csv("/tmp/drawing_profile.csv", index=False)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
