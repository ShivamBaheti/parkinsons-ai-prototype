
"""Evaluate voice models and save metrics to CSV.

Uses repeated person-level stratified 5-fold cross-validation.
Scaling is fitted inside each training fold.

Outputs:
    ml/results/voice_comparison.csv
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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.features.voice_features import FEATURE_NAMES  # noqa: E402

warnings.filterwarnings("ignore")

CSV = PROJECT_ROOT / "ml" / "data" / "processed" / "voice_features.csv"
OUTPUT = PROJECT_ROOT / "ml" / "results" / "voice_comparison.csv"

REPEATS = 20


def models():
    return {
        "logistic_regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=1.0,
                class_weight="balanced",
                max_iter=1000,
            ),
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=0,
            n_jobs=-1,
        ),
    }


def evaluate(model, X, y, groups, repeats=REPEATS):
    """Return repeated CV metrics and mean confusion matrix."""
    rows = []
    cms = []

    for seed in range(repeats):
        proba = np.zeros(len(y))

        cv = StratifiedGroupKFold(
            n_splits=5,
            shuffle=True,
            random_state=seed,
        )

        for tr, te in cv.split(X, y, groups):
            assert not set(groups[tr]) & set(groups[te])

            model.fit(X[tr], y[tr])
            proba[te] = model.predict_proba(X[te])[:, 1]

        pred = (proba >= 0.5).astype(int)
        tn, fp, fn, tp = confusion_matrix(
            y, pred, labels=[0, 1]
        ).ravel()

        rows.append({
            "roc_auc": roc_auc_score(y, proba),
            "sensitivity": tp / (tp + fn) if tp + fn else np.nan,
            "specificity": tn / (tn + fp) if tn + fp else np.nan,
        })

        cms.append([[tn, fp], [fn, tp]])

    metrics = pd.DataFrame(rows)

    summary = {
        "roc_auc_mean": metrics["roc_auc"].mean(),
        "roc_auc_sd": metrics["roc_auc"].std(),
        "sensitivity_mean": metrics["sensitivity"].mean(),
        "specificity_mean": metrics["specificity"].mean(),
        "tn_mean": np.mean(cms, axis=0)[0, 0],
        "fp_mean": np.mean(cms, axis=0)[0, 1],
        "fn_mean": np.mean(cms, axis=0)[1, 0],
        "tp_mean": np.mean(cms, axis=0)[1, 1],
    }

    return summary


def evaluate_scenario(title, data, positive, negative):
    subset = data[data["group"].isin([positive, negative])].copy()

    if subset.empty:
        raise ValueError(f"No data available for scenario: {title}")

    X = subset[FEATURE_NAMES].to_numpy()
    y = (subset["group"] == positive).astype(int).to_numpy()
    groups = subset["subject"].to_numpy()

    positive_people = subset.loc[
        subset["group"] == positive, "subject"
    ].nunique()
    negative_people = subset.loc[
        subset["group"] == negative, "subject"
    ].nunique()

    print(
        f"\n{title}: {positive} ({positive_people} people) "
        f"vs {negative} ({negative_people} people)"
    )

    rows = []

    for name, model in models().items():
        metrics = evaluate(model, X, y, groups)

        row = {
            "scenario": title,
            "model": name,
            "positive_group": positive,
            "negative_group": negative,
            "positive_people": positive_people,
            "negative_people": negative_people,
            "recordings": len(subset),
            **metrics,
        }
        rows.append(row)

        print(
            f"  {name:20s} "
            f"AUC {metrics['roc_auc_mean']:.3f} "
            f"(SD {metrics['roc_auc_sd']:.3f}) | "
            f"sens {metrics['sensitivity_mean']:.3f} | "
            f"spec {metrics['specificity_mean']:.3f}"
        )

    return rows


def main():
    if not CSV.exists():
        raise FileNotFoundError(f"Dataset not found: {CSV}")

    df = pd.read_csv(CSV)
    va = df[df["task"] == "VA"].copy()

    print(f"Voice recordings: {len(va)}")
    print(f"Features: {FEATURE_NAMES}")
    print(f"Cross-validation repeats: {REPEATS}")

    all_results = []

    # A. All PD recordings vs elderly healthy controls
    all_results += evaluate_scenario(
        "A_all_PD_vs_elderly_controls",
        va,
        "pd",
        "elderly_hc",
    )

    # B. PD recordings restricted to 16 kHz vs elderly controls
    pd16 = va[(va["group"] != "pd") | (va["sr_orig"] == 16000)]
    all_results += evaluate_scenario(
        "B_PD_16k_vs_elderly_controls",
        pd16,
        "pd",
        "elderly_hc",
    )

    # C. Recording-condition check within the PD group
    pdv = va[va["group"] == "pd"].copy()
    pdv["group"] = np.where(
        pdv["sr_orig"] == 44100,
        "pd_44k",
        "pd_16k",
    )

    all_results += evaluate_scenario(
        "C_recording_condition_check",
        pdv,
        "pd_44k",
        "pd_16k",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(OUTPUT, index=False)

    print(f"\nResults saved to:\n{OUTPUT}")
    print(f"CSV rows: {len(results_df)}")


if __name__ == "__main__":
    main()
