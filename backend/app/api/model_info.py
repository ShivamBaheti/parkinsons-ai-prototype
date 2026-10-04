import json

from fastapi import APIRouter

from app.config import settings
from app.models.fusion_model import METHOD, MODALITIES, THRESHOLD

router = APIRouter(tags=["model-info"])


def _modality_info(name: str) -> dict:
    """Report whether a trained model is installed. Metrics are shown only if a metadata file written by training exists."""
    model_path = settings.model_dir / f"{name}_model.pkl"
    meta_path = settings.model_dir / f"{name}_model.json"
    info: dict = {"available": model_path.exists(), "metadata": None}
    if meta_path.exists():
        try:
            info["metadata"] = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            info["metadata"] = None
    return info


@router.get("/model-info")
def model_info():
    return {
        "modalities": {name: _modality_info(name) for name in MODALITIES},
        "fusion": {
            "method": METHOD,
            "validated": False,
            "threshold": THRESHOLD,
            "description": "Equal-weight mean of the available modality probabilities (prototype; no paired data to validate a fusion model).",
        },
    }
