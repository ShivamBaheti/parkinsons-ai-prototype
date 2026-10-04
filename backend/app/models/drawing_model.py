"""Loads the trained drawing model (backend/models/drawing_model.pkl) and predicts from a trajectory."""
import json
from functools import lru_cache

from app.config import settings
from app.features.drawing_features import FEATURE_NAMES, Frame, extract_features

MODEL_PATH = settings.model_dir / "drawing_model.pkl"
META_PATH = settings.model_dir / "drawing_model.json"
THRESHOLD = 0.5
GUIDE_SIZE = 600.0  # the canvas is drawn at 600 px; the guide spiral has outer radius 250 px
GUIDE_RADIUS = 250.0


@lru_cache(maxsize=1)
def load_drawing_model():
    if not MODEL_PATH.exists():
        return None
    import joblib

    return joblib.load(MODEL_PATH)


def load_drawing_metadata() -> dict | None:
    try:
        return json.loads(META_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def predict_drawing(model, xs, ys, ts_ms, canvas_size: float, feature_names: list[str] | None = None) -> tuple[float, dict[str, float]]:
    """Return (probability of the elevated-signal class, extracted features). Raises ValueError if too short."""
    scale = canvas_size / GUIDE_SIZE
    frame = Frame(cx=canvas_size / 2, cy=canvas_size / 2, radius=GUIDE_RADIUS * scale)
    feats = extract_features(xs, ys, [t / 1000.0 for t in ts_ms], frame)
    proba = float(model.predict_proba([[feats[n] for n in (feature_names or FEATURE_NAMES)]])[0][1])
    return proba, feats
