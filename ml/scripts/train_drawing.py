"""Evaluate drawing models on the UCI spiral dataset (id 395). Evaluation only: saves no model.

Usage: python train_drawing.py <dataset_dir>

Design decisions (leakage and confound control):
  * Only hw_dataset (15 controls, 25 PD) is used for training/evaluation. new_dataset contains
    PD subjects only and was recorded differently, so mixing it in would let a model learn the
    recording protocol instead of the disease. It is used only for the checks at the end.
  * Static Spiral Test (test 0) only; x, y and time only (a mouse/finger gives no pressure).
  * Pen-up samples (pressure == 0) are dropped: the web canvas only records while drawing.
  * One file = one subject = one row, so stratified K-fold is automatically subject-level.
  * Scaling lives inside the sklearn Pipeline, so it is fitted on training folds only.
    No feature selection and no hyper-parameter tuning is done: fixed, default-ish settings.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.features.drawing_features import FEATURE_NAMES, Frame, extract_features  # noqa: E402

warnings.filterwarnings("ignore")
COLS = ["x", "y", "z", "pressure", "grip_angle", "t", "test"]
FRAME = Frame(cx=200.0, cy=200.0, radius=200.0)  # approximate guide-spiral frame, dataset units
SEED = 42


def features_for(path: Path) -> dict | None:
    d = pd.read_csv(path, sep=";", header=None, names=COLS)
    d = d[(d.test == 0) & (d.pressure > 0)]
    if len(d) < 50:
        return None
    return extract_features(d.x, d.y, d.t / 1000.0, FRAME)  # timestamps are milliseconds


def build_table(root: Path, rel: str, label: int, group: str) -> pd.DataFrame:
    rows = []
    for f in sorted((root / rel).glob("*.txt")):
        feats = features_for(f)
        if feats is None:
            print(f"  skipped {f.name}: no usable static-spiral data")
            continue
        rows.append({"subject": f.stem, "group": group, "label": label, **feats})
    return pd.DataFrame(rows)


def models():
    return {
        "logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=1000)),
        "random_forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced", random_state=SEED, n_jobs=-1),
        "svm_rbf": make_pipeline(StandardScaler(), SVC(class_weight="balanced", probability=True, random_state=SEED)),
    }


def score(model, X, y, n_repeats=20):
    """Repeated stratified 5-fold; metrics from pooled out-of-fold predictions per repeat."""
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=n_repeats, random_state=SEED)
    per_repeat, cms = [], []
    proba = np.zeros((n_repeats, len(y)))
    for i, (tr, te) in enumerate(cv.split(X, y)):
        r = i // 5
        m = __import__("sklearn.base", fromlist=["clone"]).clone(model).fit(X[tr], y[tr])
        proba[r, te] = m.predict_proba(X[te])[:, 1]
    for r in range(n_repeats):
        pred = (proba[r] >= 0.5).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
        per_repeat.append(dict(auc=roc_auc_score(y, proba[r]), sens=tp / (tp + fn), spec=tn / (tn + fp)))
        cms.append([[tn, fp], [fn, tp]])
    out = pd.DataFrame(per_repeat)
    out["bal_acc"] = (out.sens + out.spec) / 2
    return out, np.mean(cms, axis=0)


def main(root: Path) -> None:
    print("Extracting features...")
    ctrl = build_table(root, "hw_dataset/control", 0, "control")
    pd_hw = build_table(root, "hw_dataset/parkinson", 1, "pd_hw")
    pd_new = build_table(root, "new_dataset/parkinson", 1, "pd_new")
    train = pd.concat([ctrl, pd_hw], ignore_index=True)
    assert train.subject.is_unique, "each subject must appear once (subject-level split)"
    out = Path(__file__).resolve().parents[1] / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    pd.concat([train, pd_new]).to_csv(out / "drawing_features.csv", index=False)

    X, y = train[FEATURE_NAMES].to_numpy(), train.label.to_numpy()
    print(f"\nTraining set: {len(train)} subjects  (controls={int((y==0).sum())}, PD={int((y==1).sum())})")
    print(f"External PD-only set (new_dataset): {len(pd_new)} subjects\n")

    print("== Repeated stratified 5-fold CV x20 (mean +/- sd across repeats), threshold 0.5 ==")
    results, best = {}, None
    for name, model in models().items():
        res, cm = score(model, X, y)
        results[name] = res
        m, s = res.mean(), res.std()
        print(f"{name:20s} AUC {m.auc:.3f}+/-{s.auc:.3f} | sensitivity {m.sens:.3f}+/-{s.sens:.3f} | "
              f"specificity {m.spec:.3f}+/-{s.spec:.3f} | balanced acc {m.bal_acc:.3f}")
        print(f"{'':20s} mean confusion matrix [[TN FP],[FN TP]] = {np.round(cm, 1).tolist()}")
    best = max(results, key=lambda k: results[k].auc.mean())
    print(f"\nHighest mean AUC: {best}  (chosen among 3 models on the same CV: mildly optimistic)")

    print("\n== Label-permutation check for the best model (is AUC above chance?) ==")
    rng = np.random.default_rng(SEED)
    true_auc = results[best].auc.mean()
    null = [score(models()[best], X, rng.permutation(y), n_repeats=1)[0].auc.iloc[0] for _ in range(100)]
    print(f"observed AUC {true_auc:.3f}; permuted-label AUC mean {np.mean(null):.3f}, "
          f"95th percentile {np.percentile(null, 95):.3f}; p ~ {(np.sum(np.array(null) >= true_auc) + 1) / 101:.3f}")

    print("\n== Confound check: can the features tell the two PD recording protocols apart? ==")
    both = pd.concat([pd_hw, pd_new], ignore_index=True)
    Xb, yb = both[FEATURE_NAMES].to_numpy(), (both.group == "pd_new").astype(int).to_numpy()
    res, _ = score(models()["logistic_regression"], Xb, yb, n_repeats=10)
    print(f"hw-PD vs new-PD (same disease, different protocol): AUC {res.auc.mean():.3f}  (0.5 = indistinguishable)")

    print("\n== External PD-only check (train on all hw subjects, predict new_dataset PD) ==")
    final = models()[best].fit(X, y)
    p = final.predict_proba(pd_new[FEATURE_NAMES].to_numpy())[:, 1]
    print(f"{best}: {int((p >= 0.5).sum())}/{len(p)} new-dataset PD subjects flagged "
          f"(sensitivity {np.mean(p >= 0.5):.3f}; no controls available, so specificity cannot be measured)")

    print("\n== Univariate AUC per feature (control vs PD, hw only; no selection performed) ==")
    uni = {f: roc_auc_score(y, train[f]) for f in FEATURE_NAMES}
    for f, a in sorted(uni.items(), key=lambda kv: -abs(kv[1] - .5)):
        print(f"  {f:22s}{a:.3f}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
