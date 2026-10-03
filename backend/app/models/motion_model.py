"""Loads the trained motion model from backend/models/motion_model.pkl (none bundled yet)."""
from functools import lru_cache

from app.config import settings

MODEL_PATH = settings.model_dir / "motion_model.pkl"


@lru_cache(maxsize=1)
def load_motion_model():
    if not MODEL_PATH.exists():
        return None
    import joblib

    return joblib.load(MODEL_PATH)
