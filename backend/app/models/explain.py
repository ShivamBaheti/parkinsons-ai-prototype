"""Per-prediction feature contributions for a random forest (the "tree interpreter" decomposition).

For every tree, walk the path the sample takes. At each split, the change in the tree's
class-1 probability between the parent and the chosen child is credited to the feature used
at that split. Averaged over trees:

    probability = baseline + sum(contributions)

so the contributions are an exact breakdown of this one score, in probability units.
They describe how the MODEL used the measurements. They are not a clinical explanation.
"""
import numpy as np


def forest_contributions(model, row) -> tuple[float, np.ndarray] | None:
    """Return (baseline, contributions per feature) for one row, or None if the model is not a forest."""
    trees = getattr(model, "estimators_", None)
    classes = getattr(model, "classes_", None)
    if not trees or classes is None or 1 not in list(classes):
        return None
    cls = list(classes).index(1)
    x = np.asarray(row, dtype=float)
    contrib = np.zeros(len(x))
    baseline = 0.0
    for est in trees:
        t = est.tree_
        counts = t.value[:, 0, :]
        p1 = counts[:, cls] / counts.sum(axis=1)
        node = 0
        baseline += p1[0]
        while t.children_left[node] != -1:
            f = t.feature[node]
            child = t.children_left[node] if x[f] <= t.threshold[node] else t.children_right[node]
            contrib[f] += p1[child] - p1[node]
            node = child
    n = len(trees)
    return baseline / n, contrib / n
