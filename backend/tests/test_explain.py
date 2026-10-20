import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.models.explain import forest_contributions


def test_contributions_sum_to_the_forest_probability():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(120, 5))
    y = (X[:, 0] + 0.3 * X[:, 2] + rng.normal(scale=0.5, size=120) > 0).astype(int)
    model = RandomForestClassifier(n_estimators=50, min_samples_leaf=2, class_weight="balanced", random_state=0).fit(X, y)
    for row in X[:10]:
        baseline, contrib = forest_contributions(model, row)
        assert abs(baseline + contrib.sum() - model.predict_proba([row])[0][1]) < 1e-9
    # the informative feature carries more weight than a noise feature
    mean_abs = np.mean([np.abs(forest_contributions(model, r)[1]) for r in X], axis=0)
    assert mean_abs[0] > mean_abs[4]


def test_non_forest_models_return_none():
    assert forest_contributions(object(), [1.0, 2.0]) is None
