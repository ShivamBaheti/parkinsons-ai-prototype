
"""Train and save the voice screening model and its metadata.

Uses the existing evaluation function from train_voice.py.
Evaluation uses repeated person-level stratified group cross-validation.
"""

import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.features.voice_features import FEATURE_NAMES
from train_voice import CSV, evaluate, models


MODEL_DIR = PROJECT_ROOT / "backend" / "models"
MODEL_PATH = MODEL_DIR / "voice_model.pkl"
METADATA_PATH = MODEL_DIR / "voice_model.json"


def main():
    import joblib

    if not CSV.exists():
        raise FileNotFoundError(f"Voice dataset not found: {CSV}")

    df = pd.read_csv(CSV)

    # Use sustained-vowel recordings, matching train_voice.py.
    if "task" in df.columns:
        df = df[df["task"] == "VA"].copy()

    required_columns = (
        FEATURE_NAMES + ["group", "subject"]
    )
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns in voice dataset: {missing}"
        )

    # This model is trained to distinguish PD from elderly healthy controls.
    df = df[df["group"].isin(["pd", "elderly_hc"])].copy()

    if df.empty:
        raise ValueError(
            "No PD or elderly healthy-control recordings were found."
        )

    # Ensure model inputs are numeric and usable.
    for col in FEATURE_NAMES:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=FEATURE_NAMES + ["group", "subject"])

    if df.empty:
        raise ValueError("No complete voice-feature rows remain after cleaning.")

    X = df[FEATURE_NAMES].to_numpy()
    y = (df["group"] == "pd").astype(int).to_numpy()
    groups = df["subject"].to_numpy()

    if len(set(y)) < 2:
        raise ValueError("Training requires both PD and healthy-control classes.")

    print(f"Subjects: {df['subject'].nunique()}")
    print(f"Recordings: {len(df)}")
    print(f"Features: {len(FEATURE_NAMES)}")

    # Evaluate with the existing person-level cross-validation function.
    # evaluate() returns a dictionary, not a tuple.
    evaluation = evaluate(
        models()["logistic_regression"],
        X,
        y,
        groups,
    )

    if not isinstance(evaluation, dict):
        raise TypeError(
            "Expected evaluate() to return a dictionary. "
            f"Received {type(evaluation).__name__}."
        )

    print("\nCross-validation results:")
    for metric, value in evaluation.items():
        print(f"  {metric}: {value:.4f}")

    # Fit the final pipeline on all available rows for saving.
    # StandardScaler remains inside the pipeline.
    final_model = models()["logistic_regression"]
    final_model.fit(X, y)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, MODEL_PATH)

    metadata = {
        "model_type": "LogisticRegression",
        "task": "Voice-based PD vs elderly healthy-control classification",
        "positive_class": "pd",
        "negative_class": "elderly_hc",
        "features": list(FEATURE_NAMES),
        "n_subjects": int(df["subject"].nunique()),
        "n_recordings": int(len(df)),
        "evaluation_method": (
            "Repeated person-level StratifiedGroupKFold "
            "with 5 folds per repeat"
        ),
        "cross_validation_metrics": {
            key: float(value)
            for key, value in evaluation.items()
        },
        "reliable": False,
        "limitations": [
            "Prototype only; not a medical diagnostic tool.",
            "Small dataset; independent external validation is needed.",
            "Recording conditions may influence voice features.",
            "Cross-validation results do not establish clinical validity.",
        ],
    }

    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print("\nSaved model:")
    print(MODEL_PATH)
    print("\nSaved metadata:")
    print(METADATA_PATH)


if __name__ == "__main__":
    main()
