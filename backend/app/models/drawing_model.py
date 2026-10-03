"""Loads the trained drawing model from backend/models/drawing_model.pkl (none bundled yet)."""
from functools import lru_cache

from app.config import settings

MODEL_PATH = settings.model_dir / "drawing_model.pkl"


@lru_cache(maxsize=1)
def load_drawing_model():
    if not MODEL_PATH.exists():
        return None
    import joblib

    return joblib.load(MODEL_PATH)
