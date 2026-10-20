
"""Generate report-ready graphs from Parkinson's project CSV results."""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "ml" / "results"

DRAWING = RESULTS / "drawing_model_comparison.csv"
ABLATION = RESULTS / "drawing_ablation.csv"
VOICE = RESULTS / "voice_comparison.csv"


def load_csv(path):
    if not path.exists():
        print(f"Skipping missing file: {path.name}")
        return None
    return pd.read_csv(path)


def save_auc_plot(
    df,
    label_col,
    auc_col,
    title,
    xlabel,
    output_name,
    sd_col=None,
    rotate=0,
):
    if df is None or df.empty:
        return

    df = df.copy()
    df[auc_col] = pd.to_numeric(df[auc_col], errors="coerce")
    df = df.dropna(subset=[auc_col])

    if df.empty:
        print(f"No valid AUC values for {output_name}")
        return

    fig, ax = plt.subplots(figsize=(10, 5.5))

    errors = None
    if sd_col and sd_col in df.columns:
        errors = pd.to_numeric(df[sd_col], errors="coerce")

    bars = ax.bar(
        df[label_col].astype(str),
        df[auc_col],
        yerr=errors,
        capsize=4 if errors is not None else 0,
    )

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("ROC-AUC")
    ax.set_ylim(0, 1.05)
    ax.axhline(
        0.5,
        linestyle="--",
        linewidth=1,
        label="Chance-level AUC",
    )
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", labelrotation=rotate)
    ax.legend()

    for bar, value in zip(bars, df[auc_col]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.025,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.tight_layout()
    output = RESULTS / output_name
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output}")


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)

    # 1. Drawing model comparison
    drawing = load_csv(DRAWING)
    if drawing is not None:
        save_auc_plot(
            drawing,
            label_col="model",
            auc_col="roc_auc_mean",
            sd_col="roc_auc_sd",
            title="Drawing Model Comparison",
            xlabel="Model",
            output_name="drawing_model_comparison.png",
            rotate=15,
        )

    # 2. Drawing feature ablation
    ablation = load_csv(ABLATION)
    if ablation is not None:
        save_auc_plot(
            ablation,
            label_col="feature_set",
            auc_col="roc_auc_mean",
            title="Effect of Drawing Feature Ablation",
            xlabel="Feature set",
            output_name="drawing_ablation.png",
            rotate=15,
        )

    # 3. Voice model comparison, separated by scenario
    voice = load_csv(VOICE)
    if voice is not None and not voice.empty:
        required = {
            "scenario",
            "model",
            "roc_auc_mean",
            "roc_auc_sd",
        }
        missing = required - set(voice.columns)

        if missing:
            print(f"Voice CSV missing columns: {sorted(missing)}")
        else:
            for scenario, group in voice.groupby("scenario", sort=False):
                plot_data = group.copy()
                plot_data["model_label"] = plot_data["model"]

                filename = (
                    "voice_"
                    + "".join(
                        c.lower() if c.isalnum() else "_"
                        for c in scenario
                    ).strip("_")
                    + ".png"
                )

                save_auc_plot(
                    plot_data,
                    label_col="model_label",
                    auc_col="roc_auc_mean",
                    sd_col="roc_auc_sd",
                    title=f"Voice Model Evaluation: {scenario}",
                    xlabel="Model",
                    output_name=filename,
                )

    print("\nGraph generation complete.")


if __name__ == "__main__":
    main()
