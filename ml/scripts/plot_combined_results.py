
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "ml" / "results"

drawing = pd.read_csv(RESULTS / "drawing_model_comparison.csv")
voice = pd.read_csv(RESULTS / "voice_comparison.csv")
ablation = pd.read_csv(RESULTS / "drawing_ablation.csv")

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Drawing model comparison
axes[0].bar(
    drawing["model"],
    drawing["roc_auc_mean"],
    yerr=drawing["roc_auc_sd"],
    capsize=4,
)
axes[0].axhline(0.5, linestyle="--", linewidth=1)
axes[0].set_title("Drawing Model Comparison")
axes[0].set_ylabel("ROC-AUC")
axes[0].set_ylim(0, 1.05)
axes[0].tick_params(axis="x", rotation=20)

# Drawing feature ablation
axes[1].bar(
    ablation["feature_set"],
    ablation["roc_auc_mean"],
)
axes[1].axhline(0.5, linestyle="--", linewidth=1)
axes[1].set_title("Drawing Feature Ablation")
axes[1].set_ylabel("ROC-AUC")
axes[1].set_ylim(0, 1.05)
axes[1].tick_params(axis="x", rotation=25)

for ax in axes:
    ax.grid(axis="y", alpha=0.25)

fig.tight_layout()
output = RESULTS / "combined_drawing_results.png"
fig.savefig(output, dpi=300, bbox_inches="tight")
plt.close(fig)

# Separate, clearly labelled voice summary
voice_summary = (
    voice.groupby("scenario", sort=False)
    .apply(lambda g: g[["model", "roc_auc_mean"]].to_dict("records"))
)

print(f"Combined drawing figure saved to: {output}")
print("\nVoice AUC summary:")
for scenario, models in voice_summary.items():
    print(scenario, models)
