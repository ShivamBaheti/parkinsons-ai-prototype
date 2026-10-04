"""Fit the final voice model on all 50 people (28 PD, 22 elderly HC), sustained vowel /a/, and save it.

Logistic regression was chosen over random forest because it had the higher cross-validated AUC in
train_voice.py (both were fixed in advance; the choice was made on the same CV, so it is mildly optimistic).
The model is saved flagged as UNRELIABLE: see the caveats and TODO.md.
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.features.voice_features import FEATURE_NAMES  # noqa: E402
from train_voice import CSV, evaluate, models  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "backend" / "models"


def main() -> None:
    df = pd.read_csv(CSV)
    d = df[(df.task == "VA") & df.group.isin(["pd", "elderly_hc"])]
    X, y, g = d[FEATURE_NAMES].to_numpy(), (d.group == "pd").astype(int).to_numpy(), d.subject.to_numpy()

    mean, sd, cm = evaluate(models()["logistic_regression"], X, y, g)
    model = models()["logistic_regression"].fit(X, y)
    coefs = model[-1].coef_[0]  # features are standardised, so coefficient sizes are comparable
    imp = sorted(zip(FEATURE_NAMES, coefs), key=lambda kv: -abs(kv[1]))

    metadata = {
        "model": "StandardScaler + LogisticRegression (C=1, class_weight=balanced)",
        "reliable": False,
        "dataset": "ItalianPVS (Dimauro & Girardi, IEEE DataPort), sustained vowel /a/, PD vs elderly healthy controls",
        "n_subjects": int(d.subject.nunique()),
        "n_recordings": int(len(d)),
        "class_counts": {"control": int(d[d.group == "elderly_hc"].subject.nunique()), "parkinson": int(d[d.group == "pd"].subject.nunique())},
        "features": FEATURE_NAMES,
        "evaluation": {
            "method": "repeated person-level (StratifiedGroupKFold) 5-fold CV x20, threshold 0.5",
            "roc_auc": round(float(mean.auc), 3),
            "sensitivity": round(float(mean.sens), 3),
            "specificity": round(float(mean.spec), 3),
            "spread_across_repeats_sd": {"roc_auc": round(float(sd.auc), 3), "sensitivity": round(float(sd.sens), 3), "specificity": round(float(sd.spec), 3)},
            "mean_confusion_matrix_TN_FP_FN_TP": np.round(cm, 1).tolist(),
        },
        "feature_importance": [{"feature": f, "importance": round(float(abs(c)), 3), "direction": "higher in PD" if c > 0 else "lower in PD"} for f, c in imp],
        "caveats": [
            "The score is probably driven by how the recordings were made, not by disease: Parkinson's recordings have about half the shimmer and higher HNR than the healthy controls, which is the opposite of the clinical expectation.",
            "Healthy controls and patients appear to have been recorded with different setups (silence before the voice, different sample rates and lengths), and this dataset cannot test that.",
            "Only 50 people; no external validation yet.",
            "Not validated for browser or phone microphones.",
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUT / "voice_model.pkl")
    (OUT / "voice_model.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("Saved voice model + metadata to", OUT)
    print(json.dumps(metadata["evaluation"], indent=2))


if __name__ == "__main__":
    main()
