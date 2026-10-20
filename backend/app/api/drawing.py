import logging
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.explain import forest_contributions
from app.models.drawing_model import THRESHOLD, load_drawing_metadata, load_drawing_model, predict_drawing
from app.utils.errors import api_error
from app.utils.validation import ValidationError, validate_drawing

router = APIRouter(tags=["drawing"])
logger = logging.getLogger("parkinsons_api.drawing")


class Point(BaseModel):
    x: float = Field(allow_inf_nan=False)
    y: float = Field(allow_inf_nan=False)
    t: float = Field(allow_inf_nan=False, description="Milliseconds since the first touch")
    stroke: int = Field(default=0, ge=0)
    pressure: float | None = Field(default=None, allow_inf_nan=False)


class DrawingRequest(BaseModel):
    points: list[Point] = Field(max_length=50_000)
    canvas_size: float = Field(gt=0, allow_inf_nan=False, description="Square canvas side in pixels")
    input_type: Literal["mouse", "touch", "pen"] | None = None


@router.post("/drawing/analyze")
def analyze_drawing(req: DrawingRequest):
    try:
        info = validate_drawing(
            [p.x for p in req.points],
            [p.y for p in req.points],
            [p.t for p in req.points],
            [p.stroke for p in req.points],
            req.canvas_size,
        )
    except ValidationError as err:
        return api_error(err.status_code, err.code, err.message)

    model = load_drawing_model()
    if model is None:
        logger.warning("Drawing analysis requested but no trained model is installed.")
        return api_error(
            503,
            "model_unavailable",
            "The drawing is valid, but the drawing model has not been trained yet, so no result can be produced.",
            drawing={"n_points": info.n_points, "duration_s": info.duration_s},
        )

    meta = load_drawing_metadata() or {}
    try:
        score, feats = predict_drawing(
            model, [p.x for p in req.points], [p.y for p in req.points], [p.t for p in req.points],
            req.canvas_size, meta.get("features"),
        )
    except ValueError:
        return api_error(422, "drawing_too_short", "The drawing is too short to analyse. Please trace the whole spiral.")

    names = meta.get("features") or list(feats)
    explained = forest_contributions(model, [feats[n] for n in names])
    contributions = baseline = None
    if explained is not None:
        baseline = round(explained[0] * 100, 1)
        # Points of the 0-100 score each measurement added (+) or removed (-). They sum to score - baseline.
        contributions = {n: round(float(c) * 100, 1) for n, c in zip(names, explained[1])}

    importance = {d["feature"]: d["importance"] for d in meta.get("feature_importance", [])}
    top = sorted(importance, key=importance.get, reverse=True)[:3]
    return {
        "modality": "drawing",
        "score": round(score, 3),
        "label": "elevated_screening_signal" if score >= THRESHOLD else "lower_screening_signal",
        "validated_for_this_input": False,
        "input_type": req.input_type,
        "features": {k: round(v, 4) for k, v in feats.items()},
        "baseline": baseline,
        "contributions": contributions,
        "top_model_features": top,  # global model importance, not an explanation of this one drawing
        "note": (
            "The model was trained on stylus-on-tablet spirals from 40 people. Mouse and touch drawings "
            "have not been validated, so treat this score as a demonstration only."
        ),
    }
