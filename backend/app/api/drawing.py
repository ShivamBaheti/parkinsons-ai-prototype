import logging
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.drawing_model import load_drawing_model
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

    if load_drawing_model() is None:
        logger.warning("Drawing analysis requested but no trained model is installed.")
        return api_error(
            503,
            "model_unavailable",
            "The drawing is valid, but the drawing model has not been trained yet, so no result can be produced.",
            drawing={"n_points": info.n_points, "duration_s": info.duration_s},
        )

    return api_error(501, "not_implemented", "Drawing prediction is not implemented yet.")
