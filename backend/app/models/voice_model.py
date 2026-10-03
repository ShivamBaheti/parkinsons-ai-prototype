"""Loads the trained voice model from backend/models/voice_model.pkl.

No model is bundled until one is trained from real data (ml/scripts/train_voice.py).
Until then load_voice_model() returns None and the API reports 'model_unavailable'.
"""
from functools import lru_cache

from app.config import settings

MODEL_PATH = settings.model_dir / "voice_model.pkl"


@lru_cache(maxsize=1)
def load_voice_model():
    if not MODEL_PATH.exists():
        return None
    import joblib  # imported lazily: only needed once a model exists

    return joblib.load(MODEL_PATH)
