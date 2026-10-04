"""Loads the trained voice model (backend/models/voice_model.pkl) and predicts from a recording."""
import json
from functools import lru_cache

import numpy as np

from app.config import settings
from app.features.voice_features import FEATURE_NAMES, extract_features

MODEL_PATH = settings.model_dir / "voice_model.pkl"
META_PATH = settings.model_dir / "voice_model.json"
THRESHOLD = 0.5


@lru_cache(maxsize=1)
def load_voice_model():
    if not MODEL_PATH.exists():
        return None
    import joblib  # imported lazily: only needed once a model exists

    return joblib.load(MODEL_PATH)


def load_voice_metadata() -> dict | None:
    try:
        return json.loads(META_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def predict_voice(model, signal: np.ndarray, sample_rate: int, feature_names: list[str] | None = None):
    """Return (probability of the elevated-signal class, features). Raises ValueError if the voice can't be analysed."""
    feats = extract_features(signal, sample_rate)
    proba = float(model.predict_proba([[feats[n] for n in (feature_names or FEATURE_NAMES)]])[0][1])
    return proba, feats
