"""Fit the final drawing model on all 40 hw_dataset subjects and save it with real metadata.

Usage: python save_drawing_model.py        (reads ml/data/processed/drawing_features.csv,
                                            which train_drawing.py writes)

The model type (random forest) was chosen in train_drawing.py. The metrics stored in the
metadata are recomputed here with the same repeated stratified 5-fold CV, so they are the real
cross-validated numbers for exactly this model, not typed in by hand.
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.features.drawing_features import FEATURE_NAMES  # noqa: E402
from train_drawing import models, score  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "ml" / "data" / "processed" / "drawing_features.csv"
OUT = ROOT / "backend" / "models"


def main() -> None:
    df = pd.read_csv(CSV)
    train = df[df.group.isin(["control", "pd_hw"])]  # new_dataset is PD-only: never used for training
    assert train.subject.is_unique
    X, y = train[FEATURE_NAMES].to_numpy(), train.label.to_numpy()

    res, cm = score(models()["random_forest"], X, y)
    m, s = res.mean(), res.std()
    model = models()["random_forest"].fit(X, y)

    importances = sorted(zip(FEATURE_NAMES, model.feature_importances_), key=lambda kv: -kv[1])
    metadata = {
        "model": "RandomForestClassifier (300 trees, min_samples_leaf=2, class_weight=balanced)",
        "dataset": "UCI Parkinson Disease Spiral Drawings Using Digitized Graphics Tablet (id 395), hw_dataset, static spiral test",
        "n_subjects": int(len(train)),
        "class_counts": {"control": int((y == 0).sum()), "parkinson": int((y == 1).sum())},
        "features": FEATURE_NAMES,
        "evaluation": {
            "method": "repeated stratified 5-fold CV x20, one row per subject (subject-level), threshold 0.5",
            "roc_auc": round(float(m.auc), 3),
            "sensitivity": round(float(m.sens), 3),
            "specificity": round(float(m.spec), 3),
            "spread_across_repeats_sd": {"roc_auc": round(float(s.auc), 3), "sensitivity": round(float(s.sens), 3), "specificity": round(float(s.spec), 3)},
            "mean_confusion_matrix_TN_FP_FN_TP": np.round(cm, 1).tolist(),
        },
        "feature_importance": [{"feature": f, "importance": round(float(v), 3)} for f, v in importances],
        "caveats": [
            "Only 40 subjects; one control is worth about 7 points of specificity.",
            "Model chosen among 3 candidates on the same CV, so the numbers are mildly optimistic.",
            "PD and control recordings are dated to different sessions, so a recording-session effect cannot be ruled out.",
            "Trained on stylus-on-tablet data; mouse/finger drawings on a web canvas are a domain shift that has NOT been validated.",
            "Spiral frame for the web canvas is approximate.",
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUT / "drawing_model.pkl")
    (OUT / "drawing_model.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved model + metadata to {OUT}")
    print(json.dumps(metadata["evaluation"], indent=2))


if __name__ == "__main__":
    main()
