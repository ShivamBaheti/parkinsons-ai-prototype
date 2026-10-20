
"""Export existing drawing evaluation results to CSV."""

from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ml" / "results" / "drawing_evaluation.txt"
OUTPUT = ROOT / "ml" / "results" / "drawing_model_comparison.csv"

if not SOURCE.exists():
    raise FileNotFoundError(f"Evaluation report not found: {SOURCE}")

text = SOURCE.read_text(encoding="utf-8", errors="replace")

# Match model summary lines from the existing evaluation report.
pattern = re.compile(
    r"^\s*(logistic_regression|random_forest|svm_rbf)\s+"
    r"AUC\s+([0-9.]+)\s*\+/-\s*([0-9.]+)\s*\|\s*"
    r"sensitivity\s+([0-9.]+)\s*\+/-\s*([0-9.]+)\s*\|\s*"
    r"specificity\s+([0-9.]+)\s*\+/-\s*([0-9.]+)",
    re.MULTILINE | re.IGNORECASE,
)

rows = []

for match in pattern.finditer(text):
    model, auc, auc_sd, sens, sens_sd, spec, spec_sd = match.groups()
    rows.append({
        "model": model,
        "roc_auc_mean": float(auc),
        "roc_auc_sd": float(auc_sd),
        "sensitivity_mean": float(sens),
        "sensitivity_sd": float(sens_sd),
        "specificity_mean": float(spec),
        "specificity_sd": float(spec_sd),
        "source": "existing drawing_evaluation.txt",
    })

if not rows:
    print("Could not match the report format automatically.")
    print("Please share the complete drawing_evaluation.txt contents.")
else:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(f"Exported {len(rows)} model rows to:\n{OUTPUT}")
    print(pd.DataFrame(rows).to_string(index=False))
