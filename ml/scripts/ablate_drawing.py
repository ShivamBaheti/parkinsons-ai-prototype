"""Does the drawing model depend on protocol-like features (turns drawn, duration, path length)?

Re-runs the same repeated stratified 5-fold CV as train_drawing.py on feature subsets.
No tuning, no selection: the subsets are fixed in advance and every result is reported.
"""
import warnings
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.features.drawing_features import FEATURE_NAMES  # noqa: E402
from train_drawing import models, score  # noqa: E402

warnings.filterwarnings("ignore")
df = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "processed" / "drawing_features.csv")
train = df[df.group.isin(["control", "pd_hw"])]
y = train.label.to_numpy()

PROTOCOL = ["turns", "duration_s", "path_length"]
subsets = {
    "all 13 features": FEATURE_NAMES,
    "without turns": [f for f in FEATURE_NAMES if f != "turns"],
    "without turns, duration, path_length": [f for f in FEATURE_NAMES if f not in PROTOCOL],
    "only turns, duration, path_length": PROTOCOL,
}
for name, feats in subsets.items():
    res, cm = score(models()["random_forest"], train[feats].to_numpy(), y)
    m = res.mean()
    print(f"{name:40s} AUC {m.auc:.3f} | sens {m.sens:.3f} | spec {m.spec:.3f}")
