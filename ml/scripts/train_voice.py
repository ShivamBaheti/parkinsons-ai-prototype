"""Evaluate voice models (evaluation only; does not save a model).

Data: ItalianPVS sustained vowel /a/ (VA), 9 features from backend/app/features/voice_features.py.
Rows are recordings (1-2 per person); every split is by person (StratifiedGroupKFold), repeated 20x
with different shuffles. Scaling happens inside the pipeline, so it is fitted on training folds only.
Models and settings were fixed before running; nothing is tuned on the evaluation folds.
"""
import warnings
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.features.voice_features import FEATURE_NAMES  # noqa: E402

warnings.filterwarnings("ignore")
CSV = Path(__file__).resolve().parents[1] / "data" / "processed" / "voice_features.csv"
REPEATS = 20


def models():
    return {
        "logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000)),
        "random_forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=3, class_weight="balanced", random_state=0, n_jobs=-1),
    }


def evaluate(model, X, y, groups, repeats=REPEATS):
    """Out-of-fold predictions with person-level folds. Returns mean/sd of metrics across repeats + mean confusion matrix."""
    rows, cms = [], []
    for seed in range(repeats):
        proba = np.zeros(len(y))
        for tr, te in StratifiedGroupKFold(5, shuffle=True, random_state=seed).split(X, y, groups):
            assert not set(groups[tr]) & set(groups[te])  # no person on both sides
            proba[te] = model.fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
        pred = proba >= 0.5
        tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
        rows.append({"auc": roc_auc_score(y, proba), "sens": tp / (tp + fn), "spec": tn / (tn + fp)})
        cms.append([[tn, fp], [fn, tp]])
    r = pd.DataFrame(rows)
    return r.mean(), r.std(), np.mean(cms, axis=0)


def report(title, d, pos, neg):
    d = d[d.group.isin([pos, neg])]
    X, y, g = d[FEATURE_NAMES].to_numpy(), (d.group == pos).astype(int).to_numpy(), d.subject.to_numpy()
    n_pos, n_neg = d[d.group == pos].subject.nunique(), d[d.group == neg].subject.nunique()
    print(f"\n== {title}: {pos} ({n_pos} people) vs {neg} ({n_neg} people), {len(d)} recordings")
    for name, m in models().items():
        mean, sd, cm = evaluate(m, X, y, g)
        print(f"  {name:20s} AUC {mean.auc:.3f} (sd {sd.auc:.3f}) | sens {mean.sens:.3f} | spec {mean.spec:.3f} | mean confusion [[TN FP],[FN TP]] {np.round(cm, 1).tolist()}")


if __name__ == "__main__":
    df = pd.read_csv(CSV)
    va = df[df.task == "VA"].copy()
    print(f"Vowel /a/ recordings: {len(va)}; features: {FEATURE_NAMES}")
    print("Metrics are means over", REPEATS, "repeats of person-level 5-fold CV; sd is across repeats (not a confidence interval).")

    report("A. all PD vs elderly controls", va, "pd", "elderly_hc")
    pd16 = va[(va.group != "pd") | (va.sr_orig == 16000)]
    report("B. PD recorded at 16 kHz only vs elderly controls", pd16, "pd", "elderly_hc")

    # C. recording-condition check inside the PD group: can features tell the 44.1 kHz sessions from the 16 kHz ones?
    pdv = va[va.group == "pd"].copy()
    pdv["group"] = np.where(pdv.sr_orig == 44100, "pd_44k", "pd_16k")
    report("C. recording-condition check inside PD", pdv, "pd_44k", "pd_16k")
    print("\nIf C is far above AUC 0.5, the features carry the recording session/device, not only the person's voice.")
