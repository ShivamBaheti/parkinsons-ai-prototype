
"""Evaluate whether drawing-model performance depends on protocol-like features.

Re-runs repeated stratified 5-fold CV using the same scoring function as
train_drawing.py on predefined feature subsets.

No tuning or feature selection is performed. All results are reported
to the terminal and saved to ml/results/drawing_ablation.csv.
"""

import warnings
from pathlib import Path
import sys

import pandas as pd

# Configure project imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.features.drawing_features import FEATURE_NAMES  # noqa: E402
from train_drawing import models, score  # noqa: E402

warnings.filterwarnings("ignore")

# Input dataset
DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "drawing_features.csv"
)

# Output CSV
OUTPUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "results"
    / "drawing_ablation.csv"
)


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Drawing features dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    # Use the same training groups as the original drawing evaluation
    train = df[df["group"].isin(["control", "pd_hw"])].copy()

    if train.empty:
        raise ValueError(
            "No training rows found for groups 'control' and 'pd_hw'."
        )

    y = train["label"].to_numpy()

    # Protocol-like features
    protocol_features = ["turns", "duration_s", "path_length"]

    # Predefined feature subsets
    subsets = {
        "all 13 features": FEATURE_NAMES,
        "without turns": [
            f for f in FEATURE_NAMES if f != "turns"
        ],
        "without turns, duration, path_length": [
            f for f in FEATURE_NAMES if f not in protocol_features
        ],
        "only turns, duration, path_length": protocol_features,
    }

    results = []
    model = models()["random_forest"]

    print("Drawing Model Feature Ablation")
    print(f"Dataset: {DATA_PATH}")
    print(f"Training rows: {len(train)}")
    print(f"Unique participants: {train['subject'].nunique()}")
    print("\nEvaluation results:\n")

    for name, features in subsets.items():
        missing = [f for f in features if f not in train.columns]
        if missing:
            raise ValueError(
                f"Missing features for '{name}': {missing}"
            )

        res, _ = score(
            model,
            train[features].to_numpy(),
            y,
        )

        metrics = res.mean()

        row = {
            "feature_set": name,
            "num_features": len(features),
            "roc_auc_mean": float(metrics["auc"]),
            "sensitivity_mean": float(metrics["sens"]),
            "specificity_mean": float(metrics["spec"]),
        }
        results.append(row)

        print(
            f"{name:40s} "
            f"AUC {row['roc_auc_mean']:.3f} | "
            f"sens {row['sensitivity_mean']:.3f} | "
            f"spec {row['specificity_mean']:.3f}"
        )

    # Save results
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    results_df = pd.DataFrame(results)
    results_df.to_csv(OUTPUT_PATH, index=False)

    print(f"\nCSV saved successfully:\n{OUTPUT_PATH}")
    print("\nSaved CSV preview:")
    print(results_df.to_string(index=False))


if __name__ == "__main__":
    main()
